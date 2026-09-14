import json
import pytest
from sqlalchemy import select,update
from test_chat import chat,create
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.accounting import reconcile_usage,pending
from app.chat.execution import run_claim
from app.chat.schema import reservations,usage_accounts
from app.chat.app_server import ExecutorError

LIMITS=dict(user_concurrency=1,space_concurrency=1,user_monthly_tokens=10000,space_monthly_tokens=10000,user_storage_bytes=1000000,space_storage_bytes=1000000,turn_reserved_tokens=1000,turn_reserved_bytes=100000)

@pytest.mark.parametrize('defer', [False, True])
def test_late_usage_monotonic_scoped_idempotent(chat,tmp_path,monkeypatch,defer):
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    def usage(total,turn='run'):
        return {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':turn,'tokenUsage':{'total':{'totalTokens':total}}}}
    class Peer:
        def connect(self,_):return 'thread'
        def start_turn(self,*_):
            self.items=[usage(7),{'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'completed'}}},usage(21),usage(21),usage(10),usage(999,'other')];return 'run'
        def event(self,timeout):
            if self.items:return self.items.pop(0)
            raise ExecutorError('executor_disconnected')
        def close(self):pass
    with factory() as db:
        row=enqueue(db,'alice',cid,'late','test',LIMITS);token=worker.claim(db,'worker')
    if defer:monkeypatch.setattr('app.chat.accounting.reconcile_usage',lambda *_:False)
    assert run_claim(factory,token,path,lambda _:Peer())=='completed'
    if defer:
        with factory() as db:
            assert db.scalar(select(reservations.c.status))=='reserved'
            assert reconcile_usage(db,row['id'])
    with factory() as db:
        assert db.scalar(select(reservations.c.actual_tokens))==21
        assert not reconcile_usage(db,row['id'])
        assert db.scalar(select(usage_accounts.c.used_tokens).where(usage_accounts.c.id.like('user:alice:%')))==21


def test_missing_usage_stays_pending(chat,tmp_path):
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    class Peer:
        def connect(self,_):return 'thread'
        def start_turn(self,*_):self.done=False;return 'run'
        def event(self,timeout):
            if self.done:raise ExecutorError('executor_disconnected')
            self.done=True;return {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'interrupted'}}}
        def close(self):pass
    with factory() as db:
        row=enqueue(db,'alice',cid,'missing','test',LIMITS);token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:Peer())=='stopped'
    with factory() as db:
        assert pending(db)[0]['error_code']=='usage_unavailable'
        assert not reconcile_usage(db,row['id'])
        assert db.scalar(select(reservations.c.actual_tokens)) is None
        assert db.scalar(select(reservations.c.status))=='reserved'


def test_terminal_pending_usage_releases_slot_but_keeps_budget(chat):
    from app.chat.admission import release_concurrency, settle
    from app.chat.schema import turns, conversations
    from app.chat import service
    client,factory=chat;cid=create(client)
    with factory() as db:
        first=enqueue(db,'alice',cid,'first','test',LIMITS);token=worker.claim(db,'worker')
        # Uncertain execution must still block the slot.
        db.execute(update(turns).where(turns.c.id==first['id']).values(status='unknown'));db.commit()
        assert not release_concurrency(db,first['id'])
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id=='user:alice'))==1
        db.execute(update(turns).where(turns.c.id==first['id']).values(status='running'));db.commit()
        assert worker.record_event(db,token,'terminal','execution.state',{'status':'completed'},terminal='completed')
        assert not worker.record_event(db,token,'terminal','execution.state',{'status':'completed'},terminal='completed')
        assert not release_concurrency(db,first['id'])
        account=db.execute(select(usage_accounts).where(usage_accounts.c.id=='user:alice')).mappings().one()
        assert account['active_runs']==0 and account['reserved_bytes']==LIMITS['turn_reserved_bytes']
        assert db.scalar(select(reservations.c.status))=='reserved'
        assert db.scalar(select(reservations.c.actual_tokens)) is None
        second=enqueue(db,'alice',cid,'second','test',LIMITS)
        # Late usage for the old turn cannot take away the new turn's slot.
        assert settle(db,first['id'],17,100)
        assert not settle(db,first['id'],17,100)
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id=='user:alice'))==1
        monthly=db.execute(select(usage_accounts).where(usage_accounts.c.id.like('user:alice:%'))).mappings().one()
        assert monthly['used_tokens']==17 and monthly['reserved_tokens']==1000
        assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==cid))==second['id']


def test_legacy_terminal_backfill_and_repeated_migration(chat):
    from sqlalchemy import text
    from app.chat.schema import migrate, turns, conversations
    from app.chat import service
    client,factory=chat;cid=create(client)
    with factory() as db:
        first=enqueue(db,'alice',cid,'settled','test',LIMITS)
        service.interrupt(db,'alice',first['id'])
        second=enqueue(db,'alice',cid,'pending','test',LIMITS)
        db.execute(update(turns).where(turns.c.id==second['id']).values(status='completed',error_code='usage_unavailable'))
        db.execute(update(conversations).where(conversations.c.id==cid).values(active_turn_id=None));db.commit()
    engine=factory.kw['bind']
    with engine.begin() as connection:
        connection.execute(text('ALTER TABLE chat_usage_reservations DROP COLUMN concurrency_released'))
    migrate(engine);migrate(engine)
    with factory() as db:
        flags=dict(db.execute(select(reservations.c.turn_id,reservations.c.concurrency_released)).all())
        assert flags=={first['id']:1,second['id']:0}
        assert not reconcile_usage(db,second['id'])
        assert not reconcile_usage(db,second['id'])
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id=='user:alice'))==0
        assert db.scalar(select(reservations.c.status).where(reservations.c.turn_id==second['id']))=='reserved'
        assert db.scalar(select(usage_accounts.c.reserved_tokens).where(usage_accounts.c.id.like('user:alice:%')))==1000


def test_competing_terminal_repairs_release_once(chat):
    from concurrent.futures import ThreadPoolExecutor
    from app.chat.admission import release_concurrency
    from app.chat.schema import turns, conversations
    client,factory=chat;cid=create(client)
    with factory() as db:
        row=enqueue(db,'alice',cid,'repair','test',LIMITS)
        db.execute(update(turns).where(turns.c.id==row['id']).values(status='completed'))
        db.execute(update(conversations).where(conversations.c.id==cid).values(active_turn_id=None));db.commit()
    def repair(_):
        with factory() as db:
            result=release_concurrency(db,row['id']);db.commit();return result
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(repair,range(2)))==[False,True]
    with factory() as db:
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id=='user:alice'))==0
        assert db.scalar(select(reservations.c.status))=='reserved'


def test_resumed_process_usage_does_not_subtract_previous_process(chat,tmp_path):
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    actual=[]
    class Peer:
        def __init__(self,total):self.total=total
        def connect(self,previous):return 'thread'
        def start_turn(self,*_):
            self.items=[{'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'run','tokenUsage':{'total':{'totalTokens':self.total}}}},
                        {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'completed'}}}];return 'run'
        def event(self,timeout):
            if self.items:return self.items.pop(0)
            raise ExecutorError('executor_disconnected')
        def close(self):pass
    for total in (100,15,120):
        with factory() as db:
            row=enqueue(db,'alice',cid,str(total),'test',LIMITS);token=worker.claim(db,'worker')
        assert run_claim(factory,token,path,lambda _:Peer(total))=='completed'
        with factory() as db:
            actual.append(db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id==row['id'])))
    assert actual==[100,15,120]
    with factory() as db:
        assert db.scalar(select(usage_accounts.c.used_tokens).where(usage_accounts.c.id.like('user:alice:%')))==235


def test_legacy_unscoped_receipt_cannot_auto_settle(chat):
    from app.chat.schema import turns
    client,factory=chat;cid=create(client)
    with factory() as db:
        row=enqueue(db,'alice',cid,'old-receipt','test',LIMITS);token=worker.claim(db,'worker')
        worker.record_event(db,token,'runner:accounting','execution.usage',{'total_tokens':3,'actual_bytes':100,'thread_total':200})
        worker.record_event(db,token,'terminal','execution.state',{'status':'completed'},terminal='completed')
        assert not reconcile_usage(db,row['id'])
        assert db.scalar(select(reservations.c.status))=='reserved'
        assert db.scalar(select(reservations.c.actual_tokens)) is None
        assert db.scalar(select(usage_accounts.c.active_runs).where(usage_accounts.c.id=='user:alice'))==0
