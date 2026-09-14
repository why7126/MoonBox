import json
import pytest
from sqlalchemy import select, update
from test_chat import chat, create
from app.chat import service, worker
from app.chat.admission import enqueue, settle
from app.chat.settings import execution_limits, retention_limits
from app.chat.schema import usage_accounts, reservations, cleanup_jobs
from app.chat.execution import run_claim
from app.chat.app_server import ExecutorError


def unlimited(monkeypatch):
    value = {key: 'unlimited' for key in ('user_concurrency','space_concurrency','user_monthly_tokens','space_monthly_tokens','user_storage_bytes','space_storage_bytes','turn_reserved_tokens')}
    value['turn_reserved_bytes'] = 100000
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS', json.dumps(value))
    return execution_limits()


def test_explicit_unlimited_keeps_mutex_and_actual_accounting(chat, monkeypatch):
    client, factory = chat
    limits = unlimited(monkeypatch)
    first, second = create(client), create(client)
    with factory() as db:
        one = enqueue(db,'alice',first,'one','test',limits)
        db.execute(update(usage_accounts).values(used_tokens=10**15,used_bytes=10**15,active_runs=100)); db.commit()
        two = enqueue(db,'alice',second,'two','test',limits)
        assert two['status'] == 'queued'
        with pytest.raises(service.ChatError): enqueue(db,'alice',first,'collision','test',limits)
        assert enqueue(db,'alice',first,'one','test',limits)['id'] == one['id']
        token = worker.claim(db,'worker')
        assert worker.record_event(db,token,'terminal','execution.state',{'status':'completed'},terminal='completed')
        assert settle(db,token['turn_id'],123,456)
        assert db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id==token['turn_id'])) == 123
        assert db.scalar(select(usage_accounts.c.used_tokens).where(usage_accounts.c.id.like('user:alice:%'))) == 10**15 + 123


def test_unlimited_token_does_not_interrupt_zero_reservation(chat, tmp_path, monkeypatch):
    client, factory = chat; cid = create(client); path = tmp_path.resolve()/cid; path.mkdir()
    class Peer:
        def connect(self, _): return 'thread'
        def start_turn(self, *_):
            self.items = [
                {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'turn','tokenUsage':{'total':{'totalTokens':1000000}}}},
                {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'turn','status':'completed'}}}]
            return 'turn'
        def event(self, timeout):
            if self.items: return self.items.pop(0)
            raise ExecutorError('executor_disconnected')
        def interrupt(self, *_): pytest.fail('unlimited tokens must not request quota stop')
        def close(self): pass
    with factory() as db:
        enqueue(db,'alice',cid,'one','test',unlimited(monkeypatch)); token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:Peer()) == 'completed'
    with factory() as db: assert db.scalar(select(reservations.c.actual_tokens)) == 1000000


def test_missing_null_and_mixed_budget_fail_closed(monkeypatch):
    for value in ({}, {'user_concurrency':None}, {'user_concurrency':True}):
        monkeypatch.setenv('MOONBOX_CHAT_LIMITS',json.dumps(value)); assert execution_limits() is None
    unlimited(monkeypatch)
    value=json.loads(__import__('os').environ['MOONBOX_CHAT_LIMITS']); value['user_monthly_tokens']=100
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS',json.dumps(value)); assert execution_limits() is None


def test_unbounded_deletion_keeps_pending_copies(chat, monkeypatch):
    from app.chat.cleanup import delete_history, process_copies
    client,factory=chat; cid=create(client)
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION',json.dumps({'executor_delete_seconds':'unlimited','backup_expiry_seconds':'unlimited'}))
    assert retention_limits() == {'executor_delete_seconds':None,'backup_expiry_seconds':None}
    with factory() as db:
        row=enqueue(db,'alice',cid,'one','test',unlimited(monkeypatch)); token=worker.claim(db,'worker')
        worker.record_event(db,token,'terminal','execution.state',{'status':'completed'},terminal='completed'); settle(db,row['id'],1,2)
        result=delete_history(db,'alice',cid)
        assert result['main_status']=='purged' and result['backup_status']=='pending'
        job=db.execute(select(cleanup_jobs)).mappings().one()
        assert job['executor_due_at'] is None and job['backup_due_at'] is None
        assert not process_copies(db,cid,lambda _:True,lambda _:False)
        assert db.scalar(select(cleanup_jobs.c.backup_status))=='retry'
