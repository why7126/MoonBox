import json
from pathlib import Path
import sqlite3
import pytest
from sqlalchemy import insert, select
from test_chat import chat, create, queued
from app.chat import service
from app.chat.backup import LocalBackupStore
from app.chat.schema import messages, audit


def setup_store(chat, tmp_path):
    client, factory = chat
    with factory() as db:
        if db.get_bind().dialect.name != 'sqlite':pytest.skip('SQLite offline backup adapter')
        source = Path(db.get_bind().url.database).absolute()
    root = tmp_path / 'backups';root.mkdir(mode=0o700)
    return LocalBackupStore(root, initialize=True), source


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
