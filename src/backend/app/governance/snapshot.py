"""Bounded stable worktree snapshots. Links and nonregular files fail closed."""
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import yaml
from collections import OrderedDict
from threading import RLock
from app.chat.service import ChatError

LIMIT_FILE = 1024 * 1024
LIMIT_TOTAL = 32 * 1024 * 1024
LIMIT_COUNT = 10000
ROOTS = ('issues', 'iterations', 'openspec', 'docs', 'rules')
EXTENSIONS = {'.md', '.yaml', '.yml', '.html'}


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
    validate(files)
    with _validation_lock:
        _validated[revision] = True
        while len(_validated) > 32:
            _validated.popitem(last=False)


@dataclass(frozen=True)
class Snapshot:
    files: dict[str, bytes]
    revision: str


def digest(files):
    manifest = [(name, 'regular', hashlib.sha256(body).hexdigest()) for name,body in sorted(files.items())]
    return hashlib.sha256(json.dumps(manifest,separators=(',',':')).encode()).hexdigest()


def read_once(root):
    files = {}; total = 0
    def walk(fd, prefix, depth=0):
        nonlocal total
        if depth > 24: raise ValueError('depth')
        for name in sorted(os.listdir(fd)):
            if name.startswith('.') or name in ('node_modules','__pycache__'): continue
            relative = f'{prefix}/{name}' if prefix else name
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode): raise ValueError('link')
            if stat.S_ISDIR(info.st_mode):
                child = os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
                try: walk(child,relative,depth+1)
                finally: os.close(child)
            elif Path(name).suffix in EXTENSIONS:
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1: raise ValueError('type')
                child = os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                try:
                    before = os.fstat(child)
                    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > LIMIT_FILE: raise ValueError('size')
                    with os.fdopen(os.dup(child),'rb') as stream: body = stream.read(LIMIT_FILE+1)
                    after = os.fstat(child)
                    if (before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns) != (after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns): raise ValueError('changed')
                finally: os.close(child)
                total += len(body)
                if len(body)>LIMIT_FILE or total>LIMIT_TOTAL or len(files)>=LIMIT_COUNT: raise ValueError('size')
                files[relative] = body
    fd = os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        for name in ROOTS:
            try: child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            except FileNotFoundError: continue
            try: walk(child,name)
            finally: os.close(child)
    finally: os.close(fd)
    return files


def validate(files):
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
    for name,body in files.items():
        content=body.decode('utf-8')
        if name.endswith(('.yaml','.yml')): safe_load(content)
        elif name.endswith('.md') and content.startswith('---\n'):
            parts=content.split('---',2)
            if len(parts)!=3 or not isinstance(safe_load(parts[1]),dict): raise ValueError('frontmatter')


def stable(root, retries=3):
    kind = 'source_changing'
    for _ in range(retries):
        try:
            first = read_once(root)
            second = read_once(root)
        except (OSError, ValueError) as exc:
            kind = 'source_changing' if str(exc) == 'changed' or isinstance(exc, FileNotFoundError) else 'source_unavailable'
            continue
        if first != second:
            kind = 'source_changing'
            continue
        revision = digest(second)
        try:
            _validate_revision(second, revision)
        except (ValueError, KeyError, yaml.YAMLError, UnicodeError):
            # Identical complete reads prove a stable invalid input. Do not scan
            # it three more times or expose the parser's path/content in errors.
            raise ChatError(2603, '项目数据格式暂不可解析，请修复后重新加载', 503, kind='source_invalid') from None
        return Snapshot(second, revision)
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
                for relative, body in snapshot.files.items():
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
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
