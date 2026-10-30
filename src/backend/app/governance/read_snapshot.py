"""Bounded snapshot candidates with an independent full read on every request.

A previously validated path/byte map is only a candidate: every path and byte
must equal a fresh complete safe read. Any difference retries two full reads.
Unreliable timestamps cannot validate stale bytes. Writers use stable().
"""
from collections import OrderedDict
from threading import RLock
from sys import getsizeof
from pathlib import Path
import os

from app.governance import snapshot

MAX_VERSIONS = 2
# Reserve 8 MiB of the existing 64 MiB read-cache budget for pure parser memo.
MAX_BYTES = 56 * 1024 * 1024
_lock = RLock()
_versions = OrderedDict()


def clear():
    with _lock:
        _versions.clear()



def read_workers(*, cold=False):
    """Avoid oversubscribing CPU-constrained deployments; unknown limits use serial."""
    try:
        capacity = len(os.sched_getaffinity(0))
        quota, period = Path('/sys/fs/cgroup/cpu.max').read_text().split()
        period = int(period)
        if period <= 0:
            return 1
        if quota != 'max':
            capacity = min(capacity, int(quota) // period)
        # Two readers avoid the measured GIL/syscall scheduling overhead of
        # four while retaining I/O overlap. Leave headroom for live services.
        if cold and capacity >= 8:
            return 4
        return 2 if capacity >= 4 else 1
    except (AttributeError, OSError, ValueError):
        # cgroup v1, non-Linux and unreadable capacity retain the proven reader.
        return 1


def stable_read(root, namespace, *, enabled=True, retries=3, profile='full', root_fd=None, parallel_cold=False):
    if profile not in ('full', 'summary'): raise ValueError('profile')
    if not enabled:
        return snapshot._stable(root, retries, lambda path: snapshot.read_once(path, profile=profile, root_fd=root_fd))
    key = (str(root), namespace) if profile == 'full' else (str(root), namespace, profile)
    with _lock:
        previous = _versions.get(key)
        if previous is not None:
            _versions.move_to_end(key)
    reuse = previous[0] if previous else {}
    identities = {}
    reads = 0

    def read(path):
        nonlocal reads
        reads += 1
        # Only the first attempt may borrow the privately retained, validated
        # map. It is never returned without a fresh complete path/byte match.
        # Re-enumerating paths here cannot make candidate bytes trustworthy;
        # the independent safe read below supplies all current file evidence.
        identities.clear()
        if reads == 1 and previous is not None:
            return previous[2].files
        options = {'profile': profile} if profile != 'full' else {}
        if root_fd is not None:
            options['root_fd'] = root_fd
        if profile == 'summary' and reuse:
            options['byte_candidates'] = reuse
        # Object-session cold reads may schedule both independent full passes.
        # Each pass finishes before the next begins; retries stay serial.
        cold = parallel_cold and previous is None and reads <= 2
        parallel = profile == 'summary' or (reads == 2 and len(reuse) >= 256)
        return snapshot.read_once(path, identities=identities,
                                  workers=read_workers(cold=True) if cold else read_workers() if parallel else 1, **options)

    result = snapshot._stable(root, retries, read,
                              known_snapshot=previous[2] if previous else None)
    if (previous and result.revision == previous[2].revision and
            len(identities) == len(previous[0]) and
            all(identities.get(name) == row[0] for name, row in previous[0].items())):
        # The completed full-byte check and final metadata prove this cache
        # record is unchanged. Keep its already-accounted containers instead
        # of rebuilding thousands of tuples and recounting them every request.
        # A concurrent replacement is left intact; either version is only a hint.
        with _lock:
            if _versions.get(key) is previous:
                _versions.move_to_end(key)
        return result
    records = {name: (identities[name], body) for name, body in result.files.items()}
    # Conservatively count retained Python containers and metadata as well as
    # payload; shared integer/path objects are deliberately counted per entry.
    size = getsizeof(records) + getsizeof(result.files) + sum(
        getsizeof(name) + getsizeof(row) + getsizeof(row[0]) +
        sum(getsizeof(value) for value in row[0]) + getsizeof(row[1])
        for name, row in records.items())
    with _lock:
        # Never retain a previous version for this project/binding on replacement.
        _versions.pop(key, None)
        if size <= MAX_BYTES:
            while _versions and (len(_versions) >= MAX_VERSIONS or
                                    sum(row[1] for row in _versions.values()) + size > MAX_BYTES):
                _versions.popitem(last=False)
            _versions[key] = (records, size, snapshot.Snapshot(dict(result.files), result.revision))
    return result


def stable_alias_read(root, other_root, namespace, *, parallel_cold=False):
    """Read aliases once, anchored to a directory descriptor; None for replicas.

    Device/inode equality only identifies a directory, never validates content.
    Every accepted file byte is still freshly read. Both names must resolve to
    the pinned directory after reading; replacement or a link fails closed.
    No descriptor or alias result is retained across calls.
    """
    from contextlib import ExitStack
    import stat
    from app.chat.service import ChatError
    try:
        with ExitStack() as resources:
            descriptors = []
            for path in (root, other_root):
                fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
                resources.callback(os.close, fd)
                descriptors.append(fd)
            identities = [(os.fstat(fd).st_dev, os.fstat(fd).st_ino) for fd in descriptors]
            if identities[0] != identities[1]:
                return None
            result = stable_read(root, namespace, root_fd=descriptors[0], parallel_cold=parallel_cold)
            for path in (root, other_root):
                current = os.stat(path, follow_symlinks=False)
                if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != identities[0]:
                    raise ChatError(2603, '项目目录已变化，请重新读取完整快照', 503, kind='source_changing')
            return result
    except OSError:
        raise ChatError(2603, '项目数据暂时无法读取，请稍后重试', 503, kind='source_unavailable') from None
