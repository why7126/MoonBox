"""Bounded, noninteractive Git operations; never accept arbitrary command arguments."""
from __future__ import annotations

from dataclasses import dataclass
from functools import wraps
import fcntl
import hashlib
import os
from pathlib import Path
import re
import subprocess
import stat
from uuid import UUID

from app.chat.workspace import WorkspaceError, git_env, trusted_directory


class WorktreeConflict(WorkspaceError):
    """Safe reason code; command output and physical paths stay private."""


def _run(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ['git', '-c', 'core.hooksPath=/dev/null', '-c', 'core.fsmonitor=false',
             '-c', 'protocol.file.allow=never', '-C', str(root), *args],
            env=git_env(), capture_output=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        raise WorktreeConflict('git_unavailable') from None
    if result.returncode:
        raise WorktreeConflict('git_operation_failed')
    return result.stdout


def _oid(value: str) -> str:
    if not re.fullmatch(r'[0-9a-f]{40}(?:[0-9a-f]{24})?', value):
        raise WorktreeConflict('invalid_commit')
    return value


def _serialized(method):
    @wraps(method)
    def locked(self, *args, **kwargs):
        directory = os.open(self.common_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        descriptor = None
        try:
            descriptor = os.open('moonbox-management.lock',
                os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600, dir_fd=directory)
            info = os.fstat(descriptor)
            if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                raise WorktreeConflict('repository_lock_invalid')
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise WorktreeConflict('repository_busy') from None
            if Repository.open(self.root).identity != self.identity:
                raise WorktreeConflict('repository_identity_mismatch')
            return method(self, *args, **kwargs)
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(directory)
    return locked


@dataclass(frozen=True)
class Repository:
    root: Path
    common_dir: Path
    identity: str

    @classmethod
    def open(cls, source: Path | str) -> 'Repository':
        root = trusted_directory(source)
        dotgit = root / '.git'
        if dotgit.is_symlink():
            raise WorktreeConflict('git_pointer_invalid')
        actual = Path(_run(root, 'rev-parse', '--show-toplevel').decode().strip())
        if actual != root:
            raise WorktreeConflict('project_root_required')
        common = Path(_run(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
        common = trusted_directory(common)
        if dotgit.is_file():
            git_dir = trusted_directory(Path(_run(root, 'rev-parse', '--absolute-git-dir').decode().strip()))
            back = git_dir / 'gitdir'
            if back.is_symlink() or not back.is_file() or back.read_text().strip() != str(dotgit):
                raise WorktreeConflict('git_pointer_invalid')
        info = common.stat()
        # A different repository replacing the same pathname is not the old instance.
        identity = hashlib.sha256(f'{common}\0{info.st_dev}\0{info.st_ino}'.encode()).hexdigest()
        return cls(root, common, identity)

    def head(self) -> str:
        return _oid(_run(self.root, 'rev-parse', '--verify', 'HEAD').decode().strip())

    def require_clean(self) -> None:
        if _run(self.root, 'status', '--porcelain=v1', '--untracked-files=all'):
            raise WorktreeConflict('workspace_has_changes')

    @_serialized
    def create(self, managed_root: Path | str, workspace_id: str, base: str) -> Path:
        """Create a real linked tree at a fixed commit. Never adopt an arbitrary directory."""
        identifier = str(UUID(workspace_id))
        base = _oid(base)
        parent = trusted_directory(managed_root)
        if parent == self.root or parent in self.root.parents or self.root in parent.parents:
            raise WorktreeConflict('managed_root_overlap')
        target = parent / identifier
        if target.exists() or target.is_symlink():
            raise WorktreeConflict('workspace_already_exists')
        _run(self.root, 'cat-file', '-e', base + '^{commit}')
        branch = 'moonbox/' + identifier
        _run(self.root, 'worktree', 'add', '-b', branch, '--', str(target), base)
        self.verify(target)
        return target

    def verify(self, target: Path | str) -> 'Repository':
        child = Repository.open(target)
        if child.identity != self.identity:
            raise WorktreeConflict('repository_identity_mismatch')
        records = _run(self.root, 'worktree', 'list', '--porcelain', '-z').split(b'\0')
        expected = b'worktree ' + str(child.root).encode()
        if expected not in records:
            raise WorktreeConflict('worktree_not_registered')
        return child

    @_serialized
    def remove(self, target: Path | str, *, integrated_into: str) -> None:
        child = self.verify(target)
        if child.root == self.root or child.common_dir == child.root / '.git':
            raise WorktreeConflict('main_workspace_protected')
        child.require_clean()
        # No --force: Git locks, submodules and unexpected contents remain protected.
        _run(self.root, 'merge-base', '--is-ancestor', child.head(), _oid(integrated_into))
        _run(self.root, 'worktree', 'remove', '--', str(child.root))

    @_serialized
    def advance(self, target: Path | str) -> str:
        """Reuse a completed delivery tree only by a clean fast-forward to current main."""
        self.require_clean()
        child = self.verify(target)
        child.require_clean()
        _run(child.root, 'symbolic-ref', '--quiet', 'HEAD')
        head = self.head()
        _run(child.root, 'merge', '--ff-only', '--no-edit', head)
        if child.head() != head:
            raise WorktreeConflict('workspace_advance_unknown')
        return head

    @_serialized
    def candidate(self, source_commit: str, target_commit: str) -> str:
        """Create an immutable two-parent candidate without changing any checkout."""
        source, target = _oid(source_commit), _oid(target_commit)
        if self.head() != target:
            raise WorktreeConflict('target_changed')
        self.require_clean()
        tree = _run(self.root, 'merge-tree', '--write-tree', target, source).decode().splitlines()[0]
        _oid(tree)
        commit = _run(self.root, '-c', 'user.name=MoonBox Integration',
            '-c', 'user.email=integration@moonbox.invalid', 'commit-tree', tree,
            '-p', target, '-p', source, '-m', 'MoonBox verified integration candidate').decode().strip()
        return _oid(commit)

    @_serialized
    def integrate(self, candidate_commit: str, *, source_commit: str, target_commit: str) -> str:
        """Caller owns repository lease and freshly authorized human confirmation."""
        candidate, source, target = map(_oid, (candidate_commit, source_commit, target_commit))
        parents = _run(self.root, 'show', '-s', '--format=%P', candidate).decode().strip().split()
        if parents != [target, source]:
            raise WorktreeConflict('candidate_parent_mismatch')
        actual = self.head()
        if actual == candidate:
            return candidate  # Git succeeded before the journal commit; no second merge.
        if actual != target:
            raise WorktreeConflict('target_changed')
        self.require_clean()
        _run(self.root, 'symbolic-ref', '--quiet', 'HEAD')  # Never integrate into detached main.
        _run(self.root, 'merge', '--ff-only', '--no-edit', candidate)
        if self.head() != candidate:
            raise WorktreeConflict('integration_outcome_unknown')
        return candidate
