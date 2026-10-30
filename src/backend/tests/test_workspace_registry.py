import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.chat.schema import metadata
from app.moonbox_core.schema import TABLES, workspaces, claims
from app.moonbox_core.workspaces import register_main, reserve_development, materialize, acquire, release, public
from app.moonbox_worktree import WorktreeConflict
from test_managed_worktree_git import repo


@pytest.fixture
def factory(tmp_path):
    engine = create_engine('sqlite:///' + str(tmp_path / 'registry.db'))
    metadata.create_all(engine, tables=[t for t in TABLES if t.name != 'moonbox_workspace_sessions'])
    yield sessionmaker(engine)
    engine.dispose()


def test_main_identity_and_cross_space_protection(factory, repo):
    git, managed = repo
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', git.root)
        assert register_main(db, 'space', 'repo', git.root)['id'] == main['id']
        assert 'root_locator' not in public(main)
        with pytest.raises(WorktreeConflict, match='repository_already_bound'):
            register_main(db, 'other', 'repo', git.root)


def test_chain_reservation_survives_reentry(factory, repo):
    git, managed = repo
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', git.root)
        first = reserve_development(db, main, 'REQ-0042', managed)
    with factory.begin() as db:
        repeated = reserve_development(db, main, 'REQ-0042', managed)
        assert repeated['id'] == first['id']
        ready = materialize(db, main, repeated)
    with factory.begin() as db:
        assert materialize(db, main, ready)['lifecycle'] == 'ready'
        assert len(db.execute(select(claims)).all()) == 1
        assert len(db.execute(select(workspaces)).all()) == 2


def test_workspace_lock_is_owned_and_not_stolen(factory, repo):
    git, managed = repo
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', git.root)
        acquire(db, main['id'], 'turn-a', 1)
    with factory.begin() as db:
        acquire(db, main['id'], 'turn-a', 1)
        with pytest.raises(WorktreeConflict, match='workspace_busy'):
            acquire(db, main['id'], 'turn-b', 2)
        assert release(db, main['id'], 'turn-a', 2) == 0
        assert release(db, main['id'], 'turn-a', 1) == 1
        acquire(db, main['id'], 'turn-b', 2)


def test_dirty_main_cannot_be_used_as_task_baseline(factory, repo):
    git, managed = repo
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', git.root)
        (git.root / 'file.txt').write_text('manual edit')
        with pytest.raises(WorktreeConflict, match='workspace_has_changes'):
            reserve_development(db, main, 'REQ-0042', managed)
        assert not db.execute(select(claims)).all()


def test_concurrent_requests_return_one_identity(factory, repo):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    source, managed = repo
    gate = Barrier(2)
    def register():
        gate.wait()
        with factory.begin() as db:
            return register_main(db, 'space', 'repo', source.root)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(register) for _ in range(2)]
        mains = [f.result() for f in futures]
    assert mains[0]['id'] == mains[1]['id']
    gate = Barrier(2)
    def reserve():
        gate.wait()
        with factory.begin() as db:
            return reserve_development(db, mains[0], 'REQ-0042', managed)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(reserve) for _ in range(2)]
        results = [f.result() for f in futures]
    assert results[0]['id'] == results[1]['id']


def test_linked_tree_cannot_become_second_main_and_remote_url_is_not_identity(factory, repo, tmp_path):
    from test_managed_worktree_git import git
    from uuid import uuid4
    source, managed = repo
    linked = source.create(managed, str(uuid4()), source.head())
    other = tmp_path / 'other-project'; other.mkdir()
    git(other, 'init', '-q', '-b', 'main')
    (other / 'file').write_text('other')
    git(other, 'add', '.')
    git(other, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'other')
    for root in (source.root, other):
        git(root, 'remote', 'add', 'origin', 'https://example.invalid/same.git')
    with factory.begin() as db:
        first = register_main(db, 'space', 'repo', source.root)
        with pytest.raises(WorktreeConflict):
            register_main(db, 'space', 'other-binding', linked)
        second = register_main(db, 'space', 'other-repo', other)
        assert first['git_identity'] != second['git_identity']


def test_lease_and_registration_do_not_escape_outer_rollback(factory, repo):
    source, _ = repo
    with factory() as db:
        main = register_main(db,'space','repo',source.root)
        db.rollback()
    with factory() as db:
        assert db.scalar(select(workspaces.c.id)) is None
        main = register_main(db,'space','repo',source.root)
        db.commit()
        acquire(db,main['id'],'pending',1)
        db.rollback()
    from app.moonbox_core.schema import write_locks
    with factory() as db:
        assert db.scalar(select(write_locks.c.operation_id)) is None
