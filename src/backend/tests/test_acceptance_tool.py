"""Durable consumption protocol; synthetic owner/IPC, real operation transactions."""
import pytest
from sqlalchemy import insert,select,update
from test_chat import chat
from test_acceptance_archive import settled
from app.chat import service
from app.chat.schema import turns,conversations
from app.verification.acceptance_schema import tool_waits
from app.verification import acceptance_tool as tool


def waiting(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);_,factory=chat
    token={'turn_id':item['source_turn_id'],'generation':1}
    with factory.begin() as db:
        db.execute(update(turns).values(status='running'))
        db.execute(insert(tool_waits).values(**service.identity(),source_turn_id=token['turn_id'],
            operation_id=item['id'],call_id='call-test',generation=1,state='waiting'))
    def owner(db,token):
        return (dict(db.execute(select(turns).where(turns.c.id==token['turn_id'])).mappings().one()),
                dict(db.execute(select(conversations)).mappings().one()))
    monkeypatch.setattr('app.chat.execution.owned',owner)
    monkeypatch.setattr('app.verification.acceptance_delivery.validate_inputs',lambda db,row:None)
    return state,item,token


def test_result_is_sent_once_and_requires_explicit_ack(chat,monkeypatch,tmp_path):
    state,item,token=waiting(chat,monkeypatch,tmp_path);_,factory=chat
    class Server:
        sent=[]
        def respond_tool(self,*args):self.sent.append(args)
    peer=Server()
    assert tool.poll(factory,token,peer,99,item['id'])
    assert not tool.poll(factory,token,peer,99,item['id'])
    with factory() as db:assert db.scalar(select(tool_waits.c.state))=='dispatching'
    tool.acknowledge(factory,token,'foreign-call')
    with factory() as db:assert db.scalar(select(tool_waits.c.state))=='dispatching'
    tool.acknowledge(factory,token,'call-test')
    with factory() as db:assert db.scalar(select(tool_waits.c.state))=='delivered'
    assert len(peer.sent)==1


def test_lost_send_ack_is_not_replayed(chat,monkeypatch,tmp_path):
    state,item,token=waiting(chat,monkeypatch,tmp_path);_,factory=chat
    class Peer:
        count=0
        def respond_tool(self,*args):
            self.count+=1
            raise OSError('synthetic lost acknowledgement')
    peer=Peer()
    with pytest.raises(OSError):tool.poll(factory,token,peer,99,item['id'])
    assert not tool.poll(factory,token,peer,99,item['id'])
    assert peer.count==1


def test_stop_before_result_never_sends_to_model(chat,monkeypatch,tmp_path):
    state,item,token=waiting(chat,monkeypatch,tmp_path);_,factory=chat
    current=state.get(item['id']);state.cancel(item['id'],current['version'])
    class Peer:
        def respond_tool(self,*args):pytest.fail('cancelled result sent')
    assert not tool.poll(factory,token,Peer(),99,item['id'])
    with factory() as db:assert db.scalar(select(turns.c.status))=='stopping'
