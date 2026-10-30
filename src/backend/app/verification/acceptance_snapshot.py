"""Bounded uncommitted source capture under the caller's exclusive workspace lease.

This module consumes server-authorized exact paths, never a client directory or glob.
A second complete scan rejects concurrent external edits; the lease must remain held
until the immutable capture has been published by the orchestrator.
"""
import hashlib
import json
import os
import stat
from pathlib import Path

from app.chat.snapshot_store import parent_fd
from app.chat.workspace import trusted_directory
from app.moonbox_rollout.recovery import validate_path
from app.verification.acceptance_state import Conflict

LIMIT_FILE = 64 * 1024 * 1024
LIMIT_TOTAL = 512 * 1024 * 1024
DENIED = {'.git', '.aws', '.ssh', '.codex', 'node_modules', '__pycache__', '.venv', 'venv', 'logs', '.runtime'}


def source_path(value):
    try:
        validate_path(value)
    except ValueError:
        raise Conflict('snapshot_path_invalid') from None
    parts = value.split('/')
    if (len(value) > 4096 or any(p in DENIED for p in parts)
            or any(p == '.env' or p.startswith('.env.') and p not in {'.env.example', '.env.sample'} for p in parts)
            or Path(value).suffix.lower() in {'.pem', '.key', '.sqlite', '.sqlite3', '.db', '.db-wal', '.db-shm'}):
        raise Conflict('snapshot_path_forbidden')
    return value


def _read(root_fd, path):
    directory = None
    try:
        directory, name = parent_fd(root_fd, path)
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise Conflict('snapshot_file_unsafe')
            if before.st_size > LIMIT_FILE:
                raise Conflict('snapshot_file_limit')
            chunks = []; size = 0
            while block := os.read(fd, 65536):
                size += len(block)
                if size > LIMIT_FILE: raise Conflict('snapshot_file_limit')
                chunks.append(block)
            after = os.fstat(fd)
            current = os.stat(name, dir_fd=directory, follow_symlinks=False)
            fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns', 'st_mode', 'st_nlink')
            if any(getattr(before, k) != getattr(after, k) or getattr(after, k) != getattr(current, k) for k in fields):
                raise Conflict('snapshot_changed')
            return b''.join(chunks), 0o755 if before.st_mode & 0o111 else 0o644
        finally:
            os.close(fd)
    except FileNotFoundError:
        return None, None
    except OSError:
        raise Conflict('snapshot_file_unsafe') from None
    finally:
        if directory is not None: os.close(directory)


def capture(root, authorized_paths, *, binding, head_commit):
    paths = sorted(set(source_path(p) for p in authorized_paths))
    if not paths or len(paths) > 100000: raise Conflict('snapshot_scope_invalid')
    root_fd = os.open(trusted_directory(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        content = {}; manifest = []; total = 0
        for path in paths:
            data, mode = _read(root_fd, path)
            total += len(data) if data is not None else 0
            if total > LIMIT_TOTAL: raise Conflict('snapshot_total_limit')
            content[path] = (data, mode)
            manifest.append([path, hashlib.sha256(data).hexdigest() if data is not None else None, mode])
        for path in paths:
            if _read(root_fd, path) != content[path]: raise Conflict('snapshot_changed')
        digest = hashlib.sha256(json.dumps([binding, head_commit, manifest], separators=(',', ':')).encode()).hexdigest()
        return {'digest': digest, 'manifest': manifest, 'content': content}
    finally:
        os.close(root_fd)
