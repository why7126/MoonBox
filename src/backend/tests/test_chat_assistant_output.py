import json

from sqlalchemy import select
from test_chat import chat, create
from test_chat_accounting import LIMITS
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.app_server import ExecutorError
from app.chat.execution import run_claim, reconcile_unknown
from app.chat.schema import turns, events, messages


class Peer:
    def __init__(self, disconnect):
        self.disconnect = disconnect

    def connect(self, _):
        return 'synthetic-thread'

    def start_turn(self, *_):
        self.items = [
            {'method': 'item/agentMessage/delta', 'params': {'threadId': 'synthetic-thread', 'turnId': 'synthetic-turn', 'delta': 'synthetic assistant output'}},
        ]
        if not self.disconnect:
            self.items.append({'method': 'turn/completed', 'params': {'threadId': 'synthetic-thread', 'turn': {'id': 'synthetic-turn', 'status': 'interrupted'}}})
        return 'synthetic-turn'

    def event(self, timeout):
        if self.items:
            return self.items.pop(0)
        raise ExecutorError('synthetic_disconnect')

    def read_turn(self, thread, turn):
        return {'id': turn, 'status': 'interrupted', 'items': []}

    def close(self):
        pass


def run_case(chat, tmp_path, disconnect):
    client, factory = chat
    cid = create(client)
    path = tmp_path.resolve() / cid
    path.mkdir()
    with factory() as db:
        row = enqueue(db, 'alice', cid, 'synthetic request', 'test', LIMITS)
        token = worker.claim(db, 'synthetic-worker')
    result = run_claim(factory, token, path, lambda _: Peer(disconnect), usage_grace_seconds=0)
    with factory() as db:
        status = db.scalar(select(turns.c.status).where(turns.c.id == row['id']))
        output_count = len(db.scalars(select(events.c.id).where(events.c.turn_id == row['id'], events.c.event_type == 'execution.output')).all())
        assistant_count = len(db.scalars(select(messages.c.id).where(messages.c.turn_id == row['id'], messages.c.role == 'assistant')).all())
    response = client.get(f'/api/v1/chat/conversations/{cid}/messages')
    assert response.status_code == 200
    api_assistant_count = sum(item['role'] == 'assistant' for item in response.json()['data']['items'])
    return row['id'], path, result, status, output_count, assistant_count, api_assistant_count


def test_synthetic_disconnect_and_reconcile(chat, tmp_path):
    tid, path, result, status, outputs, assistants, api_assistants = run_case(chat, tmp_path, True)
    assert (result, status, outputs, assistants, api_assistants) == ('unknown', 'unknown', 1, 1, 1)
    client, factory = chat
    assert reconcile_unknown(factory, tid, path, lambda _: Peer(True))
    assert not reconcile_unknown(factory, tid, path, lambda _: Peer(True))
    with factory() as db:
        status = db.scalar(select(turns.c.status).where(turns.c.id == tid))
        output_count = len(db.scalars(select(events.c.id).where(events.c.turn_id == tid, events.c.event_type == 'execution.output')).all())
        assistant_count = len(db.scalars(select(messages.c.id).where(messages.c.turn_id == tid, messages.c.role == 'assistant')).all())
        terminal_count = len(db.scalars(select(events.c.id).where(events.c.turn_id == tid, events.c.source_id == 'reconcile:terminal')).all())
    assert (status, output_count, assistant_count, terminal_count) == ('stopped', 1, 1, 1)
    print('SYNTHETIC_ABNORMAL', json.dumps({'before': {'status': result, 'output_events': outputs, 'assistant_messages': assistants, 'api_assistant_messages': api_assistants}, 'after_reconcile': {'status': status, 'output_events': output_count, 'assistant_messages': assistant_count, 'terminal_events': terminal_count}}, sort_keys=True))


def test_synthetic_normal_terminal_control(chat, tmp_path):
    tid, path, result, status, outputs, assistants, api_assistants = run_case(chat, tmp_path, False)
    assert (result, status, outputs, assistants, api_assistants) == ('stopped', 'stopped', 1, 1, 1)
    print('SYNTHETIC_CONTROL', json.dumps({'status': status, 'output_events': outputs, 'assistant_messages': assistants, 'api_assistant_messages': api_assistants}, sort_keys=True))


def test_historical_projection_pages_are_read_only_and_authorized(chat):
    from sqlalchemy import insert, update, func
    from app.chat import service
    from app.chat.schema import conversations
    from app.main import app
    from app.api.v1.admin_auth import require_session_user
    client, factory = chat
    cid = create(client)
    tids = []
    with factory() as db:
        for n in range(4):
            tid = 'historical-' + str(n); tids.append(tid)
            stamp = f'2026-10-01T00:00:0{n}Z'
            db.execute(insert(turns).values(id=tid,created_at=stamp,updated_at=stamp,conversation_id=cid,
                client_request_id=tid,status='stopped',prompt='synthetic',generation=0))
            for seq, item, text in [(1,'a','first'),(2,'a',' part'),(4,'b','second')]:
                db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=seq,source_id=str(seq),
                    event_type='execution.output',payload=json.dumps({'text':text,'item_id':item})))
        db.commit()
    items=[]
    for page in [1,2]:
        response=client.get(f'/api/v1/chat/conversations/{cid}/messages?page={page}&page_size=2')
        assert response.status_code == 200
        items += response.json()['data']['items']
    assert len(items) == 4 and len({r['id'] for r in items}) == 4
    assert {r['turn_id'] for r in items} == set(tids)
    assert all(r['content']=='first part\n\nsecond' and r['output_partial'] and r['output_truncated'] for r in items)
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(messages)) == 0
    app.dependency_overrides[require_session_user] = lambda:{'id':'bob'}
    assert client.get(f'/api/v1/chat/conversations/{cid}/messages').status_code == 404


def test_projection_bounds_and_final_snapshot(chat, monkeypatch):
    from sqlalchemy import insert, func
    from app.chat import service, assistant_output
    from test_chat import queued
    client,factory=chat;cid=create(client);tid=queued(factory,cid,'stopped')
    with factory() as db:
        for seq,kind,text in [(1,'execution.output','part'),(2,'execution.output','part'),(3,'execution.state','final')]:
            db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=seq,
                source_id='assistant:final:item' if seq==3 else str(seq),event_type=kind,payload=json.dumps({'text':text,'item_id':'a'})))
        db.commit()
        assert assistant_output.saved_output(db,tid)=={'content':'final','partial':False,'truncated':False}
        assistant_output.persist_output(db,tid)
        assistant_output.persist_output(db,tid)
        db.commit()
        assert db.scalar(select(func.count()).select_from(messages).where(messages.c.turn_id==tid))==1
        monkeypatch.setattr(assistant_output,'MAX_EVENTS',1)
        assert assistant_output.saved_output(db,tid)=={'content':'part','partial':True,'truncated':True,'truncation_reason':'read_window'}
    data=client.get(f'/api/v1/chat/conversations/{cid}/messages').json()['data']['items']
    assert len(data)==1 and data[0]['content']=='final'


def test_no_output_has_no_fabricated_message(chat):
    from test_chat import queued
    client,factory=chat;cid=create(client);queued(factory,cid,'failed')
    assert client.get(f'/api/v1/chat/conversations/{cid}/messages').json()['data']['items']==[]


import pytest

@pytest.mark.parametrize('external,expected', [('interrupted','stopped'),('failed','failed'),('completed','completed')])
def test_authoritative_recovery_final_answer(chat, tmp_path, external, expected):
    tid,path,*_=run_case(chat,tmp_path,True)
    client,factory=chat
    class FinalPeer(Peer):
        def read_turn(self, thread, turn):
            return {'id':turn,'status':external,'items':[{'id':'answer','type':'agentMessage','phase':'final_answer','text':'synthetic final answer'}]}
    assert reconcile_unknown(factory,tid,path,lambda _:FinalPeer(True))
    assert not reconcile_unknown(factory,tid,path,lambda _:FinalPeer(True))
    data=client.get(f'/api/v1/chat/conversations/{path.name}/messages').json()['data']['items']
    answers=[x for x in data if x['role']=='assistant']
    assert len(answers)==1 and answers[0]['content']=='synthetic final answer'
    assert answers[0]['output_partial'] is (expected != 'completed')
    with factory() as db:
        assert db.scalar(select(turns.c.status).where(turns.c.id==tid))==expected


def test_message_write_failure_still_preserves_unknown_and_read_projection(chat,tmp_path,monkeypatch):
    from app.chat import execution
    def failure(*args,**kwargs): raise RuntimeError('synthetic message failure')
    monkeypatch.setattr(execution,'persist_output',failure)
    tid,path,result,status,outputs,assistants,api_assistants=run_case(chat,tmp_path,True)
    assert (result,status,outputs,assistants,api_assistants)==('unknown','unknown',1,0,1)
    client,_=chat
    answer=next(x for x in client.get(f'/api/v1/chat/conversations/{path.name}/messages').json()['data']['items'] if x['role']=='assistant')
    assert answer['output_source']=='events' and answer['output_partial']


def test_stale_worker_cannot_materialize_output(chat,tmp_path):
    from app.chat.execution import mark_unknown
    from sqlalchemy import update,func
    tid,path,*_=run_case(chat,tmp_path,True)
    _,factory=chat
    with factory() as db:
        before=db.scalar(select(messages.c.content).where(messages.c.turn_id==tid,messages.c.role=='assistant'))
        db.execute(update(turns).where(turns.c.id==tid).values(generation=99,status='running'));db.commit()
    mark_unknown(factory,{'turn_id':tid,'worker_id':'synthetic-worker','generation':1},'stale')
    with factory() as db:
        assert db.scalar(select(turns.c.status).where(turns.c.id==tid))=='running'
        assert db.scalar(select(messages.c.content).where(messages.c.turn_id==tid,messages.c.role=='assistant'))==before


@pytest.mark.parametrize('has_delta', [True, False])
def test_normal_final_snapshot_replaces_commentary(chat,tmp_path,has_delta):
    client,factory=chat;cid=create(client);path=tmp_path/cid;path.mkdir()
    class FinalPeer(Peer):
        def start_turn(self,*args):
            super().start_turn(*args)
            delta=self.items[0]
            final={'method':'item/completed','params':{'threadId':'synthetic-thread','turnId':'synthetic-turn',
                'item':{'id':'answer','type':'agentMessage','phase':'final_answer','text':'final answer'}}}
            terminal={'method':'turn/completed','params':{'threadId':'synthetic-thread','turn':{'id':'synthetic-turn','status':'completed'}}}
            self.items=([delta] if has_delta else [])+[final,terminal]
            return 'synthetic-turn'
    with factory() as db:
        row=enqueue(db,'alice',cid,'synthetic','final',LIMITS);token=worker.claim(db,'w')
    assert run_claim(factory,token,path,lambda _:FinalPeer(False),usage_grace_seconds=0)=='completed'
    answers=[r for r in client.get(f'/api/v1/chat/conversations/{cid}/messages').json()['data']['items'] if r['role']=='assistant']
    assert len(answers)==1 and answers[0]['content']=='final answer' and not answers[0]['output_partial']


def test_concurrent_recovery_materializes_once(chat,tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from sqlalchemy import func
    tid,path,*_=run_case(chat,tmp_path,True)
    _,factory=chat
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(lambda _:reconcile_unknown(factory,tid,path,lambda _:Peer(True)),range(2)))
    assert sum(outcomes)==1
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(messages).where(messages.c.turn_id==tid,messages.c.role=='assistant'))==1


def test_character_bound_and_tool_payload_exclusion(chat,monkeypatch):
    from sqlalchemy import insert
    from app.chat import assistant_output,service
    from test_chat import queued
    client,factory=chat;cid=create(client);tid=queued(factory,cid,'unknown')
    monkeypatch.setattr(assistant_output,'MAX_CHARS',5)
    with factory() as db:
        for seq,kind,text in [(1,'execution.tool','tool text'),(2,'execution.output','123456')]:
            db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=seq,source_id=str(seq),event_type=kind,payload=json.dumps({'text':text})))
        db.commit()
    answer=client.get(f'/api/v1/chat/conversations/{cid}/messages').json()['data']['items'][0]
    assert answer['content']=='12345' and answer['output_truncated'] and answer['output_partial']
