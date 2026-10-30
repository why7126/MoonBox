"""Versioned recovery scope shared with executor permissions; Git ignore is not authority."""
import hashlib
import json
import os
from pathlib import PurePosixPath
from app.chat.snapshot_store import parent_fd

# Host runtime, credentials and Git administration are never writable project content.
EXCLUDED = ('.git', '.env', '.env.local', '.env.production', '.aws', '.ssh',
            '.codex', 'logs', 'data', '.runtime')
EXCLUDED_COMPONENTS = ('.git', '.aws', '.ssh', '.codex', 'node_modules', '.venv', 'venv',
    '__pycache__', '.cache', 'dist', 'build', 'coverage', '.next')


def excluded(relative):
    parts = PurePosixPath(relative).parts
    return (relative in EXCLUDED or any(part in EXCLUDED_COMPONENTS or part.startswith('.env') for part in parts)
        or relative.endswith(('.sqlite', '.sqlite3', '.db', '.db-wal', '.db-shm')))


def roots(write_scope, delivery=None):
    if write_scope == 'read_only':
        return ()
    if delivery:
        from app.moonbox_core.delivery_policy import writable_roots
        return writable_roots(delivery['change_id']) if write_scope == 'implementation_write' else ()
    if write_scope == 'implementation_write':
        return ('',)
    if write_scope == 'governance_write':
        return ('issues', 'openspec/changes', 'iterations', 'docs/spec-logs')
    if write_scope == 'archive_write':
        return ('issues', 'openspec/changes', 'openspec/specs', 'openspec/archive', 'iterations', 'docs/spec-logs')
    raise ValueError('unknown_write_scope')


def policy_id(allowed):
    return hashlib.sha256(json.dumps(['workspace-scope-v1', allowed, EXCLUDED, EXCLUDED_COMPONENTS], separators=(',', ':')).encode()).hexdigest()


def names(root, allowed):
    development = any(value.startswith('openspec/changes/') for value in allowed)
    def walk(fd, prefix):
        with os.scandir(fd) as children:
            for child in children:
                relative = prefix + child.name
                if excluded(relative) or (development and (relative == 'docs/spec-logs' or relative.startswith('docs/spec-logs/'))):
                    continue
                if child.is_dir(follow_symlinks=False):
                    nested = os.open(child.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                    try:
                        yield from walk(nested, relative + '/')
                    finally:
                        os.close(nested)
                else:
                    yield relative
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for relative in allowed:
            if not relative:
                yield from walk(root_fd, '')
                continue
            from app.moonbox_rollout.recovery import validate_path
            validate_path(relative)
            directory = None
            try:
                directory, name = parent_fd(root_fd, relative)
                info = os.stat(name, dir_fd=directory, follow_symlinks=False)
                import stat
                if stat.S_ISDIR(info.st_mode):
                    nested = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                    try:
                        yield from walk(nested, relative + '/')
                    finally:
                        os.close(nested)
                else:
                    yield relative
            except FileNotFoundError:
                continue
            finally:
                if directory is not None:
                    os.close(directory)
    finally:
        os.close(root_fd)
