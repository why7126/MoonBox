"""Real disposable Git repos exercise linked identity and loss-prevention boundaries."""
import subprocess
from uuid import uuid4

import pytest

from app.moonbox_worktree import Repository, WorktreeConflict


def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], stderr=subprocess.DEVNULL).decode().strip()


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / 'source'; root.mkdir()
    git(root, 'init', '-q', '-b', 'main')
    (root / 'file.txt').write_text('baseline')
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'baseline')
    managed = tmp_path / 'managed'; managed.mkdir()
    return Repository.open(root), managed


def test_real_linked_worktree_and_safe_removal(repo):
    source, managed = repo
    target = source.create(managed, str(uuid4()), source.head())
    assert (target / '.git').is_file()
    assert source.verify(target).identity == source.identity
    assert (target / 'file.txt').read_text() == 'baseline'
    source.remove(target, integrated_into=source.head())
    assert not target.exists()


def test_dirty_and_unmerged_results_are_preserved(repo):
    source, managed = repo
    target = source.create(managed, str(uuid4()), source.head())
    (target / 'file.txt').write_text('user work')
    with pytest.raises(WorktreeConflict, match='workspace_has_changes'):
        source.remove(target, integrated_into=source.head())
    git(target, 'add', '.')
    git(target, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'work')
    with pytest.raises(WorktreeConflict):
        source.remove(target, integrated_into=source.head())
    assert (target / 'file.txt').read_text() == 'user work'


def test_main_root_and_preexisting_target_protected(repo):
    source, managed = repo
    with pytest.raises(WorktreeConflict, match='main_workspace_protected'):
        source.remove(source.root, integrated_into=source.head())
    identifier = str(uuid4()); target = managed / identifier; target.mkdir()
    (target / 'keep').write_text('private')
    with pytest.raises(WorktreeConflict, match='workspace_already_exists'):
        source.create(managed, identifier, source.head())
    assert (target / 'keep').read_text() == 'private'


def test_outside_repo_cannot_be_adopted(repo, tmp_path):
    source, managed = repo
    other = tmp_path / 'other'; other.mkdir()
    git(other, 'init', '-q')
    with pytest.raises(WorktreeConflict, match='repository_identity_mismatch'):
        source.verify(other)


def test_overlapping_managed_root_rejected(repo):
    source, managed = repo
    with pytest.raises(WorktreeConflict, match='managed_root_overlap'):
        source.create(source.root, str(uuid4()), source.head())


def commit(root, content):
    (root / 'file.txt').write_text(content)
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', content)
    return git(root, 'rev-parse', 'HEAD')


def test_candidate_preserves_source_commits_and_integrates_exactly_once(repo):
    source, managed = repo
    base = source.head()
    task = source.create(managed, str(uuid4()), base)
    result = commit(task, 'task result')
    candidate = source.candidate(result, base)
    assert source.head() == base
    assert (source.root / 'file.txt').read_text() == 'baseline'
    assert git(source.root, 'show', '-s', '--format=%P', candidate).split() == [base, result]
    assert source.integrate(candidate, source_commit=result, target_commit=base) == candidate
    assert (source.root / 'file.txt').read_text() == 'task result'
    assert source.integrate(candidate, source_commit=result, target_commit=base) == candidate
    assert git(source.root, 'rev-list', '--count', 'HEAD') == '3'


def test_conflicts_leave_main_and_task_untouched(repo):
    source, managed = repo
    task = source.create(managed, str(uuid4()), source.head())
    result = commit(task, 'task change')
    target = commit(source.root, 'main change')
    with pytest.raises(WorktreeConflict):
        source.candidate(result, target)
    assert source.head() == target
    assert (source.root / 'file.txt').read_text() == 'main change'
    assert (task / 'file.txt').read_text() == 'task change'


def test_dirty_target_and_changed_target_refuse_integration(repo):
    source, managed = repo
    base = source.head()
    task = source.create(managed, str(uuid4()), base)
    result = commit(task, 'task result')
    candidate = source.candidate(result, base)
    (source.root / 'manual.txt').write_text('manual change')
    with pytest.raises(WorktreeConflict, match='workspace_has_changes'):
        source.integrate(candidate, source_commit=result, target_commit=base)
    assert (source.root / 'manual.txt').read_text() == 'manual change'
    commit(source.root, 'new main')
    with pytest.raises(WorktreeConflict, match='target_changed'):
        source.integrate(candidate, source_commit=result, target_commit=base)


def test_repository_management_operations_are_serialized(repo):
    import fcntl
    source, managed = repo
    with (source.common_dir / 'moonbox-management.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(WorktreeConflict, match='repository_busy'):
            source.create(managed, str(uuid4()), source.head())
    assert list(managed.iterdir()) == []


def test_forged_linked_git_pointer_is_rejected(repo, tmp_path):
    source, managed = repo
    target = source.create(managed, str(uuid4()), source.head())
    forged = tmp_path/'forged'; forged.mkdir()
    (forged/'.git').write_text((target/'.git').read_text())
    with pytest.raises(WorktreeConflict, match='git_pointer_invalid'):
        Repository.open(forged)
    assert source.verify(target).head() == source.head()
