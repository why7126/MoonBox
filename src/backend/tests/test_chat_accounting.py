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

def test_terminal_grace_preserves_command_completion(chat,tmp_path):
    from app.chat.schema import events
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    class Peer:
        def connect(self,_):return 'thread'
        def start_turn(self,*_):
            self.items=[
                {'method':'item/started','params':{'threadId':'thread','turnId':'run','item':{'id':'cmd','type':'commandExecution'}}},
                {'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'run','status':'completed'}}},
                {'method':'item/completed','params':{'threadId':'thread','turnId':'run','item':{'id':'cmd','type':'commandExecution','status':'completed','exitCode':0}}},
                {'method':'thread/tokenUsage/updated','params':{'threadId':'thread','turnId':'run','tokenUsage':{'total':{'totalTokens':7}}}}]
            return 'run'
        def event(self,timeout):
            if self.items:return self.items.pop(0)
            raise ExecutorError('executor_disconnected')
        def close(self):pass
    with factory() as db:
        row=enqueue(db,'alice',cid,'late-command','test',LIMITS);token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:Peer())=='completed'
    with factory() as db:
        payloads=[json.loads(value) for value in db.scalars(select(events.c.payload).where(events.c.turn_id==row['id'],events.c.event_type=='execution.tool'))]
        assert [value['phase'] for value in payloads]==['started','completed']
        assert payloads[-1]['exit_code']==0
        assert db.scalar(select(reservations.c.actual_tokens))==7

def test_unknown_terminal_reconciliation_settles_persisted_receipt(chat,tmp_path):
    from sqlalchemy import insert
    from app.chat import service
    from app.chat.execution import reconcile_unknown
    from app.chat.schema import conversations, turns, events
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    with factory() as db:
        row=enqueue(db,'alice',cid,'recover-accounting','test',LIMITS)
        db.execute(update(conversations).where(conversations.c.id==cid).values(workspace_id=cid,thread_id='thread'))
        db.execute(update(turns).where(turns.c.id==row['id']).values(status='unknown',executor_turn_id='run'))
        db.execute(insert(events).values(**service.identity(),turn_id=row['id'],sequence=1,source_id='runner:accounting',
            event_type='execution.usage',payload=json.dumps({'total_tokens':17,'actual_bytes':123,'usage_scope':'app_server_process_v1'})))
        db.commit()
    class Peer:
        def read_turn(self,thread,turn):return {'id':turn,'status':'completed','items':[
            {'id':'archive-cmd','type':'commandExecution','status':'completed','exitCode':0},
            {'id':'unfinished-cmd','type':'commandExecution','status':'inProgress'}]}
        def close(self):pass
    assert reconcile_unknown(factory,row['id'],path,lambda _:Peer())
    assert not reconcile_unknown(factory,row['id'],path,lambda _:Peer())
    with factory() as db:
        assert db.scalar(select(reservations.c.status))=='settled'
        assert db.scalar(select(reservations.c.actual_tokens))==17
        assert db.scalar(select(turns.c.error_code)) is None
        recovered=[json.loads(value) for value in db.scalars(select(events.c.payload).where(events.c.event_type=='execution.tool'))]
        assert len(recovered)==1 and recovered[0]['exit_code']==0
        terminal=json.loads(db.scalar(select(events.c.payload).where(events.c.source_id=='reconcile:terminal')))
        assert terminal['usage_pending'] is False

def test_archive_execution_prompt_uses_serial_recovery_contract(chat):
    from app.governance.preparation import execution_prompt_for_turn
    client,factory=chat;cid=create(client)
    prompt='/opsx-archive BUG-9001-test-archive'
    with factory() as db:
        result=execution_prompt_for_turn(db,{'id':cid},prompt)
        assert result.startswith(prompt+'\n')
        assert 'scripts/archive-change.sh' in result and '--finalize' in result
        assert 'shutil.move' in result and '禁止使用 Path.rename' in result
        assert 'Workflow Sync' in result and 'Issue promote' in result

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
