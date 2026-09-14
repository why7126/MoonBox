import os
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert, select, text, update
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.chat import service, worker
from app.chat.schema import migrate, conversations, turns, events

@pytest.fixture
def chat(tmp_path,monkeypatch):
    engine=create_engine(os.environ.get('CHAT_TEST_DATABASE_URL',f'sqlite:///{tmp_path}/chat.db'))
    with engine.begin() as db:
        db.execute(text('CREATE TABLE admin_users (id VARCHAR(64) PRIMARY KEY)'))
        db.execute(text("CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, name VARCHAR(80) DEFAULT 'Test space', owner_id VARCHAR(64), status VARCHAR(24), deleted_at VARCHAR(32), expires_at VARCHAR(32))"))
        db.execute(text("CREATE TABLE admin_space_members (id VARCHAR(64) PRIMARY KEY, space_id VARCHAR(64), user_id VARCHAR(64), role VARCHAR(32) DEFAULT '查看者')"))
        db.execute(text("INSERT INTO admin_users (id) VALUES ('alice'),('bob')"))
        db.execute(text("INSERT INTO admin_spaces (id,owner_id,status) VALUES ('space','alice','ACTIVE')"))
    migrate(engine);migrate(engine)
    factory=sessionmaker(engine)
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES','[{"id":"repo","space_id":"space"}]')
    monkeypatch.setattr('app.chat.api.get_session_factory',lambda:factory)
    def dependency():
        with factory() as db:yield db
    app.dependency_overrides[get_db]=dependency
    app.dependency_overrides[require_session_user]=lambda:{'id':'alice'}
    client=TestClient(app,raise_server_exceptions=True)
    yield client,factory
    client.close()
    app.dependency_overrides.clear()
    # Dedicated disposable test DB only; never uses application DATABASE_URL.
    from app.chat.schema import CHAT_TABLES
    for table in reversed(CHAT_TABLES):table.drop(engine)
    with engine.begin() as db:
        for name in ['admin_space_members','admin_spaces','admin_users']:
            db.execute(text('DROP TABLE '+name))
    engine.dispose()

def create(client):
    response=client.post('/api/v1/chat/conversations',json={'space_id':'space','repository_id':'repo'})
    assert response.status_code==200,response.text
    return response.json()['data']['id']

def queued(factory,cid,status='queued'):
    tid=service.identity()
    with factory() as db:
        db.execute(insert(turns).values(**tid,conversation_id=cid,client_request_id=tid['id'],status=status,prompt='synthetic fixture',generation=0))
        db.execute(update(conversations).where(conversations.c.id==cid).values(active_turn_id=tid['id']))
        db.commit()
    return tid['id']

def test_crud_and_readiness(chat):
    client,factory=chat;cid=create(client)
    assert client.patch('/api/v1/chat/conversations/'+cid,json={'title':' renamed ','pinned':True}).json()['data']['title']=='renamed'
    response=client.get('/api/v1/chat/conversations',params={'space_id':'space','q':'renamed'})
    assert response.json()['data']['total']==1
    assert 'X-Request-ID' in response.headers
    assert client.post(f'/api/v1/chat/conversations/{cid}/turns',json={'client_request_id':'once','prompt':'hello'}).json()['code']==2505
    assert client.patch(f'/api/v1/chat/conversations/{cid}',json={'archived':True}).status_code==200
    assert client.delete(f'/api/v1/chat/conversations/{cid}').status_code==200
    assert client.get(f'/api/v1/chat/conversations/{cid}').status_code==404

def test_owner_and_revoked_space(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    for suffix in [f'conversations/{cid}',f'turns/{tid}',f'turns/{tid}/events',f'turns/{tid}/diff']:
        assert client.get('/api/v1/chat/'+suffix).status_code==404
    app.dependency_overrides[require_session_user]=lambda:{'id':'alice'}
    with factory() as db:db.execute(text("UPDATE admin_spaces SET status='FROZEN'"));db.commit()
    assert client.get(f'/api/v1/chat/turns/{tid}/events').status_code==403

def test_claim_fencing_terminal_and_replay(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        token=worker.claim(db,'worker-one');assert token
        assert worker.claim(db,'worker-two') is None
        assert not worker.record_event(db,{**token,'generation':99},'e1','execution.state',{'status':'running'})
        assert worker.record_event(db,token,'e1','execution.state',{'status':'running'})
        assert not worker.record_event(db,token,'e1','execution.state',{'status':'running'})
        assert worker.record_event(db,token,'e2','execution.state',{'status':'completed'},terminal='completed')
        assert not worker.record_event(db,token,'e3','execution.state',{'status':'running'})
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==cid)) is None
    stream=client.get(f'/api/v1/chat/turns/{tid}/events?after=1')
    assert 'id: 2' in stream.text and 'id: 1' not in stream.text
    assert stream.headers['content-type'].startswith('text/event-stream')

def test_restart_never_releases_unknown_lock(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        token=worker.claim(db,'worker-one')
        db.execute(update(turns).where(turns.c.id==tid).values(heartbeat_at=(datetime.now(timezone.utc)-timedelta(seconds=300)).isoformat(timespec='seconds')));db.commit()
        assert worker.mark_stale_unknown(db)==1
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==cid))==tid
        assert worker.claim(db,'worker-two') is None
        assert not worker.record_event(db,token,'late','execution.state',{},terminal='completed')
    assert client.post(f'/api/v1/chat/turns/{tid}/interrupt').json()['code']==2506
    assert client.delete(f'/api/v1/chat/conversations/{cid}').status_code==409

def test_stop_queued_and_running(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    assert client.post(f'/api/v1/chat/turns/{tid}/interrupt').json()['data']['status']=='stopped'
    tid=queued(factory,cid)
    with factory() as db:worker.claim(db,'worker-one')
    assert client.post(f'/api/v1/chat/turns/{tid}/interrupt').json()['data']['status']=='stopping'
    assert client.patch(f'/api/v1/chat/conversations/{cid}',json={'archived':True}).status_code==409

def test_request_id_conflict_and_validation(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:r=db.execute(select(turns).where(turns.c.id==tid)).mappings().one()
    url=f'/api/v1/chat/conversations/{cid}/turns'
    assert client.post(url,json={'client_request_id':r['client_request_id'],'prompt':r['prompt']}).json()['data']['id']==tid
    assert client.post(url,json={'client_request_id':r['client_request_id'],'prompt':'different'}).status_code==409
    assert client.patch(f'/api/v1/chat/conversations/{cid}',json={'title':'   '}).status_code==422
    assert client.patch(f'/api/v1/chat/conversations/{cid}',json={'archived':None}).status_code==422


def test_authentication_and_logs_have_no_prompt(chat):
    client,factory=chat
    app.dependency_overrides.pop(require_session_user)
    assert client.get('/api/v1/chat/conversations?space_id=space').status_code==401
    from app.chat.schema import audit
    with factory() as db:
        row=db.execute(select(audit)).mappings().one()
        assert row['status_code']==401
        assert row['route_template']=='/api/v1/chat/conversations'
        assert 'Authorization' not in str(row)


def test_space_expiry_is_time_aware(chat):
    client,factory=chat;cid=create(client)
    with factory() as db:
        db.execute(text('UPDATE admin_spaces SET expires_at=:expiry'),{'expiry':(datetime.now(timezone.utc)-timedelta(minutes=1)).isoformat()});db.commit()
    assert client.get(f'/api/v1/chat/conversations/{cid}').status_code==403


def test_two_workers_cannot_claim_same_turn(chat):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    client,factory=chat;cid=create(client);queued(factory,cid);barrier=Barrier(2)
    def attempt(name):
        with factory() as db:
            barrier.wait(timeout=5)
            return worker.claim(db,name)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(attempt,name) for name in ('worker-a','worker-b')]
        claims=[f.result(timeout=10) for f in futures]
    assert sum(token is not None for token in claims)==1


def test_space_catalog_filters_non_members(chat):
    client,factory=chat
    assert client.get('/api/v1/chat/spaces').json()['data']==[{'id':'space','name':'Test space'}]
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    assert client.get('/api/v1/chat/spaces').json()['data']==[]


def test_admission_reservation_idempotency_and_terminal_settlement(chat):
    from app.chat.admission import enqueue, settle
    from app.chat.schema import usage_accounts
    client, factory = chat
    cid = create(client)
    limits = dict(user_concurrency=1, space_concurrency=2, user_monthly_tokens=1000, space_monthly_tokens=2000,
                  user_storage_bytes=1000, space_storage_bytes=2000, turn_reserved_tokens=100, turn_reserved_bytes=200)
    with factory() as db:
        first = enqueue(db, 'alice', cid, 'same-request', 'synthetic input', limits)
        assert enqueue(db, 'alice', cid, 'same-request', 'synthetic input', limits)['id'] == first['id']
        with pytest.raises(service.ChatError): enqueue(db, 'alice', cid, 'different', 'input', limits)
        with pytest.raises(service.ChatError): settle(db, first['id'], 10, 20)
    cid2 = create(client)
    with factory() as db:
        with pytest.raises(service.ChatError) as error: enqueue(db, 'alice', cid2, 'other', 'input', limits)
        assert error.value.code == 2508
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id == cid2)) is None
    assert client.post(f"/api/v1/chat/turns/{first['id']}/interrupt").status_code == 200
    with factory() as db:
        # Queue cancellation now settles atomically; repeated settlement cannot double-release.
        assert not settle(db, first['id'], 0, 20)
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id == 'user:alice')) == 0
        assert enqueue(db, 'alice', cid2, 'other', 'input', limits)['status'] == 'queued'
    data = client.get(f'/api/v1/chat/conversations/{cid}/messages').json()['data']['items']
    assert data[0]['content'] == 'synthetic input'
    app.dependency_overrides[require_session_user] = lambda: {'id': 'bob'}
    assert client.get(f'/api/v1/chat/conversations/{cid}/messages').status_code == 404


def test_limits_are_explicit_and_fail_closed(monkeypatch):
    from app.chat.settings import execution_limits
    monkeypatch.delenv('MOONBOX_CHAT_LIMITS', raising=False)
    assert execution_limits() is None
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS', '{"user_concurrency":true}')
    assert execution_limits() is None


def test_concurrent_admission_returns_one_id(chat):
    from concurrent.futures import ThreadPoolExecutor
    from app.chat.admission import enqueue
    from app.chat.schema import reservations
    from sqlalchemy import func
    client, factory = chat; cid = create(client)
    limits = dict(user_concurrency=1, space_concurrency=2, user_monthly_tokens=1000, space_monthly_tokens=2000,
                  user_storage_bytes=1000, space_storage_bytes=2000, turn_reserved_tokens=100, turn_reserved_bytes=200)
    def submit():
        with factory() as db: return enqueue(db, 'alice', cid, 'concurrent', 'synthetic', limits)['id']
    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: submit(), range(2)))
    assert len(set(results)) == 1
    with factory() as db: assert db.scalar(select(func.count()).select_from(reservations)) == 1


def test_execution_persists_reply_diff_and_settles_confirmed_usage(chat,tmp_path):
    import json
    from app.chat.admission import enqueue
    from app.chat.execution import run_claim
    from app.chat.schema import workspace_baselines, reservations
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir();(path/'counter').write_text('0\n')
    limits=dict(user_concurrency=1,space_concurrency=2,user_monthly_tokens=10000,space_monthly_tokens=20000,
        user_storage_bytes=1000000,space_storage_bytes=2000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)
    class Peer:
        def connect(self,previous):return 'thread'
        def start_turn(self,thread,prompt):
            (path/'counter').write_text(prompt+'\n')
            self.events=[{'method':'item/completed','params':{'threadId':'thread','turnId':'run','item':{'id':'tool-one','type':'commandExecution','command':'echo synthetic; password=synthetic-secret','aggregatedOutput':'ok','exitCode':0,'durationMs':5}}}, {'method':'item/agentMessage/delta','params':{'threadId':'thread','turnId':'run','delta':'checking; done'}},
                {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'run','tokenUsage':{'total':{'totalTokens':int(prompt)*10}}}},
                {'method':'item/completed','params':{'threadId':'thread','turnId':'run','item':{'id':'final','type':'agentMessage','phase':'final_answer','text':'done'}}},
                {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'completed'}}}]
            return 'run'
        def event(self,timeout):return self.events.pop(0) if self.events else None
        def close(self):pass
    results=[]
    for value in ['1','2']:
        with factory() as db:
            turn=enqueue(db,'alice',cid,'request-'+value,value,limits);token=worker.claim(db,'executor')
        assert run_claim(factory,token,path,lambda _:Peer())=='completed'
        result=client.get(f"/api/v1/chat/turns/{turn['id']}/diff").json()['data'];results.append(result)
        with factory() as db:
            assert db.scalar(select(reservations.c.status).where(reservations.c.turn_id==turn['id']))=='settled'
    with factory() as db:
        stored=list(db.execute(select(events.c.event_type,events.c.payload)).all())
        assert any(item[0]=='execution.tool' for item in stored)
        assert 'echo synthetic' in str(stored)
        assert 'synthetic-secret' not in str(stored)
        tool = json.loads(next(item[1] for item in stored if item[0]=='execution.tool'))
        assert tool['result']=='ok' and tool['exit_code']==0 and tool['duration_ms']==5
    assert '-1\n+2\n' in results[1]['files'][0]['patch']
    assert '-0\n+2\n' in results[1]['cumulative_files'][0]['patch']
    with factory() as db:assert db.scalar(select(workspace_baselines.c.token_total))==20


def test_execution_disconnect_keeps_unknown_lock_and_reservation(chat,tmp_path):
    from app.chat.admission import enqueue
    from app.chat.execution import run_claim
    from app.chat.app_server import ExecutorError
    from app.chat.schema import reservations
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    limits=dict(user_concurrency=1,space_concurrency=2,user_monthly_tokens=10000,space_monthly_tokens=20000,
        user_storage_bytes=1000000,space_storage_bytes=2000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)
    class Peer:
        def connect(self,previous):return 'thread'
        def start_turn(self,*_):raise ExecutorError('executor_disconnected')
        def close(self):pass
    with factory() as db:turn=enqueue(db,'alice',cid,'request','synthetic',limits);token=worker.claim(db,'executor')
    assert run_claim(factory,token,path,lambda _:Peer())=='unknown'
    with factory() as db:
        assert db.scalar(select(conversations.c.active_turn_id))==turn['id']
        assert db.scalar(select(reservations.c.status))=='reserved'


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_PROBE')!='1',reason='Explicit controlled local Codex probe only')
def test_live_app_server_two_rounds_through_persistent_runner(chat,tmp_path,governance):
    import shutil
    from pathlib import Path
    from app.chat.admission import enqueue
    from app.chat.execution import run_claim
    from app.chat.app_server import AppServer
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    allow_governed_write(client,cid,governance)
    import subprocess
    subprocess.run(['git','init','-q',str(path)],check=True)
    (path/'counter.txt').write_text('0\n')
    limits=dict(user_concurrency=1,space_concurrency=1,user_monthly_tokens=100000,space_monthly_tokens=100000,
        user_storage_bytes=10000000,space_storage_bytes=10000000,turn_reserved_tokens=40000,turn_reserved_bytes=4000000)
    result=[]
    for value in ['1','2']:
        prompt=f'Bounded integration test. Set counter.txt to exactly {value} followed by a newline. Do not change other files or commit. Reply only done.'
        with factory() as db:
            turn=enqueue(db,'alice',cid,'live-'+value,prompt,limits);token=worker.claim(db,'controlled-local-probe')
        state=run_claim(factory,token,path,lambda directory:AppServer(shutil.which('codex'),directory,Path.home()/'.codex',home=Path.home(),write=True),max_seconds=180)
        with factory() as db:error=db.scalar(select(turns.c.error_code).where(turns.c.id==turn['id']))
        assert state=='completed',error
        assert (path/'counter.txt').read_text()==value+'\n'
        diff=client.get(f"/api/v1/chat/turns/{turn['id']}/diff").json()['data']
        result.append({'round':int(value),'status':state,'expected_file_content':True,'diff_files':len(diff['files'])})
    assert '-1\n+2\n' in diff['files'][0]['patch']
    assert '-0\n+2\n' in diff['cumulative_files'][0]['patch']
    Path('/tmp/moonbox-chat-runner-probe.json').write_text(__import__('json').dumps({'rounds':result,'thread_resume_after_process_restart':True,'auth_source':'existing local login, not platform credential','platform_isolation_validated':False},indent=2))


def test_incremental_indexes_are_present(chat):
    from sqlalchemy import inspect
    client,factory=chat
    with factory() as db:
        index=next(index for index in turns.indexes if index.name=='ix_chat_turn_conversation_time')
        index.drop(db.bind)
        migrate(db.bind)
        names={row['name'] for row in inspect(db.bind).get_indexes('chat_turns')}
        assert 'ix_chat_turn_conversation_time' in names

@pytest.fixture
def governance(tmp_path,monkeypatch):
    import json
    root=(tmp_path/'governance').resolve();root.mkdir()
    entries=[]
    for number in range(1,4):
        oid=f'REQ-900{number}-synthetic';relative=f'issues/requirements/review/{oid}'
        directory=root/relative;directory.mkdir(parents=True)
        (directory/'requirement.md').write_text(f'synthetic original {number}')
        entries.append({'id':oid,'title':f'Synthetic object {number}','path':relative})
    (root/'issues/requirements/_registry.yaml').write_text(json.dumps({'entries':entries}))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','governance_root':str(root)}]))
    return root,entries


def test_relations_snapshots_and_revocation(chat,governance):
    from app.chat.relations import capture_for_turn
    from app.chat.schema import object_access
    client,factory=chat;root,entries=governance;cid=create(client)
    url=f'/api/v1/chat/conversations/{cid}'
    primary=entries[0]['id'];reference=entries[1]['id']
    assert len(client.get(url+'/objects').json()['data']['items'])==3
    assert client.put(url+'/relations',json={'primary':[primary,reference]}).status_code==422
    assert client.put(url+'/relations',json={'primary':primary,'references':['REQ-9001']}).status_code==409
    assert client.put(url+'/relations',json={'primary':primary,'references':[reference]}).status_code==200
    assert client.get('/api/v1/chat/conversations',params={'space_id':'space','q':primary}).json()['data']['total']==1
    tid=queued(factory,cid)
    with factory() as db:
        capture_for_turn(db,'alice',service.conversation(db,'alice',cid),tid);db.commit()
    before=client.get(f'/api/v1/chat/turns/{tid}/context').json()['data']
    (root/entries[0]['path']/'requirement.md').write_text('changed source after enqueue')
    assert client.get(f'/api/v1/chat/turns/{tid}/context').json()['data']==before
    assert client.put(url+'/relations',json={'primary':None,'references':[]}).status_code==409
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id=primary,user_id='alice',can_read=0));db.commit()
    for path in [url,url+'/relations',url+'/messages',f'/api/v1/chat/turns/{tid}/events',f'/api/v1/chat/turns/{tid}/diff',f'/api/v1/chat/turns/{tid}/context']:
        assert client.get(path).status_code==403,path
    assert client.get('/api/v1/chat/conversations',params={'space_id':'space'}).json()['data']['total']==0
    assert client.post(url+'/turns',json={'client_request_id':'revoked','prompt':'hello'}).status_code==403


def test_relation_scope_links_and_context_bounds(chat,governance,tmp_path):
    from app.chat.relations import capture_for_turn
    from app.chat.schema import snapshots
    client,factory=chat;root,entries=governance;cid=create(client);url=f'/api/v1/chat/conversations/{cid}'
    source=root/entries[0]['path']/'requirement.md';source.unlink()
    outside=tmp_path/'outside.md';outside.write_text('must not be included');source.symlink_to(outside)
    assert client.put(url+'/relations',json={'primary':entries[0]['id']}).status_code==403
    source.unlink();source.write_text('中文'*50000)
    for entry in entries[1:]: (root/entry['path']/'requirement.md').write_text('中文'*50000)
    assert client.put(url+'/relations',json={'primary':entries[0]['id'],'references':[e['id'] for e in entries[1:]]}).status_code==200
    tid=queued(factory,cid)
    with factory() as db:
        items=capture_for_turn(db,'alice',service.conversation(db,'alice',cid),tid);db.commit()
        assert sum(len(i['content'].encode()) for i in items)<=48000
        assert all(i['truncated'] for i in items)
        assert len(list(db.scalars(select(snapshots.c.id))))==3
    assert client.get(url+'/objects',params={'q':'nonexistent'}).json()['data']['items']==[]


def test_retry_reuses_snapshot_and_queued_stop_settles(chat,governance):
    from app.chat.admission import enqueue
    from app.chat.schema import reservations,usage_accounts
    client,factory=chat;root,entries=governance;cid=create(client)
    url=f'/api/v1/chat/conversations/{cid}';oid=entries[0]['id']
    assert client.put(url+'/relations',json={'primary':oid}).status_code==200
    limits=dict(user_concurrency=1,space_concurrency=2,user_monthly_tokens=10000,space_monthly_tokens=20000,user_storage_bytes=1000000,space_storage_bytes=2000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)
    with factory() as db: original=enqueue(db,'alice',cid,'first','synthetic',limits)
    assert client.post(f"/api/v1/chat/turns/{original['id']}/retries",json={'client_request_id':'retry'}).status_code==409
    assert client.post(f"/api/v1/chat/turns/{original['id']}/interrupt").json()['data']['status']=='stopped'
    with factory() as db:
        assert db.scalar(select(reservations.c.status))=='settled'
        assert all(value==0 for value in db.scalars(select(usage_accounts.c.active_runs)))
    (root/entries[0]['path']/'requirement.md').write_text('source changed')
    assert client.put(url+'/relations',json={'primary':None}).status_code==200
    with factory() as db: retried=enqueue(db,'alice',cid,'retry','synthetic',limits,retry_of=original['id'])
    assert retried['retry_of']==original['id']
    context=lambda tid:client.get(f'/api/v1/chat/turns/{tid}/context').json()['data']
    assert context(retried['id'])==context(original['id'])
    assert context(retried['id'])[0]['content']=='synthetic original 1'
    with factory() as db:assert enqueue(db,'alice',cid,'retry','synthetic',limits,retry_of=original['id'])['id']==retried['id']


def test_repository_revocation_blocks_history_and_executor(chat,monkeypatch):
    from app.chat.execution import owned
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db: token=worker.claim(db,'worker')
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES','[]')
    assert client.get(f'/api/v1/chat/conversations/{cid}').status_code==403
    assert client.get('/api/v1/chat/conversations',params={'space_id':'space'}).json()['data']['total']==0
    with factory() as db:
        with pytest.raises(service.ChatError):owned(db,token)


def allow_governed_write(client,cid,governance):
    import json
    root,entries=governance;oid=entries[0]['id'];change='synthetic-change';sprint='sprint-999'
    entries[0].update(status='in_sprint',related_change=change,iteration=sprint)
    (root/'issues/requirements/_registry.yaml').write_text(json.dumps({'entries':entries}))
    folder=root/'openspec/changes'/change;folder.mkdir(parents=True,exist_ok=True)
    (folder/'trace.md').write_text(f'---\nstatus: in_progress\nrequirement: {oid}\nsprint: {sprint}\n---\n')
    folder=root/'iterations/change'/sprint;folder.mkdir(parents=True,exist_ok=True)
    (folder/'sprint.yaml').write_text(json.dumps({'changes':[change],'requirements':[oid]}))
    assert client.put(f'/api/v1/chat/conversations/{cid}/relations',json={'primary':oid}).status_code==200


def test_write_policy_requires_current_role_and_sprint_change(chat,governance):
    from app.chat.policy import write_allowed
    client,factory=chat;cid=create(client)
    with factory() as db:assert not write_allowed(db,'alice',service.conversation(db,'alice',cid))
    allow_governed_write(client,cid,governance)
    with factory() as db:
        parent=service.conversation(db,'alice',cid)
        assert write_allowed(db,'alice',parent)
        db.execute(text("INSERT INTO admin_space_members (id,space_id,user_id,role) VALUES ('m','space','bob','查看者')"));db.commit()
        assert not write_allowed(db,'bob',parent)
        db.execute(text("UPDATE admin_space_members SET role='编辑者'"));db.commit()
        assert write_allowed(db,'bob',parent)
    root,_=governance
    (root/'iterations/change/sprint-999/sprint.yaml').write_text('changes: []\nrequirements: []')
    with factory() as db:assert not write_allowed(db,'alice',parent)


def test_observability_trusted_ids_and_retention(chat):
    from app.chat.schema import usage_events,task_traces,task_trace_spans,audit
    from app.chat.observability import trace,prune
    client,factory=chat;cid=create(client)
    response=client.post(f'/api/v1/chat/conversations/{cid}/turns',headers={'X-Chat-Client':'web','X-Request-ID':'forged'},json={'client_request_id':'forged','prompt':'private synthetic prompt'})
    assert response.headers['X-Request-ID']!='forged'
    with factory() as db:
        row=db.execute(select(usage_events)).mappings().one()
        assert row['parent_request_id']==response.headers['X-Request-ID']
        assert row['event_name']=='chat.send' and row['result']=='failure' and row['properties']=='{}'
        trace(db,'synthetic-turn','queued',actor='alice');trace(db,'synthetic-turn','completed');db.commit()
        task=db.execute(select(task_traces)).mappings().one()
        assert task['parent_request_id'] is None and task['status']=='completed'
        assert len(list(db.scalars(select(task_trace_spans.c.id))))==2
        old=(datetime.now(timezone.utc)-timedelta(days=200)).isoformat(timespec='seconds')
        db.execute(update(task_traces).values(finished_at=old));db.execute(update(usage_events).values(created_at=old));db.execute(update(audit).values(created_at=old));db.commit();prune(db)
        assert db.scalar(select(task_traces.c.id)) is None
        assert db.scalar(select(task_trace_spans.c.id)) is None
        assert db.scalar(select(usage_events.c.id)) is None
        assert service.conversation(db,'alice',cid)['id']==cid


def test_trace_failure_does_not_rollback_business(chat,monkeypatch):
    from app.chat.observability import trace
    client,factory=chat;cid=create(client)
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id==cid).values(title='kept'))
        original=db.execute
        def execute(statement,*args,**kwargs):
            if 'task_traces' in str(statement):raise RuntimeError('synthetic instrumentation failure')
            return original(statement,*args,**kwargs)
        monkeypatch.setattr(db,'execute',execute)
        trace(db,'synthetic-turn','queued');db.commit()
    with factory() as db:assert service.conversation(db,'alice',cid)['title']=='kept'


def test_history_deletion_checks_current_code_and_preserves_audit(chat,governance,tmp_path,monkeypatch):
    import json,subprocess
    from app.chat.schema import messages,audit,cleanup_jobs
    client,factory=chat;root,_=governance;cid=create(client)
    workspace_root=(tmp_path/'workspaces').resolve();workspace_root.mkdir();workspace=workspace_root/cid;workspace.mkdir()
    subprocess.run(['git','init','-q',str(workspace)],check=True)
    source=workspace/'code.txt';source.write_text('code remains')
    tid=queued(factory,cid)
    assert client.post(f'/api/v1/chat/turns/{tid}/interrupt').status_code==200
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id==cid).values(workspace_id=cid,thread_id='synthetic-thread'))
        db.execute(insert(messages).values(**service.identity(),turn_id=tid,role='assistant',content='private synthetic reply'));db.commit()
    url=f'/api/v1/chat/conversations/{cid}'
    assert client.get(url+'/deletion-check').json()['data']['allowed'] is False
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION',json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','governance_root':str(root),'workspace_root':str(workspace_root)}]))
    assert client.get(url+'/deletion-check').json()['data']['allowed'] is False
    # The test owner explicitly handles code. The application never commits automatically.
    subprocess.run(['git','-C',str(workspace),'add','code.txt'],check=True)
    subprocess.run(['git','-C',str(workspace),'-c','user.name=Synthetic','-c','user.email=synthetic@example.invalid','commit','-qm','synthetic code handling'],check=True)
    verdict=client.get(url+'/deletion-check').json()['data'];assert verdict['allowed']
    assert client.delete(url,params={'expected_hash':'0'*64}).status_code==409
    deleted=client.delete(url,params={'expected_hash':verdict['workspace_hash']})
    assert deleted.status_code==200,deleted.text
    assert deleted.json()['data']['executor_status']=='pending'
    assert source.read_text()=='code remains'
    assert client.get(url).status_code==404
    with factory() as db:
        assert db.scalar(select(messages.c.id).where(messages.c.turn_id==tid)) is None
        assert db.scalar(select(audit.c.id)) is not None
        assert db.scalar(select(cleanup_jobs.c.backup_status))=='pending'
    assert client.get(url+'/cleanup').json()['data']['main_status']=='purged'
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    assert client.get(url+'/cleanup').status_code==404


def test_history_filters_all_and_pinned(chat):
    client,_=chat;first=create(client);second=create(client)
    client.patch(f'/api/v1/chat/conversations/{first}',json={'pinned':True,'archived':True})
    url='/api/v1/chat/conversations'
    assert client.get(url,params={'space_id':'space','filter':'all'}).json()['data']['total']==2
    rows=client.get(url,params={'space_id':'space','filter':'pinned'}).json()['data']['items']
    assert [row['id'] for row in rows]==[first]


def test_unknown_reconciliation_reads_exact_turn_without_restart(chat,tmp_path):
    from app.chat.execution import reconcile_unknown
    client,factory=chat;cid=create(client);tid=queued(factory,cid,'unknown')
    workspace=tmp_path.resolve()/cid;workspace.mkdir()
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id==cid).values(workspace_id=cid,thread_id='thread'))
        db.execute(update(turns).where(turns.c.id==tid).values(executor_turn_id='original'));db.commit()
    class Peer:
        status='inProgress'
        def read_turn(self,thread,turn):assert (thread,turn)==('thread','original');return {'id':turn,'status':self.status}
        def close(self):pass
    with factory() as db:assert db.scalar(select(conversations.c.active_turn_id))==tid
    assert not reconcile_unknown(factory,tid,workspace,lambda _:Peer())
    Peer.status='interrupted'
    assert reconcile_unknown(factory,tid,workspace,lambda _:Peer())
    assert not reconcile_unknown(factory,tid,workspace,lambda _:Peer())
    with factory() as db:
        assert db.scalar(select(conversations.c.active_turn_id)) is None
        assert db.scalar(select(turns.c.status))=='stopped'
        assert db.scalar(select(turns.c.error_code))=='reconciled_usage_pending'


def test_stop_behavior_links_only_authorized_turn(chat):
    import json
    from app.chat.schema import usage_events
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    response=client.post(f'/api/v1/chat/turns/{tid}/interrupt',headers={'X-Chat-Client':'web'})
    assert response.status_code==200
    with factory() as db:
        row=db.execute(select(usage_events).where(usage_events.c.event_name=='chat.stop')).mappings().one()
        assert json.loads(row['properties'])=={'turn_id':tid}
        assert row['parent_request_id']==response.headers['X-Request-ID']
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    response=client.post(f'/api/v1/chat/turns/{tid}/interrupt',headers={'X-Chat-Client':'web'})
    assert response.status_code==404
    with factory() as db:
        row=db.execute(select(usage_events).where(usage_events.c.result=='failure')).mappings().one()
        assert json.loads(row['properties'])=={}


def test_output_limit_is_explicit_and_requests_interrupt(chat,tmp_path):
    from app.chat.admission import enqueue
    from app.chat.execution import run_claim
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    limits=dict(user_concurrency=1,space_concurrency=1,user_monthly_tokens=1000,space_monthly_tokens=1000,user_storage_bytes=100000,space_storage_bytes=100000,turn_reserved_tokens=100,turn_reserved_bytes=20000)
    class Peer:
        interrupted=False
        def connect(self,_):return 'thread'
        def start_turn(self,*_):
            self.items=[{'method':'item/agentMessage/delta','params':{'threadId':'thread','turnId':'turn','delta':'x'*7000}}, {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'turn','tokenUsage':{'total':{'totalTokens':10}}}}, {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'turn','status':'interrupted'}}}];return 'turn'
        def event(self,timeout):return self.items.pop(0) if self.items else None
        def interrupt(self,*_):self.interrupted=True
        def close(self):pass
    peer=Peer()
    with factory() as db:record=enqueue(db,'alice',cid,'limit','input',limits);token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:peer)=='stopped'
    assert peer.interrupted
    with factory() as db:
        assert db.scalar(select(turns.c.error_code).where(turns.c.id==record['id']))=='result_or_token_limit'
        payload=db.scalar(select(events.c.payload).where(events.c.source_id=='runner:limit'))
        assert 'output_may_be_truncated' in payload


def test_revocation_during_execution_closes_adapter_and_hides_output(chat,governance,tmp_path):
    from app.chat.admission import enqueue
    from app.chat.execution import run_claim
    from app.chat.schema import object_access,reservations
    from test_chat_accounting import LIMITS
    client,factory=chat;cid=create(client);oid=governance[1][0]['id']
    assert client.put(f'/api/v1/chat/conversations/{cid}/relations',json={'primary':oid,'references':[]}).status_code==200
    path=tmp_path.resolve()/cid;path.mkdir();closed=[]
    class Peer:
        def connect(self,previous):return 'thread'
        def start_turn(self,*_):return 'run'
        def event(self,timeout):
            with factory() as db:
                db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id=oid,user_id='alice',can_read=0));db.commit()
            return {'method':'item/agentMessage/delta','params':{'threadId':'thread','turnId':'run','delta':'revoked-content'}}
        def close(self):closed.append(True)
    with factory() as db:
        row=enqueue(db,'alice',cid,'revoke-during-run','test',LIMITS);token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:Peer())=='unknown'
    assert closed==[True]
    with factory() as db:
        assert db.scalar(select(reservations.c.status))=='reserved'
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==cid))==row['id']
        assert 'revoked-content' not in str(db.execute(select(events.c.payload)).all())
    for suffix in ('messages','relations'):
        assert client.get(f'/api/v1/chat/conversations/{cid}/{suffix}').status_code==403
    for suffix in ('events','context','diff'):
        assert client.get(f'/api/v1/chat/turns/{row["id"]}/{suffix}').status_code==403


def test_create_idempotency_permissions_conflict_and_tombstone(chat, monkeypatch):
    client, factory = chat
    payload = {'space_id': 'space', 'repository_id': 'repo', 'client_request_id': 'first-send'}
    first = client.post('/api/v1/chat/conversations', json=payload)
    assert first.status_code == 200
    cid = first.json()['data']['id']
    assert client.post('/api/v1/chat/conversations', json=payload).json()['data']['id'] == cid
    with factory() as db:
        assert len(db.execute(select(conversations)).all()) == 1
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES', '[{"id":"repo","space_id":"space"},{"id":"other","space_id":"space"}]')
    assert client.post('/api/v1/chat/conversations', json={**payload, 'repository_id': 'other'}).status_code == 409
    app.dependency_overrides[require_session_user] = lambda: {'id': 'bob'}
    assert client.post('/api/v1/chat/conversations', json=payload).status_code == 403
    with factory() as db:
        db.execute(text("INSERT INTO admin_space_members (id,space_id,user_id) VALUES ('member','space','bob')")); db.commit()
    other = client.post('/api/v1/chat/conversations', json=payload)
    assert other.status_code == 200 and other.json()['data']['id'] != cid
    app.dependency_overrides[require_session_user] = lambda: {'id': 'alice'}
    assert client.delete(f'/api/v1/chat/conversations/{cid}').status_code == 200
    assert client.post('/api/v1/chat/conversations', json=payload).status_code == 404
    assert client.post('/api/v1/chat/conversations', json={**payload,'client_request_id':'bad/id'}).status_code == 422


def test_concurrent_create_returns_one_conversation(chat):
    from concurrent.futures import ThreadPoolExecutor
    _, factory = chat
    def create_once(_):
        with factory() as db:
            return service.create_conversation(db,'alice','space','repo','并发测试','concurrent-create')['id']
    with ThreadPoolExecutor(max_workers=4) as pool:
        ids = list(pool.map(create_once, range(8)))
    assert len(set(ids)) == 1
    with factory() as db:
        assert len(db.execute(select(conversations)).all()) == 1
