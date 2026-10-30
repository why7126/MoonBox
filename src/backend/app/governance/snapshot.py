"""Bounded stable worktree snapshots. Links and nonregular files fail closed."""
from contextlib import contextmanager
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import yaml
from collections import OrderedDict
from threading import RLock, Event
from concurrent.futures import ThreadPoolExecutor, wait
from app.chat.service import ChatError

LIMIT_FILE = 1024 * 1024
LIMIT_TOTAL = 32 * 1024 * 1024
LIMIT_COUNT = 10000
ROOTS = ('issues', 'iterations', 'openspec', 'docs', 'rules')
EXTENSIONS = {'.md', '.yaml', '.yml', '.html'}
SUFFIXES = tuple(EXTENSIONS)


# Only SafeLoader variants: libyaml accelerates parsing without enabling objects.
def safe_load(value):
    return yaml.load(value, Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))


_validation_lock = RLock()
_validated = OrderedDict()
CACHE_ENTRIES = 4
CACHE_BYTES = 128 * 1024 * 1024
_tree_lock = RLock()
_trees = OrderedDict()


def _validate_revision(files, revision):
    with _validation_lock:
        if revision in _validated:
            _validated.move_to_end(revision)
            return
    registries = validate(files)
    with _validation_lock:
        _validated[revision] = True
        while len(_validated) > 32:
            _validated.popitem(last=False)
    return registries


@dataclass(frozen=True)
class Snapshot:
    files: dict[str, bytes]
    revision: str
    # Request-local validation result. Never retained in the cross-request cache.
    registries: dict | None = field(default=None, compare=False, repr=False)


def digest(files):
    manifest = [(name, 'regular', hashlib.sha256(body).hexdigest()) for name,body in sorted(files.items())]
    return hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()


def file_identity(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns,
            info.st_ctime_ns, info.st_mode, info.st_nlink, info.st_uid, info.st_gid)


def read_body(fd, size):
    """Read the bounded file directly; handle short reads and concurrent growth."""
    body = os.read(fd, min(size + 1, LIMIT_FILE + 1))
    if len(body) == size:
        # A complete regular-file read normally ends here. Keep the EOF probe
        # (and growth detection) but avoid building/joining a list per file.
        tail = os.read(fd, 1)
        if not tail:
            return body
        body += tail
    chunks = [body]
    total = len(body)
    while body and total <= LIMIT_FILE:
        # The common EOF probe needs one byte, not a 1 MiB temporary buffer.
        # If the file grew, continue with the remaining bounded allowance.
        remaining = size + 1 - total if total <= size else LIMIT_FILE + 1 - total
        body = os.read(fd, min(remaining, LIMIT_FILE + 1 - total))
        chunks.append(body)
        total += len(body)
    return b''.join(chunks)


def read_once(root, *, reuse=None, identities=None, workers=1, profile='full', byte_candidates=None, root_fd=None):
    if profile not in ('full', 'summary'): raise ValueError('profile')
    if workers not in (1, 2, 4): raise ValueError('workers')
    files = {}; total = 0
    lock = RLock()
    aborted = Event()
    pool = ThreadPoolExecutor(max_workers=workers) if workers > 1 else None
    def add(relative, body, identity=None):
        nonlocal total
        with lock:
            if aborted.is_set(): return
            total += len(body)
            if len(body)>LIMIT_FILE or total>LIMIT_TOTAL or len(files)>=LIMIT_COUNT:
                aborted.set()
                raise ValueError('size')
            files[relative] = body
            if identities is not None and identity is not None:
                identities[relative] = identity
    def descend(fd, name, relative, depth):
        if aborted.is_set(): return
        try:
            child = os.open(name, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW, dir_fd=fd)
            try: walk(child, relative, depth)
            finally: os.close(child)
        except BaseException:
            aborted.set()
            raise
    def walk(fd, prefix, depth=0):
        nonlocal total
        if depth > 24: raise ValueError('depth')
        with os.scandir(fd) as stream:
            entries = list(stream)
        pending = []
        try:
            for entry in entries:
                if aborted.is_set(): break
                name = entry.name
                change_control = (name == '.openspec.yaml' and
                                  len(prefix.split('/')) == 3 and
                                  prefix.startswith('openspec/changes/'))
                if (name.startswith('.') and not change_control) or name in ('node_modules','__pycache__'):
                    continue
                relative = f'{prefix}/{name}' if prefix else name
                # Summary reads have an explicit server-owned dependency scope.
                # Evidence is checked by the full reader on demand, never inferred
                # from the absence of these files in a summary materialization.
                if profile == 'summary' and prefix.startswith(('openspec/changes/', 'openspec/archive/')) and len(prefix.split('/')) == 3 and name == 'evidence':
                    continue
                if entry.is_symlink(): raise ValueError('link')
                if entry.is_dir(follow_symlinks=False):
                    if pool is not None and depth == 1:
                        pending.append(pool.submit(descend, fd, name, relative, depth+1))
                    else:
                        descend(fd, name, relative, depth+1)
                elif name.endswith(SUFFIXES):
                    cached = reuse.get(relative) if reuse is not None else None
                    if cached is not None and entry.is_file(follow_symlinks=False):
                        # This first-pass value is only a candidate. The independent
                        # second pass opens every file with NOFOLLOW, verifies both
                        # fstats/type/link count/limits and compares all bytes. A
                        # repeated metadata stat here adds no acceptance evidence.
                        body = cached[1]
                        add(relative, body, cached[0])
                        continue
                    child = os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                    try:
                        before = os.fstat(child)
                        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > LIMIT_FILE: raise ValueError('size')
                        body = read_body(child, before.st_size)
                        after = os.fstat(child)
                        identity = file_identity(after)
                        if file_identity(before) != identity: raise ValueError('changed')
                    finally: os.close(child)
                    # Retain an existing immutable payload only after opening,
                    # reading and validating this file in full. This is not the
                    # first-pass metadata hint above: every fresh byte was read
                    # and compared, including when timestamps are unchanged.
                    candidate = byte_candidates.get(relative) if byte_candidates is not None else None
                    if candidate is not None and body == candidate[1]:
                        body = candidate[1]
                    add(relative, body, identity)
        except BaseException:
            aborted.set()
            raise
        finally:
            # Keep the parent descriptor alive even if enumeration fails.
            if pending: wait(pending)
        for future in pending:
            future.result()
    # An internal caller may pin an already NOFOLLOW-opened directory while
    # checking two authorized names for the same physical tree. Own only a dup.
    fd = os.dup(root_fd) if root_fd is not None else os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for name in ROOTS:
            if profile == 'summary' and name in ('docs', 'rules'): continue
            try: child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            except FileNotFoundError: continue
            try: walk(child,name)
            finally: os.close(child)
    finally:
        os.close(fd)
        if pool is not None: pool.shutdown(wait=True)
        # The mutually recursive closures otherwise keep each request's file
        # and metadata maps alive until cyclic GC. All submitted work has
        # finished, so break their shared cells before returning the snapshot.
        walk = descend = None
    return files


def validate(files):
    registries = {}
    for folder in ('requirements','bugs'):
        value = safe_load(files[f'issues/{folder}/_registry.yaml'].decode())
        if not isinstance(value,dict) or not isinstance(value.get('entries'),list): raise ValueError('registry')
        ids=set()
        for entry in value['entries']:
            if not isinstance(entry,dict) or not isinstance(entry.get('id'),str) or entry['id'] in ids: raise ValueError('entry')
            ids.add(entry['id'])
            path=entry.get('path','')
            if not isinstance(path,str) or not path.startswith(f'issues/{folder}/') or '..' in Path(path).parts: raise ValueError('path')
            # Missing issue directories are stable drift facts (e.g. archived index);
            # the existing parser exposes the missing-document warning.
        registries[folder] = value
    for name,body in files.items():
        content=body.decode('utf-8')
        if name in ('issues/requirements/_registry.yaml', 'issues/bugs/_registry.yaml'):
            continue  # Fully parsed and structurally validated above.
        if name.endswith(('.yaml','.yml')): safe_load(content)
        elif name.endswith('.md') and content.startswith('---\n'):
            parts=content.split('---',2)
            if len(parts)!=3 or not isinstance(safe_load(parts[1]),dict): raise ValueError('frontmatter')
    return registries


def stable(root, retries=3):
    return _stable(root, retries, read_once)


def _stable(root, retries, read, *, known_snapshot=None):
    kind = 'source_changing'
    for _ in range(retries):
        try:
            first = read(root)
            second = read(root)
        except (OSError, ValueError) as exc:
            kind = 'source_changing' if str(exc) == 'changed' or isinstance(exc, FileNotFoundError) else 'source_unavailable'
            continue
        if first != second:
            kind = 'source_changing'
            continue
        # Reuse a digest only after equality of every path and byte, never from
        # metadata or a partial manifest. The independent second read still ran.
        revision = (known_snapshot.revision if known_snapshot is not None and
                    second == known_snapshot.files else digest(second))
        try:
            registries = _validate_revision(second, revision)
        except (ValueError, KeyError, yaml.YAMLError, UnicodeError):
            # Identical complete reads prove a stable invalid input. Do not scan
            # it three more times or expose the parser's path/content in errors.
            raise ChatError(2603, '项目数据格式暂不可解析，请修复后重新加载', 503, kind='source_invalid') from None
        return Snapshot(second, revision, registries)
    message = '项目文件正在变化，请稍后重新加载' if kind == 'source_changing' else '项目数据暂时无法读取，请稍后重试'
    raise ChatError(2603, message, 503, kind=kind)


@contextmanager
def cached_materialize(snapshot, namespace):
    """Bounded read-adapter cache; never used by candidate/writer operations.

    Holds the lock through the parser call so eviction cannot remove a tree in
    use. Authorization and content/fence checks run outside this cache on every
    request. Only immutable input files, never user-specific results, are reused.
    """
    key = (namespace, snapshot.revision)
    size = sum(map(len, snapshot.files.values()))
    with _tree_lock:
        if key not in _trees:
            while _trees and (len(_trees) >= CACHE_ENTRIES or sum(row[2] for row in _trees.values()) + size > CACHE_BYTES):
                _, (directory, _, _) = _trees.popitem(last=False)
                directory.cleanup()
            directory = tempfile.TemporaryDirectory(prefix='moonbox-governance-cache-')
            try:
                root = Path(directory.name).resolve()
                created = {root}
                for relative, body in snapshot.files.items():
                    target = root / relative
                    if target.parent not in created:
                        target.parent.mkdir(parents=True, exist_ok=True)
                        created.add(target.parent)
                    target.write_bytes(body)
                _trees[key] = (directory, root, size)
            except BaseException:
                directory.cleanup()
                raise
        _trees.move_to_end(key)
        yield _trees[key][1]


@contextmanager
def materialize(snapshot):
    # Existing parsers only see a private, complete tree, never a live partial write.
    with tempfile.TemporaryDirectory(prefix='moonbox-governance-read-') as directory:
        root=Path(directory).resolve()
        for relative,body in snapshot.files.items():
            target=root/relative; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(body)
        yield root
