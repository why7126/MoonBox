import hashlib
import pytest
from sqlalchemy import select, func
from test_chat import chat, create, queued
from app.chat import content_store as store
from app.chat.content_schema import objects, chunks, ledger, segments


def test_content_publish_replay_and_isolation(chat):
    client, factory = chat
    cid = create(client); other = create(client)
    payload = b'a' * store.CHUNK_BYTES
    with factory() as db:
        oid = store.put(db, cid, 'text', iter([payload, b'tail']))
        assert store.put(db, cid, 'text', iter([payload, b'tail'])) == oid
        assert store.put(db, other, 'text', iter([payload, b'tail'])) != oid
        assert db.scalar(select(func.count()).select_from(ledger)) == 2
        assert store.read_page(db, oid) == (payload, 0)
        assert store.read_page(db, oid, 0) == (b'tail', None)
        assert db.scalar(select(objects.c.sha256).where(objects.c.id == oid)) == hashlib.sha256(payload+b'tail').hexdigest()
        db.commit()


def test_uncommitted_content_and_chunk_checkpoints(chat):
    client, factory = chat; cid = create(client)
    with factory() as db:
        oid = store.begin(db, cid, 'text')
        store.append(db, oid, 0, b'one')
        store.append(db, oid, 0, b'one')
        with pytest.raises(ValueError, match='conflicts'):
            store.append(db, oid, 0, b'two')
        with pytest.raises(ValueError, match='gap'):
            store.append(db, oid, 2, b'two')
        with pytest.raises(ValueError, match='unavailable'):
            store.read_page(db, oid)
        db.rollback()
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(objects)) == 0
        assert db.scalar(select(func.count()).select_from(chunks)) == 0


def test_result_replay_and_conflict(chat):
    client, factory = chat; cid = create(client); tid = queued(factory, cid)
    with factory() as db:
        assert store.result(db, cid, tid, 'output', 'source', 0, b'one') == 1
        assert store.result(db, cid, tid, 'output', 'source', 0, b'one') == 1
        with pytest.raises(ValueError, match='replay conflict'):
            store.result(db, cid, tid, 'output', 'source', 0, b'two')
        assert store.result(db, cid, tid, 'output', 'source', 3, b'two') == 2
        db.commit()
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(segments)) == 2


def test_source_gap_and_orphan_cleanup_keep_committed_result(chat):
    from app.chat.schema import conversations
    from sqlalchemy import update
    client, factory = chat; cid = create(client); tid = queued(factory, cid)
    with factory() as db:
        store.result(db, cid, tid, 'output', 'source', 0, b'one')
        with pytest.raises(ValueError, match='sequence gap'):
            store.result(db, cid, tid, 'output', 'source', 9, b'gap')
        orphan = store.put(db, cid, 'snapshot', [b'orphan'])
        db.execute(update(conversations).where(conversations.c.id == cid).values(active_turn_id=None))
        assert store.collect_orphans(db, cid) == 1
        assert db.scalar(select(objects.c.id).where(objects.c.id == orphan)) is None
        assert db.scalar(select(func.count()).select_from(segments)) == 1
        db.commit()


def test_storage_quota_atomic_and_metadata_idempotent(chat, monkeypatch):
    from app.chat.schema import usage_accounts
    from app.chat import service
    client, factory = chat; cid = create(client)
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS', '{"user_storage_bytes":8,"space_storage_bytes":8}')
    with factory() as db:
        store.put(db, cid, 'text', [b'12345']); db.commit()
        store.charge_metadata(db, cid, 'synthetic-metadata', 2); db.commit()
        store.charge_metadata(db, cid, 'synthetic-metadata', 2); db.commit()
        with pytest.raises(service.ChatError):
            store.put(db, cid, 'text', [b'overflow'])
        db.rollback()
        assert db.scalar(select(usage_accounts.c.used_bytes).where(usage_accounts.c.id == 'user:alice')) == 7
        assert store.purge_conversation(db, cid) == 7


def test_disk_failure_preserves_previous_commit(chat, monkeypatch):
    from app.chat import resource_guard
    from app.chat.app_server import ExecutorError
    client, factory = chat; cid = create(client)
    with factory() as db:
        oid = store.put(db, cid, 'text', [b'saved']); db.commit()
        def fail(_): raise ExecutorError('workspace_resource_exhausted')
        monkeypatch.setattr(resource_guard, 'require_database_disk', fail)
        with pytest.raises(ExecutorError): store.put(db, cid, 'text', [b'not-saved'])
        db.rollback()
        assert store.read_page(db, oid) == (b'saved', None)


def test_chat_lock_budget_restores_pool_configuration(chat):
    from app.chat.resource_guard import lock_budget
    client, factory = chat
    with factory() as db:
        mysql = db.get_bind().dialect.name == 'mysql'
        query = 'SELECT @@SESSION.innodb_lock_wait_timeout' if mysql else 'PRAGMA busy_timeout'
        original = db.connection().exec_driver_sql(query).scalar()
        lock_budget(db)
        assert db.connection().exec_driver_sql(query).scalar() == (5 if mysql else 5000)
        db.commit()
        assert db.connection().exec_driver_sql(query).scalar() == original


def test_concurrent_writers_cannot_exceed_finite_operating_storage(chat, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from app.chat import service
    from app.chat.schema import usage_accounts
    client, factory = chat; cids = [create(client), create(client)]
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS','{"user_storage_bytes":5,"space_storage_bytes":5}')
    def write(cid):
        with factory() as db:
            try:
                store.put(db, cid, 'text', [b'four']); db.commit(); return 'saved'
            except service.ChatError as error:
                db.rollback(); assert error.code == 2508; return 'quota'
    with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(write, cids))
    assert sorted(results) == ['quota','saved']
    with factory() as db:
        assert db.scalar(select(usage_accounts.c.used_bytes).where(usage_accounts.c.id == 'user:alice')) == 4
