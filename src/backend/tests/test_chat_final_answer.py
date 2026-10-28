import hashlib
import json
import pytest
from sqlalchemy import select, update, insert, func
from test_chat import chat, create, queued
from app.chat import content_store, final_answer, assistant_output, result_reader, service
from app.chat.schema import events, turns
from app.chat.content_schema import segments


def publish(db, cid, tid, item, parts, complete=True):
    source = final_answer.source(item)
    final_answer.mark(db, tid, source, 'begin')
    offset = 0
    for part in parts:
        content_store.result(db, cid, tid, 'final', source, offset, part.encode())
        offset += len(part.encode())
    if complete:
        final_answer.mark(db, tid, source, 'complete')


def test_cross_path_identity_and_conflict(chat):
    client, factory = chat; cid=create(client); tid=queued(factory,cid)
    with factory() as db:
        for first, second in [('final:a','recovered-final:a'), ('recovered-final:b','final:b')]:
            seq=content_store.result(db,cid,tid,'final',first,0,'中文'.encode())
            assert content_store.result(db,cid,tid,'final',second,0,'中文'.encode()) == seq
            with pytest.raises(ValueError, match='conflict'):
                content_store.result(db,cid,tid,'final',second,0,b'different')
        assert db.scalar(select(func.count()).select_from(segments)) == 2
        with pytest.raises(ValueError,match='identity'):
            final_answer.source(None)


def test_version_partial_and_cursor(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        publish(db,cid,tid,'a',['重复。','重复。'])
        publish(db,cid,tid,'b',['未完成'],False)
        assert assistant_output.saved_output(db,tid)['content']=='重复。重复。'
        with pytest.raises(ValueError,match='conflict'):
            content_store.result(db,cid,tid,'final','final:a',len('重复。重复。'.encode()),b'extension')
        old=result_reader.results(db,'alice',tid,'final')['resume_cursor']
        publish(db,cid,tid,'b',['未完成'])
        assert assistant_output.saved_output(db,tid)['content']=='未完成'
        with pytest.raises(service.ChatError):
            result_reader.results(db,'alice',tid,'final',old)
        # Replay old complete cannot supersede newer complete.
        publish(db,cid,tid,'a',['重复。','重复。'])
        assert assistant_output.saved_output(db,tid)['content']=='未完成'
        with pytest.raises(service.ChatError):
            result_reader.results(db,'bob',tid,'final')
        db.commit()


def test_legacy_recovery_projection_does_not_delete(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        # Simulate pre-fix hashed sources, without normalizing them at write time.
        for i,src in enumerate(['old-normal','old-recovery']):
            content_store.result(db,cid,tid,'final',src,0,b'repeat repeat')
        db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=1,
            source_id='reconcile:terminal',event_type='execution.state',payload='{}'))
        assert assistant_output.saved_output(db,tid)['content']=='repeat repeat'
        page=result_reader.results(db,'alice',tid,'final')
        assert ''.join(x['text'] for x in page['items'])=='repeat repeat'
        assert db.scalar(select(func.count()).select_from(segments))==2


def test_unknown_legacy_not_text_deduplicated(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        for src in ['old-a','old-b']:
            content_store.result(db,cid,tid,'final',src,0,b'legitimate')
        assert assistant_output.saved_output(db,tid)['content']=='legitimatelegitimate'
        assert assistant_output.saved_output(db,tid)['partial']


def test_complete_answer_paging_is_bounded(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        publish(db,cid,tid,'long',['中'*12000]*8)
        cursor=None; parts=[]
        while True:
            page=result_reader.results(db,'alice',tid,'final',cursor)
            assert sum(x['byte_count'] for x in page['items'])<=content_store.CHUNK_BYTES
            parts.extend(x['text'] for x in page['items'])
            cursor=page['next_cursor']
            if not cursor: break
        assert ''.join(parts)=='中'*96000


def test_persisted_message_refresh_uses_corrected_projection(chat):
    from app.chat.schema import messages
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        for src in ['old-normal','old-recovery']:
            content_store.result(db,cid,tid,'final',src,0,b'answer')
        db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=1,
            source_id='reconcile:terminal',event_type='execution.state',payload='{}'))
        assistant_output.persist_output(db,tid,'answeranswer')
        db.commit()
        page=assistant_output.message_page(db,cid,1,20)
        assert [m['content'] for m in page if m['role']=='assistant']==['answer']
        assert db.scalar(select(messages.c.content).where(messages.c.turn_id==tid,messages.c.role=='assistant'))=='answeranswer'
