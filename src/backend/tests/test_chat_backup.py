import json
from pathlib import Path
import sqlite3
import pytest
from sqlalchemy import insert, select
from test_chat import chat, create, queued
from app.chat import service
from app.chat.backup import LocalBackupStore
from app.chat.schema import messages, audit
from app.chat.schema import task_traces, task_trace_spans


def setup_store(chat, tmp_path):
    client, factory = chat
    with factory() as db:
        if db.get_bind().dialect.name != 'sqlite':pytest.skip('SQLite offline backup adapter')
        source = Path(db.get_bind().url.database).absolute()
    root = tmp_path / 'backups';root.mkdir(mode=0o700)
    return LocalBackupStore(root, initialize=True), source


def test_backup_yields_source_lock_and_keeps_concurrent_commit(tmp_path, monkeypatch):
    from app.chat import backup
    root = tmp_path / 'backups'; root.mkdir(mode=0o700)
    source = tmp_path / 'source.sqlite'
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE payload (body BLOB)')
        db.executemany('INSERT INTO payload VALUES (zeroblob(4096))', [()] * 600)
        db.execute('CREATE TABLE marker (value TEXT)')
    store = LocalBackupStore(root, initialize=True)
    commits = []
    def yielding(seconds):
        if commits:
            return
        # The progress callback runs between backup steps. A separate writer
        # must commit here, before backup completes, without waiting for it.
        with sqlite3.connect(source, timeout=.05) as writer:
            writer.execute("INSERT INTO marker VALUES ('concurrent')")
        commits.append(True)
    monkeypatch.setattr(backup.time, 'sleep', yielding)
    backup_id = store.create(source)
    assert commits == [True]
    with sqlite3.connect(root / (backup_id + '.sqlite')) as copied:
        assert copied.execute('PRAGMA integrity_check').fetchone() == ('ok',)
        assert copied.execute('SELECT COUNT(*) FROM payload').fetchone() == (600,)
        assert copied.execute('SELECT value FROM marker').fetchone() == ('concurrent',)


def test_busy_automatic_copy_keeps_old_backup_and_worker_retries(chat, tmp_path, monkeypatch):
    from app.chat import backup, platform_worker
    _, factory = chat
    store, source = setup_store(chat, tmp_path)
    old = store.create(source, origin='automatic')
    with sqlite3.connect(source) as db:
        db.execute('CREATE TABLE synthetic_load (body BLOB)')
        db.executemany('INSERT INTO synthetic_load VALUES (zeroblob(4096))', [()] * 600)
    monkeypatch.setattr(backup, 'AUTOMATIC_COPY_SECONDS', 0)
    assert platform_worker.initial_snapshot_delay(factory, store, source, 1) == 300
    assert {row['id'] for row in store.inventory()} == {old}
    assert next(iter(store.inventory()))['valid']
    assert {p.name for p in store.root.glob('*.sqlite')} == {'deletions.sqlite', old + '.sqlite'}
    with factory() as db:
        assert db.scalar(select(task_traces.c.id).where(task_traces.c.status == 'failed'))
    monkeypatch.setattr(backup, 'AUTOMATIC_COPY_SECONDS', 60)
    assert platform_worker.initial_snapshot_delay(factory, store, source, 1) == 86400
    assert len(store.inventory()) == 1
    assert next(iter(store.inventory()))['id'] != old


def test_real_backup_delete_restore_cannot_resurrect(chat, tmp_path, monkeypatch):
    client, factory = chat
    store, source = setup_store(chat, tmp_path)
    cid = create(client);tid = queued(factory, cid)
    client.post(f'/api/v1/chat/turns/{tid}/interrupt')
    other = create(client);other_turn = queued(factory, other)
    code = tmp_path / 'code.txt';code.write_text('preserve code')
    with factory() as db:
        db.execute(insert(messages).values(**service.identity(), turn_id=tid, role='assistant', content='synthetic deleted content'))
        db.commit()
        audit_count = len(list(db.scalars(select(audit.c.id))))
    backup_id = store.create(source)
    monkeypatch.setenv('MOONBOX_CHAT_BACKUP_ROOT', str(store.root))
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION', json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}))
    assert client.delete(f'/api/v1/chat/conversations/{cid}').status_code == 200
    assert not store.copies_cleared(cid)
    from app.chat.cleanup import process_copies
    with factory() as db:
        assert not process_copies(db,cid,lambda _:False,lambda job:store.copies_cleared(job['conversation_id']))
    restored = tmp_path / 'restored.sqlite'
    assert store.restore(backup_id, restored)['deleted_conversations_replayed'] == 1
    with sqlite3.connect(restored) as db:
        assert db.execute('SELECT deleted_at,title FROM chat_conversations WHERE id=?', (cid,)).fetchone()[0]
        assert db.execute('SELECT COUNT(*) FROM chat_messages WHERE turn_id=?', (tid,)).fetchone()[0] == 0
        assert db.execute('SELECT COUNT(*) FROM chat_turns WHERE id=?', (tid,)).fetchone()[0] == 0
        assert db.execute('SELECT COUNT(*) FROM chat_request_logs').fetchone()[0] == audit_count
        assert db.execute('SELECT status FROM chat_turns WHERE id=?', (other_turn,)).fetchone()[0] == 'unknown'
        assert db.execute('SELECT active_turn_id FROM chat_conversations WHERE id=?', (other,)).fetchone()[0] == other_turn
    assert code.read_text() == 'preserve code'
    # The immutable backup still contains old content until explicit physical expiry.
    with sqlite3.connect(store.root / (backup_id + '.sqlite')) as db:
        assert db.execute('SELECT COUNT(*) FROM chat_messages').fetchone()[0] == 1
    assert store.expire(backup_id)
    assert not (store.root / (backup_id + '.sqlite')).exists()
    assert store.ledger.exists()
    assert store.copies_cleared(cid)
    with factory() as db:
        assert process_copies(db,cid,lambda _:False,lambda job:store.copies_cleared(job['conversation_id']))
    assert not store.expire(backup_id)


def test_missing_ledger_blocks_deletion_and_restore(chat, tmp_path, monkeypatch):
    client, factory = chat;store, source = setup_store(chat, tmp_path)
    cid=create(client);tid=queued(factory,cid);client.post(f'/api/v1/chat/turns/{tid}/interrupt')
    backup_id=store.create(source)
    monkeypatch.setenv('MOONBOX_CHAT_BACKUP_ROOT', str(store.root))
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION', json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}))
    store.ledger.rename(store.root / 'held-ledger.sqlite')
    assert client.delete(f'/api/v1/chat/conversations/{cid}').status_code == 409
    assert client.get(f'/api/v1/chat/conversations/{cid}').status_code == 200
    with pytest.raises(ValueError):store.restore(backup_id, tmp_path / 'missing.sqlite')
    assert not (tmp_path / 'missing.sqlite').exists()


def test_corrupt_backup_existing_target_and_wrong_database_rejected(chat,tmp_path):
    store,source=setup_store(chat,tmp_path);backup_id=store.create(source)
    destination=tmp_path/'occupied.sqlite';destination.write_text('preserve')
    with pytest.raises(ValueError):store.restore(backup_id,destination)
    assert destination.read_text()=='preserve'
    with pytest.raises(ValueError):store.record_deletion('test',source=tmp_path/'other.sqlite')
    (store.root/(backup_id+'.sqlite')).write_bytes(b'corrupt')
    with pytest.raises(ValueError):store.restore(backup_id,tmp_path/'corrupt.sqlite')
    assert not (tmp_path/'corrupt.sqlite').exists()


def test_empty_conversation_deletion_also_survives_restore(chat,tmp_path,monkeypatch):
    client,_=chat;store,source=setup_store(chat,tmp_path);cid=create(client)
    backup_id=store.create(source)
    monkeypatch.setenv('MOONBOX_CHAT_BACKUP_ROOT',str(store.root))
    response=client.delete(f'/api/v1/chat/conversations/{cid}')
    assert response.status_code==200
    assert response.json()['data']['backup_status']=='pending'
    output=tmp_path/'empty-restored.sqlite';store.restore(backup_id,output)
    with sqlite3.connect(output) as db:
        assert db.execute('SELECT deleted_at FROM chat_conversations WHERE id=?',(cid,)).fetchone()[0]


def test_automatic_rotation_preserves_manual_and_protected_backups(chat, tmp_path):
    store, source = setup_store(chat, tmp_path)
    manual = store.create(source)
    protected = store.create(source, origin='automatic')
    store.protect(protected, 'governance-bundle')
    old = store.create(source, origin='automatic')
    result = store.create_automatic(source, 1)
    assert result == {'created': True, 'expired': 1, 'protected': 1}
    inventory = store.inventory()
    assert {row['id'] for row in inventory} >= {manual, protected}
    assert old not in {row['id'] for row in inventory}
    assert len([row for row in inventory if row['origin'] == 'automatic' and not row['protected']]) == 1
    with pytest.raises(ValueError, match='protected'):
        store.expire(protected)
    assert store.create_automatic(source, 0)['created'] is False
    assert store.ledger.exists()


def test_old_unclassified_snapshots_are_not_rotated(chat, tmp_path):
    store, source = setup_store(chat, tmp_path)
    old = store.create(source)
    with sqlite3.connect(store.ledger) as db:
        db.execute('DELETE FROM backup_metadata WHERE id=?', (old,))
    store.create_automatic(source, 1)
    assert next(row for row in store.inventory() if row['id'] == old)['origin'] == 'unknown'
    assert (store.root / (old + '.sqlite')).exists()


def test_rotation_failure_keeps_previous_recovery_point_and_trace(chat, tmp_path, monkeypatch):
    _, factory = chat
    store, source = setup_store(chat, tmp_path)
    old = store.create(source, origin='automatic')
    def failed_expire(*_args, **_kwargs):
        raise OSError('synthetic expire failure')
    monkeypatch.setattr(store, 'expire', failed_expire)
    from app.chat.platform_worker import automatic_snapshot
    with pytest.raises(OSError, match='synthetic'):
        automatic_snapshot(factory, store, source, 1)
    assert (store.root / (old + '.sqlite')).is_file()
    assert next(row for row in store.inventory() if row['id'] == old)['valid']
    with factory() as db:
        row = db.execute(select(task_traces).where(task_traces.c.task_type == 'local_snapshot')).mappings().one()
        assert row['status'] == 'failed' and row['task_type'] == 'local_snapshot'
        assert len(list(db.scalars(select(task_trace_spans.c.id).where(task_trace_spans.c.task_trace_id == row['task_trace_id'])))) == 2


def test_worker_snapshot_start_and_periodic_limit_zero(chat, tmp_path):
    _, factory = chat
    store, source = setup_store(chat, tmp_path)
    from app.chat.platform_worker import automatic_snapshot
    assert automatic_snapshot(factory, store, source, 2)['created']
    assert automatic_snapshot(factory, store, source, 2)['created']
    assert automatic_snapshot(factory, store, source, 2)['expired'] == 1
    assert len(store.inventory()) == 2
    assert automatic_snapshot(factory, store, source, 0)['created'] is False
    assert len(store.inventory()) == 2
    with factory() as db:
        assert db.scalar(select(task_traces.c.id).where(task_traces.c.status == 'skipped'))


def test_snapshot_registration_failure_preserves_old_backup(chat, tmp_path, monkeypatch):
    store, source = setup_store(chat, tmp_path)
    old = store.create(source, origin='automatic')
    from app.chat import backup as backup_module
    def failed_digest(*_args):
        raise OSError('synthetic registration failure')
    monkeypatch.setattr(backup_module, 'digest', failed_digest)
    with pytest.raises(OSError, match='registration'):
        store.create_automatic(source, 1)
    assert (store.root / (old + '.sqlite')).is_file()
    with sqlite3.connect(store.ledger) as db:
        assert db.execute('SELECT count(*) FROM backups').fetchone()[0] == 1


def test_interrupted_expiry_reconciles_file_and_ledger(chat, tmp_path):
    store, source = setup_store(chat, tmp_path)
    bid = store.create(source, origin='automatic')
    backup = store.root / (bid + '.sqlite')
    stage = store.root / ('.expiring-' + bid + '.sqlite')
    backup.replace(stage)
    assert next(row for row in store.inventory() if row['id'] == bid)['valid']
    assert backup.is_file() and not stage.exists()
    backup.replace(stage)
    with sqlite3.connect(store.ledger) as db:
        db.execute('DELETE FROM backups WHERE id=?', (bid,))
    assert store.inventory() == []
    assert not stage.exists()


def test_v2_deleted_content_cannot_return_through_backup(chat, tmp_path, monkeypatch):
    from app.chat import content_store
    from app.chat.content_schema import objects, segments
    client, factory = chat; store, source = setup_store(chat, tmp_path)
    cid = create(client); tid = queued(factory, cid)
    with factory() as db:
        content_store.result(db, cid, tid, 'final', 'synthetic', 0, b'persisted v2')
        db.commit()
    client.post(f'/api/v1/chat/turns/{tid}/interrupt')
    backup_id = store.create(source)
    monkeypatch.setenv('MOONBOX_CHAT_BACKUP_ROOT', str(store.root))
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION', json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}))
    response = client.delete(f'/api/v1/chat/conversations/{cid}')
    assert response.status_code == 200, response.text
    restored = tmp_path / 'v2-restored.sqlite'
    store.restore(backup_id, restored)
    with sqlite3.connect(restored) as db:
        assert db.execute('SELECT COUNT(*) FROM chat_content_objects').fetchone()[0] == 0
        assert db.execute('SELECT COUNT(*) FROM chat_content_chunks').fetchone()[0] == 0
        assert db.execute('SELECT COUNT(*) FROM chat_result_segments').fetchone()[0] == 0
    assert client.get(f'/api/v1/chat/turns/{tid}/results').status_code in (403, 404)
