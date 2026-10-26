import io
import json
import queue
from types import SimpleNamespace
import pytest
from sqlalchemy import select
from test_chat import chat, create
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.schema import turns
from app.chat.app_server import AppServer


@pytest.mark.parametrize('explicit_limit,expected', [(None, 'completed'), (300, 'unknown')])
def test_long_turn_default_has_no_wall_clock_deadline(chat,tmp_path,monkeypatch,explicit_limit,expected):
    client,factory=chat; cid=create(client); path=tmp_path/cid; path.mkdir()
    limits=dict(user_concurrency=1,space_concurrency=2,user_monthly_tokens=10000,space_monthly_tokens=20000,user_storage_bytes=1000000,space_storage_bytes=2000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)
    clock=[0]
    monkeypatch.setattr('app.chat.execution.time',SimpleNamespace(monotonic=lambda:clock[0]))
    class Peer:
        def connect(self,previous):return 'thread'
        def start_turn(self,thread,prompt):self.step=0;return 'run'
        def event(self,timeout):
            self.step+=1;clock[0]+=301
            if self.step==1:return {'method':'item/agentMessage/delta','params':{'threadId':'thread','turnId':'run','delta':'still working'}}
            if self.step==2:return {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'run','tokenUsage':{'total':{'totalTokens':10}}}}
            return {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'completed'}}}
        def close(self):pass
    with factory() as db:
        row=enqueue(db,'alice',cid,'long','test',limits);token=worker.claim(db,'test')
    options={} if explicit_limit is None else {'max_seconds':explicit_limit}
    assert run_claim(factory,token,path,lambda _:Peer(),**options)==expected
    with factory() as db:
        assert db.scalar(select(turns.c.status).where(turns.c.id==row['id']))==expected


@pytest.mark.parametrize('response,oversize,accepted',[(True,False,True),(False,False,True),(True,True,False),(False,True,False)])
def test_deployment_frame_boundary_applies_to_responses_and_events(response,oversize,accepted):
    size=9*1024*1024 if oversize else 300000
    value={'id':1,'result':'x'*size} if response else {'method':'event','params':'x'*size}
    server=AppServer.__new__(AppServer)
    server.process=SimpleNamespace(stdout=io.BytesIO((json.dumps(value)+'\n').encode()))
    server.incoming=queue.Queue();server.failure=None
    server.closed = False
    server._read()
    assert (not server.incoming.empty())==accepted
    assert server.failure==('executor_disconnected' if accepted else 'protocol_resource_limit')


@pytest.mark.parametrize('size,response', [(262144,False),(1048576,False),(4194304,True),(7340032,True),(8388608,True),(8388609,False)])
def test_exact_protocol_frame_matrix(size, response):
    value = {'id':1,'result':''} if response else {'method':'event','params':''}
    key = 'result' if response else 'params'
    overhead = len((json.dumps(value)+'\n').encode())
    value[key] = 'x' * (size-overhead)
    payload = (json.dumps(value)+'\n').encode(); assert len(payload) == size
    server = AppServer.__new__(AppServer); server.process = SimpleNamespace(stdout=io.BytesIO(payload))
    server.incoming = queue.Queue(); server.failure = None; server.closed = False
    server._read()
    assert (not server.incoming.empty()) == (size <= 8388608)
    assert server.failure == ('executor_disconnected' if size <= 8388608 else 'protocol_resource_limit')


@pytest.mark.parametrize('payload',[b'{"text":"unfinished',b'{"text":"\xff"}\n',b'{"ok":true}'])
def test_malformed_or_incomplete_frames_are_not_published(payload):
    server = AppServer.__new__(AppServer); server.process = SimpleNamespace(stdout=io.BytesIO(payload))
    server.incoming = queue.Queue(); server.failure = None; server.closed = False
    server._read()
    assert server.incoming.empty() and server.failure == 'executor_invalid_frame'
