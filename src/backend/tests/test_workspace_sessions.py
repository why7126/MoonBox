import pytest
from sqlalchemy import create_engine, insert, update
from sqlalchemy.orm import sessionmaker
from app.chat.schema import metadata, conversations, turns
from app.moonbox_core.schema import TABLES
from app.moonbox_core.workspaces import register_main, stamp
from app.moonbox_core.sessions import bind, execution_workspace
from app.moonbox_worktree import WorktreeConflict
from test_managed_worktree_git import repo


@pytest.fixture
def session_data(tmp_path, repo):
    engine = create_engine('sqlite:///' + str(tmp_path / 'sessions.db'))
    metadata.create_all(engine, tables=[conversations, turns, *TABLES])
    factory = sessionmaker(engine)
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', repo[0].root)
        parent = dict(id='session', created_at=stamp(), updated_at=stamp(), owner_id='actor', space_id='space', repository_id='repo', title='任务', active_turn_id=None, archived=0)
        db.execute(insert(conversations).values(**parent))
    yield factory, parent, main
    engine.dispose()


def test_binding_is_immutable_and_resolves_trusted_root(session_data):
    factory, parent, main = session_data
    with factory.begin() as db:
        assert bind(db, parent, main['id'])['id'] == main['id']
        assert bind(db, parent, main['id'])['id'] == main['id']
        assert str(execution_workspace(db, parent)[1]) == main['root_locator']
        with pytest.raises(WorktreeConflict, match='immutable'):
            bind(db, parent, 'different-workspace')


@pytest.mark.parametrize('values,reason', [
    ({'active_turn_id': 'running'}, 'busy'),
    ({'archived': 1}, 'unavailable'),
    ({'workspace_id': 'source'}, 'legacy'),
    ({'thread_id': 'external-thread'}, 'legacy'),
])
def test_stale_parent_cannot_move_active_or_historical_session(session_data, values, reason):
    factory, parent, main = session_data
    with factory.begin() as db:
        db.execute(update(conversations).where(conversations.c.id == parent['id']).values(**values))
    with factory.begin() as db:
        with pytest.raises(WorktreeConflict, match=reason):
            bind(db, parent, main['id'])


def test_repository_replaced_at_same_path_cannot_resume(session_data, tmp_path):
    from pathlib import Path
    from test_managed_worktree_git import git
    factory, parent, main = session_data
    with factory.begin() as db:
        bind(db, parent, main['id'])
    root = Path(main['root_locator'])
    root.rename(tmp_path / 'original-preserved')
    root.mkdir()
    git(root, 'init', '-q', '-b', 'main')
    (root / 'file').write_text('replacement')
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'replacement')
    with factory() as db:
        with pytest.raises(WorktreeConflict, match='repository_identity_mismatch'):
            execution_workspace(db, parent)
