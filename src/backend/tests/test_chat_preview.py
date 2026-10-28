"""Regression for short text split into many committed deltas."""
import pytest
from test_chat import chat, create, queued
from app.chat import assistant_output, content_store

@pytest.mark.parametrize('count', [20, 21, 22, 294])
def test_micro_segments_remain_complete(chat, count):
    client, factory = chat
    cid = create(client); tid = queued(factory, cid, 'running')
    with factory() as db:
        for index in range(count):
            content_store.result(db, cid, tid, 'output', str(index), 0, '中\n'.encode())
        result = assistant_output.saved_output(db, tid)
        assert result['content'] == '中\n' * count
        assert result['truncated'] is False
        assert result['partial'] is True

from sqlalchemy import event, select, func, insert
from app.chat import result_reader, service, final_answer
from app.chat.content_schema import segments, chunks
from app.chat.schema import events


def store_parts(db, cid, tid, count, text='x', stream='output'):
    for index in range(count):
        content_store.result(db, cid, tid, stream, f'part:{index}', 0, text.encode())


@pytest.mark.parametrize('count,expected', [(4096, False), (4097, True), (16384, True)])
def test_segment_window_query_bound(chat, count, expected):
    client, factory = chat; cid = create(client); tid = queued(factory, cid, 'running')
    with factory() as db:
        # Bulk metadata fixture keeps this scale test about reads, not writer overhead.
        from app.chat.content_schema import objects
        import hashlib
        oid = content_store.put(db,cid,'result',[b'x'])
        db.execute(insert(segments), [dict(**service.identity(),turn_id=tid,stream_id='output',
            source_event_id=f'{i:064x}',source_offset=0,sequence=i+1,object_id=oid) for i in range(count)])
        statements=[]
        def observe(conn,cursor,statement,parameters,context,many): statements.append(statement)
        event.listen(db.bind,'before_cursor_execute',observe)
        try: result=assistant_output.saved_output(db,tid)
        finally: event.remove(db.bind,'before_cursor_execute',observe)
        assert result['content']=='x'*min(count,4096)
        assert result['truncated']==expected
        if expected: assert result['truncation_reason']=='read_window'
        assert len(statements)<=20
        assert all(s.lstrip().upper().startswith('SELECT') for s in statements)


@pytest.mark.parametrize('count,reason', [(199999,None),(200000,None),(200001,'preview_limit')])
def test_exact_character_budget(chat,count,reason):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        text='中'*count
        for i in range(0,len(text),12000):
            content_store.result(db,cid,tid,'output',str(i),0,text[i:i+12000].encode())
        value=assistant_output.saved_output(db,tid)
        assert value['content']=='中'*min(count,200000)
        assert value.get('truncation_reason')==reason
        assert value['truncated']==bool(reason)


def test_result_page_bounded_and_authorized(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid);other=queued(factory,cid)
    with factory() as db:
        store_parts(db,cid,tid,520,'中\n')
        page=result_reader.results(db,'alice',tid)
        assert len(page['items'])==512 and page['next_cursor']
        tail=result_reader.results(db,'alice',tid,cursor=page['next_cursor'])
        assert len(tail['items'])==8 and tail['next_cursor'] is None
        assert ''.join(x['text'] for x in page['items']+tail['items'])=='中\n'*520
        with pytest.raises(service.ChatError):result_reader.results(db,'bob',tid)
        with pytest.raises(service.ChatError):result_reader.results(db,'alice',other,cursor=page['next_cursor'])


def test_corrupt_payload_not_hidden(chat):
    from sqlalchemy import update
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        store_parts(db,cid,tid,1)
        oid=db.scalar(select(segments.c.object_id).where(segments.c.turn_id==tid))
        db.execute(update(chunks).where(chunks.c.object_id==oid).values(payload=b'y'))
        assert assistant_output.saved_output(db,tid)['truncation_reason']=='invalid_payload'
        with pytest.raises(service.ChatError):result_reader.results(db,'alice',tid)


@pytest.mark.parametrize('payload,reason', [('{}','history_gap'), ('not-json','invalid_payload')])
def test_legacy_gap_and_invalid_payload(chat,payload,reason):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=2,
            source_id='legacy',event_type='execution.output',payload=payload))
        assert assistant_output.saved_output(db,tid)['truncation_reason']==reason
        with pytest.raises(service.ChatError,match='未保存可分页正文'):
            result_reader.results(db,'alice',tid)


def test_complete_stored_message_not_replaced_by_limited_preview(chat):
    from test_chat_final_answer import publish
    from app.chat.schema import messages
    client,factory=chat;cid=create(client);tid=queued(factory,cid,'completed')
    with factory() as db:
        publish(db,cid,tid,'large',['x'*12000]*18)
        assistant_output.persist_output(db,tid,'x'*216000)
        db.commit()
        rows=assistant_output.message_page(db,cid,1,20)
        answer=next(r for r in rows if r['role']=='assistant')
        assert len(answer['content'])==216000
        assert answer['output_truncation_reason']=='preview_limit'
        assistant_output.persist_output(db,tid)
        assert len(db.scalar(select(messages.c.content).where(messages.c.turn_id==tid)))==216000

@pytest.mark.parametrize('size',[262143,262144,262145])
def test_page_byte_boundary_and_read_only(chat,size):
    from app.chat.output_window import read_batch
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        content_store.result(db,cid,tid,'output','first',0,b'x'*min(size,262144))
        if size>262144:content_store.result(db,cid,tid,'output','second',0,b'y')
        items,more,used=read_batch(db,tid,'output')
        assert used==min(size,262144) and more==(size>262144)
        assert sum(x['byte_count'] for x in items)==used
        if more:
            tail,more,used=read_batch(db,tid,'output',items[-1]['sequence'])
            assert tail[0]['text']=='y' and not more

@pytest.mark.parametrize('state',['running','completed','failed','stopped'])
def test_http_projection_state_and_no_replay(chat,state):
    from app.chat.schema import turns,messages
    client,factory=chat;cid=create(client);tid=queued(factory,cid,state)
    with factory() as db:
        store_parts(db,cid,tid,22,'中文\n')
        db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=1,
            source_id='seen',event_type='execution.output',payload='{}'));db.commit()
    for _ in range(2):
        response=client.get(f'/api/v1/chat/conversations/{cid}/messages')
        assert response.status_code==200
        row=response.json()['data']['items'][0]
        assert row['content']=='中文\n'*22 and not row['output_truncated']
    with factory() as db:
        assert db.scalar(select(turns.c.status).where(turns.c.id==tid))==state
        assert db.scalar(select(func.count()).select_from(messages))==0
        assert db.scalar(select(func.count()).select_from(segments))==22

@pytest.mark.parametrize('width',[1,2,20,21,294])
def test_same_text_independent_of_delta_width(chat,width):
    client,factory=chat;cid=create(client);tid=queued(factory,cid,'running')
    text='中文\n'*98
    with factory() as db:
        for offset in range(0,len(text),width):
            content_store.result(db,cid,tid,'output',str(offset),0,text[offset:offset+width].encode())
        value=assistant_output.saved_output(db,tid)
        assert value['content']==text and not value['truncated']
