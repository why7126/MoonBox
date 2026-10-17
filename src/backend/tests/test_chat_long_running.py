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


@pytest.mark.parametrize('response,oversize,accepted',[(True,False,True),(False,False,False),(True,True,False)])
def test_history_response_bound_preserves_stream_event_limit(response,oversize,accepted):
    value={'id':1,'result':'x'*(5*1024*1024 if oversize else 300000)} if response else {'method':'event','params':'x'*300000}
    server=AppServer.__new__(AppServer)
    server.process=SimpleNamespace(stdout=io.BytesIO((json.dumps(value)+'\n').encode()))
    server.incoming=queue.Queue();server.failure=None
    server.closed = False
    server._read()
    assert (not server.incoming.empty())==accepted
    assert server.failure==('executor_disconnected' if accepted else 'executor_frame_limit')
