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



def read_workers():
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
        return 2 if capacity >= 4 else 1
    except (AttributeError, OSError, ValueError):
        # cgroup v1, non-Linux and unreadable capacity retain the proven reader.
        return 1


def stable_read(root, namespace, *, enabled=True, retries=3):
    if not enabled:
        return snapshot.stable(root, retries)
    key = (str(root), namespace)
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
        return snapshot.read_once(path, identities=identities,
                                  workers=read_workers() if reads == 2 and len(reuse) >= 256 else 1)

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
