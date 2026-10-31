import io
import json
import queue
import threading
import time
from collections import deque
from types import SimpleNamespace
import pytest
from sqlalchemy import select, update, text
from test_chat import chat, create, queued
from app.chat import service
from app.chat.schema import turns, conversations
from app.chat.question_schema import questions
from app.chat.questions import create as create_question, submit, list_questions, normalize_questions
from app.chat.question_bridge import QuestionBridge
from app.chat.app_server import AppServer, ExecutorError
from app.api.v1.admin_auth import require_session_user
from app.main import app

RAW = [{'id': 'choice', 'header': '验证入口', 'question': '选择验证方式', 'options': [
    {'label': '隔离环境（推荐）', 'description': '合成业务数据'}, {'label': '暂缓', 'description': '保留阻塞'}]}]


def setup_question(chat):
    client, factory = chat
    cid = create(client); tid = queued(factory, cid, 'running')
    token = {'turn_id': tid, 'conversation_id': cid, 'worker_id': 'question-test', 'generation': 0}
    with factory() as db:
        db.execute(update(turns).where(turns.c.id == tid).values(worker_id=token['worker_id'], executor_turn_id='executor-turn'))
        db.execute(update(conversations).where(conversations.c.id == cid).values(thread_id='thread'))
        db.commit()
    params = {'threadId': 'thread', 'turnId': 'executor-turn', 'questions': RAW}
    return client, factory, token, params


def payload(key='answer-one', option='0'):
    return {'version': 1, 'idempotency_key': key, 'answers': {'choice': {'option_id': option, 'text': 'synthetic note'}}}


def test_api_answers_idempotent_authorized_and_no_new_turn(chat):
    client, factory, token, params = setup_question(chat)
    with factory() as db: row = create_question(db, token, params, 'request-one')
    path = f"/api/v1/chat/turns/{token['turn_id']}/questions"
    assert client.get(path).json()['data']['items'][0]['status'] == 'pending'
    answer_path = path + '/' + row['id'] + '/answers'
    response = client.post(answer_path, json=payload())
    assert response.status_code == 200, response.text
    assert response.json()['data']['status'] == 'answer_received'
    assert client.post(answer_path, json=payload()).status_code == 200
    assert client.post(answer_path, json=payload('different')).status_code == 409
    with factory() as db:
        assert len(list(db.scalars(select(turns.c.id)))) == 1
        assert db.scalar(select(conversations.c.active_turn_id)) == token['turn_id']
    app.dependency_overrides[require_session_user] = lambda: {'id': 'bob'}
    assert client.get(path).status_code == 404
    assert client.post(answer_path, json=payload()).status_code == 404


@pytest.mark.parametrize('state', ['stopping', 'stopped', 'unknown', 'completed'])
def test_late_answers_do_not_wake_finished_or_unknown_turn(chat, state):
    client, factory, token, params = setup_question(chat)
    with factory() as db:
        row = create_question(db, token, params, 5)
        db.execute(update(turns).where(turns.c.id == token['turn_id']).values(status=state)); db.commit()
    response = client.post(f"/api/v1/chat/turns/{token['turn_id']}/questions/{row['id']}/answers", json=payload())
    assert response.status_code == 409
    with factory() as db: assert db.scalar(select(questions.c.answer_json)) is None


def test_invalid_answer_expiration_and_revocation(chat):
    client, factory, token, params = setup_question(chat)
    with factory() as db: row = create_question(db, token, params, 5)
    path = f"/api/v1/chat/turns/{token['turn_id']}/questions/{row['id']}/answers"
    assert client.post(path, json=payload(option='bad')).status_code == 422
    bad = payload(); bad['answers']['choice']['text'] = 'x' * 4001
    assert client.post(path, json=bad).status_code == 422
    with factory() as db:
        db.execute(update(questions).values(expires_at='2000-01-01T00:00:00+00:00')); db.commit()
    assert client.post(path, json=payload()).status_code == 409
    with factory() as db:
        db.execute(text("UPDATE admin_users SET status='停用' WHERE id='alice'")); db.commit()
    assert client.post(path, json=payload()).status_code == 403


def test_refresh_does_not_duplicate_or_expose_answer(chat):
    client, factory, token, params = setup_question(chat)
    with factory() as db:
        row = create_question(db, token, params, 'same')
        assert create_question(db, token, params, 'same')['id'] == row['id']
        result = submit(db, 'alice', token['turn_id'], row['id'], 1, 'key', payload()['answers'])
        assert 'answer_json' not in result
        read = list_questions(db, 'alice', token['turn_id'])
        assert len(read['items']) == 1
        assert read['items'][0]['status'] == 'answer_received'
        assert 'synthetic note' not in json.dumps(read)


@pytest.mark.parametrize('phase', ['rpc', 'event'])
def test_bridge_consumes_api_answer_in_same_protocol_request(chat, phase):
    client, factory, token, params = setup_question(chat)
    server = object.__new__(AppServer)
    server.seq = 0; server.timeout = 3; server.failure = None
    from app.chat.protocol_buffer import ByteQueue
    server.incoming = ByteQueue(); server.pending = deque()
    sent = []; server._send = sent.append
    server.question_handler = QuestionBridge(factory, token, server)
    frame = {'id': 'server-request', 'method': 'item/tool/requestUserInput', 'params': params}
    server.incoming.put(frame)
    server.incoming.put({'id': 1, 'result': {'turn': {'id': 'executor-turn'}}})
    result = {}; errors = []
    def run():
        try: result['value'] = server.rpc('turn/start', {}) if phase == 'rpc' else server.event()
        except Exception as exc: errors.append(exc)
    thread = threading.Thread(target=run); thread.start()
    try:
        deadline = time.monotonic() + 4
        q = None
        while time.monotonic() < deadline:
            with factory() as db: q = db.execute(select(questions)).mappings().first()
            if q: break
            time.sleep(.02)
        assert q
        response = client.post(f"/api/v1/chat/turns/{token['turn_id']}/questions/{q['id']}/answers", json=payload())
        assert response.status_code == 200, response.text
        thread.join(4)
        assert not thread.is_alive() and not errors, errors
        wire = [v for v in sent if v.get('id') == 'server-request']
        assert wire == [{'id': 'server-request', 'result': {'answers': {'choice': {'answers': ['隔离环境（推荐）', 'synthetic note']}}}}]
        with factory() as db: assert db.scalar(select(questions.c.status)) == 'delivered'
        assert server._handle_question(frame) is True
        assert len([v for v in sent if v.get('id') == 'server-request']) == 1
    finally:
        server.failure = 'executor_disconnected'; thread.join(4)


def test_secret_questions_are_not_persisted():
    with pytest.raises(ValueError): normalize_questions([{**RAW[0], 'isSecret': True}])


def test_concurrent_answers_have_one_winner(chat):
    _, factory, token, params = setup_question(chat)
    with factory() as db: row = create_question(db, token, params, 'concurrent')
    barrier = threading.Barrier(2); outcomes = []
    def answer(key):
        with factory() as db:
            barrier.wait()
            try:
                submit(db, 'alice', token['turn_id'], row['id'], 1, key, payload()['answers'])
                outcomes.append('accepted')
            except service.ChatError as exc: outcomes.append(exc.status)
    threads = [threading.Thread(target=answer, args=(key,)) for key in ('one', 'two')]
    for thread in threads: thread.start()
    for thread in threads: thread.join(5)
    assert all(not thread.is_alive() for thread in threads)
    assert outcomes.count('accepted') == 1
    assert len(outcomes) == 2


@pytest.mark.parametrize('failure', ['disconnect', 'revoked', 'stopped', 'write_uncertain', 'ended'])
def test_bridge_failure_never_replays_answer(chat, failure):
    client, factory, token, params = setup_question(chat)
    from app.chat.protocol_buffer import ByteQueue
    server = object.__new__(AppServer); server.seq = 0; server.timeout = 2; server.failure = None
    server.incoming = ByteQueue(); server.pending = deque(); sent=[]; server._send=sent.append
    bridge = QuestionBridge(factory, token, server)
    errors=[]
    def run():
        try: bridge({'id':'request','method':'item/tool/requestUserInput','params':params})
        except Exception as exc: errors.append(type(exc).__name__)
    thread=threading.Thread(target=run);thread.start()
    try:
        q=None;deadline=time.monotonic()+4
        while time.monotonic()<deadline:
            with factory() as db:q=db.execute(select(questions)).mappings().first()
            if q:break
            time.sleep(.02)
        assert q
        if failure=='disconnect':server.failure='executor_disconnected'
        elif failure=='ended':server.incoming.put({'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'executor-turn'}}})
        elif failure=='write_uncertain':
            def uncertain(value):
                sent.append(value);raise ExecutorError('executor_disconnected')
            server._send=uncertain
            with factory() as db:submit(db,'alice',token['turn_id'],q['id'],1,'key',payload()['answers'])
        else:
            with factory() as db:
                if failure=='revoked':db.execute(text("UPDATE admin_users SET status='停用' WHERE id='alice'"))
                else:db.execute(update(turns).where(turns.c.id==token['turn_id']).values(status='stopping'))
                db.commit()
        thread.join(5);assert not thread.is_alive() and errors
        with factory() as db:
            state=db.scalar(select(questions.c.status))
            assert state in ('cancelled','unrecoverable')
        assert len([v for v in sent if 'result' in v]) == (1 if failure=='write_uncertain' else 0)
    finally:server.failure='executor_disconnected';thread.join(4)


def test_question_observability_contains_no_answer(chat):
    _, factory, token, params=setup_question(chat)
    from app.chat.observability import trace
    from app.chat.schema import task_trace_spans
    with factory() as db:
        trace(db, token['turn_id'], 'running');db.commit()
        row=create_question(db,token,params,'observed')
        submit(db,'alice',token['turn_id'],row['id'],1,'key',payload()['answers'],'trusted-request')
        spans=list(db.execute(select(task_trace_spans)).mappings())
        raw=json.dumps([dict(x) for x in spans])
        assert 'synthetic note' not in raw and '选择验证方式' not in raw
        assert 'trusted-request' in raw and row['id'] in raw


def test_client_capability_is_persisted_and_defaults_closed(chat):
    client, factory = chat
    from app.chat.admission import enqueue
    from test_chat_local_execution import LIMITS
    first = create(client); second = create(client)
    with factory() as db:
        a = enqueue(db, 'alice', first, 'a', 'synthetic', {**LIMITS,'user_concurrency':3})
        b = enqueue(db, 'alice', second, 'b', 'synthetic', {**LIMITS,'user_concurrency':3,'space_concurrency':3}, question_capable=True)
        assert db.scalar(select(turns.c.question_capable).where(turns.c.id == a['id'])) == 0
        assert db.scalar(select(turns.c.question_capable).where(turns.c.id == b['id'])) == 1


def test_unknown_interactive_method_rejected_in_event_phase():
    server=object.__new__(AppServer);server.pending=deque([{'id':'x','method':'untrusted/method','params':{}}]);sent=[]
    server._send=sent.append
    with pytest.raises(ExecutorError,match='executor_interactive_request'):server.event()
    assert sent[0]['error']['code']==-32601


def test_history_deletion_removes_question_and_answer(chat, monkeypatch):
    _, factory, token, params=setup_question(chat)
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION', json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':60}))
    from app.chat.cleanup import delete_history
    with factory() as db:
        row=create_question(db,token,params,'delete')
        submit(db,'alice',token['turn_id'],row['id'],1,'key',payload()['answers'])
        db.execute(update(turns).where(turns.c.id==token['turn_id']).values(status='completed'))
        db.execute(update(conversations).where(conversations.c.id==token['conversation_id']).values(active_turn_id=None));db.commit()
        result=delete_history(db,'alice',token['conversation_id'])
        assert result['deleted']
        assert db.scalar(select(questions.c.id).where(questions.c.id==row['id'])) is None


def test_scope_downgrade_blocks_answer_delivery(chat, monkeypatch):
    _, factory, token, params=setup_question(chat)
    from app.chat.protocol_buffer import ByteQueue
    server=object.__new__(AppServer);server.failure=None;server.incoming=ByteQueue();server.pending=deque()
    server.write_scope='implementation_write';sent=[];server._send=sent.append
    monkeypatch.setattr('app.chat.policy.write_policy',lambda *args,**kwargs:{'write_scope':'read_only','reason_code':'analysis_object_read_only'})
    with pytest.raises(ExecutorError,match='write_permission_revoked'):
        QuestionBridge(factory,token,server)({'id':'r','method':'item/tool/requestUserInput','params':params})
    assert not sent
    with factory() as db:assert db.scalar(select(questions.c.status))=='unrecoverable'


def test_foreign_question_and_space_revocation(chat):
    client, factory, token, params=setup_question(chat)
    with factory() as db: row=create_question(db,token,params,'scope')
    other_cid=create(client);other_tid=queued(factory,other_cid,'running')
    assert client.post(f"/api/v1/chat/turns/{other_tid}/questions/{row['id']}/answers",json=payload()).status_code==404
    with factory() as db:
        db.execute(text("UPDATE admin_spaces SET status='DISABLED' WHERE id='space'"));db.commit()
    path=f"/api/v1/chat/turns/{token['turn_id']}/questions"
    assert client.get(path).status_code==403
    assert client.post(path+'/'+row['id']+'/answers',json=payload()).status_code==403
