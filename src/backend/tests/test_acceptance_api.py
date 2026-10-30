import json
from sqlalchemy import text
from test_chat import chat, create, queued
from app.main import app
from app.api.v1.admin_auth import require_session_user
from app.governance.scope import authorize
from app.verification.acceptance_state import AcceptanceState


def operation(chat,monkeypatch,tmp_path):
    client,factory=chat
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':'repo','space_id':'space','governance_root':str(tmp_path)}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','governance_root':str(tmp_path)}]))
    cid=create(client);tid=queued(factory,cid)
    with factory() as db:binding=authorize(db,'alice','space','repo').binding_revision
    return AcceptanceState(factory).create(actor='alice',space='space',repository='repo',conversation=cid,
        turn=tid,change='add-test',request_key='key',binding=binding,input_digest='a'*64,
        plan={'checks':[{'id':'AC-001','inputs':['src/app.py']}]})


def test_read_stop_and_optimistic_conflict(chat,monkeypatch,tmp_path):
    item=operation(chat,monkeypatch,tmp_path);client,factory=chat
    url='/api/v1/chat/acceptance-operations/'+item['id']
    assert client.get(url).json()['data']['status']=='queued'
    assert client.post(url+'/stop',json={'version':99}).status_code==409
    response=client.post(url+'/stop',json={'version':1})
    assert response.status_code==200,response.text
    assert response.json()['data']['cancel_requested']
    assert 'plan_json' not in response.json()['data']


def test_cross_actor_and_revoked_binding_denied(chat,monkeypatch,tmp_path):
    item=operation(chat,monkeypatch,tmp_path);client,factory=chat
    url='/api/v1/chat/acceptance-operations/'+item['id']
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    assert client.get(url).status_code==404
    assert client.post(url+'/stop',json={'version':1}).status_code==404
    app.dependency_overrides[require_session_user]=lambda:{'id':'alice'}
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES','[]')
    assert client.get(url).status_code==403


def test_create_rejects_unconfirmed_or_unbound_source(chat,monkeypatch,tmp_path):
    client,factory=chat
    cid=create(client);tid=queued(factory,cid)
    response=client.post('/api/v1/chat/acceptance-operations',json={
        'conversation_id':cid,'source_turn_id':tid,'change_id':'synthetic-change','client_request_id':'key'})
    assert response.status_code in {409,503}
    assert client.post('/api/v1/chat/acceptance-operations',json={
        'conversation_id':cid,'source_turn_id':tid,'change_id':'../../private','client_request_id':'key'}).status_code==422


def test_polling_does_not_emit_behavior_but_explicit_verify_does(chat,monkeypatch,tmp_path):
    from sqlalchemy import select
    from app.chat.schema import usage_events,task_traces
    item=operation(chat,monkeypatch,tmp_path);client,factory=chat
    url='/api/v1/chat/acceptance-operations/'+item['id']
    assert client.get(url,headers={'X-Chat-Client':'web'}).status_code==200
    with factory() as db:
        assert not db.execute(select(usage_events).where(usage_events.c.event_name.like('acceptance.%'))).all()
        assert db.execute(select(task_traces).where(task_traces.c.turn_id==item['id'])).first()
    headers={'X-Chat-Client':'web','X-Acceptance-Action':'verify','X-Behavior-Event-ID':'synthetic-verify'}
    assert client.get(url,headers=headers).status_code==200
    with factory() as db:
        rows=db.execute(select(usage_events).where(usage_events.c.event_name=='acceptance.verify')).mappings().all()
        assert len(rows)==1
        assert 'plan_json' not in str(rows) and 'password' not in str(rows)


def test_evidence_expiry_uses_result_timestamp_not_heartbeat(chat,monkeypatch,tmp_path):
    from sqlalchemy import update
    from app.verification.acceptance_schema import results
    item=operation(chat,monkeypatch,tmp_path);client,factory=chat;state=AcceptanceState(factory)
    token=state.claim(item['id'],'synthetic-worker')
    state.result(token,'AC-001','passed',evidence={'kind':'command','digest':'d'*64})
    state.advance(token,'ready');state.advance(token,'running');state.advance(token,'passed')
    state.cleanup(item['id'],released=True)
    assert state.get(item['id'])['ready']
    url='/api/v1/chat/acceptance-operations/'+item['id']+'/evidence'
    assert client.get(url).status_code==200
    with factory.begin() as db:
        db.execute(update(results).where(results.c.attempt_id==token['attempt_id']).values(updated_at='2000-01-01T00:00:00+00:00'))
    state.heartbeat(token)
    assert client.get(url).status_code==410
    assert not state.get(item['id'])['ready']


def test_read_does_not_present_old_template_as_current_ready(chat,monkeypatch,tmp_path):
    from types import SimpleNamespace
    item=operation(chat,monkeypatch,tmp_path);client,factory=chat;state=AcceptanceState(factory)
    token=state.claim(item['id'],'synthetic-worker')
    state.bind_template(token,'d'*64)
    state.result(token,'AC-001','passed',evidence={'kind':'command','digest':'e'*64})
    state.advance(token,'ready');state.advance(token,'running');state.advance(token,'passed')
    state.cleanup(item['id'],released=True)
    url='/api/v1/chat/acceptance-operations/'+item['id']
    before=state.get(item['id'])['version']
    monkeypatch.setattr('app.verification.acceptance_template.approved_template',lambda:SimpleNamespace(key='f'*64))
    view=client.get(url).json()['data']
    assert not view['ready'] and view['reason_code']=='template_changed'
    assert view['checks'][0]['evidence_available']
    assert state.get(item['id'])['version']==before
    monkeypatch.setattr('app.verification.acceptance_template.approved_template',lambda:SimpleNamespace(key='d'*64))
    assert client.get(url).json()['data']['ready']


def test_frozen_actor_is_rejected_by_background_authorization(chat,monkeypatch,tmp_path):
    import pytest
    from app.chat.service import ChatError, conversation
    from app.verification.acceptance_service import authorize as authorize_operation
    item=operation(chat,monkeypatch,tmp_path);_,factory=chat
    with factory() as db:
        db.execute(text("UPDATE admin_users SET status='已冻结' WHERE id='alice'"));db.commit()
        for check in (lambda:authorize(db,'alice','space','repo'),
                      lambda:conversation(db,'alice',item['conversation_id']),
                      lambda:authorize_operation(db,'alice',item['id'],write=True)):
            with pytest.raises(ChatError) as error:check()
            assert error.value.status==403
