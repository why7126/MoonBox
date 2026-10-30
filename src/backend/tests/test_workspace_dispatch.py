"""The queue skips occupied workspaces without blocking unrelated delivery chains."""
from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker
from app.chat.schema import metadata, conversations, turns
from app.chat.content_schema import prepare_attempts
from app.moonbox_core.schema import TABLES, session_bindings, write_locks
from app.moonbox_core.workspaces import register_main, stamp
from app.chat.worker import claim
from test_managed_worktree_git import repo


def test_queue_serializes_shared_workspace_and_preserves_unknown_lock(tmp_path, repo, monkeypatch):
    from app.chat import observability
    monkeypatch.setattr(observability, 'trace', lambda *args, **kwargs: None)
    engine = create_engine('sqlite:///' + str(tmp_path / 'queue.db'))
    metadata.create_all(engine, tables=[conversations, turns, prepare_attempts, *TABLES])
    factory = sessionmaker(engine)
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', repo[0].root)
        for number in range(3):
            cid, tid = 'c'+str(number), 't'+str(number)
            db.execute(insert(conversations).values(id=cid, created_at=stamp(), updated_at=stamp(),
                owner_id='a', space_id='space', repository_id='repo', title='test', active_turn_id=tid))
            db.execute(insert(turns).values(id=tid, created_at=str(number), updated_at=stamp(),
                conversation_id=cid, client_request_id=tid, status='queued', prompt='test'))
            if number < 2:
                db.execute(insert(session_bindings).values(conversation_id=cid, workspace_id=main['id']))
    with factory() as db:
        first = claim(db, 'worker-a')
        assert first['turn_id'] == 't0'
    with factory() as db:
        second = claim(db, 'worker-b')
        assert second['turn_id'] == 't2'  # t1 waits, unrelated legacy queue remains live.
    with factory() as db:
        assert claim(db, 'worker-c') is None
        assert db.scalar(select(turns.c.status).where(turns.c.id == 't1')) == 'queued'
        assert db.scalar(select(write_locks.c.operation_id)) == 't0'
    engine.dispose()
