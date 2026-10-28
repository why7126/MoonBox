"""BUG-0064: budget, fencing, truthful status and retry authorization."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import time
import pytest
from sqlalchemy import select, update
from test_chat import chat, create, queued
from app.chat import recovery
from app.chat.recovery_schema import recoveries, resumes
from app.chat.schema import turns, conversations, task_trace_spans
from app.chat.settings import recovery_policy
from app.chat.execution import reconcile_unknown
from app.chat.app_server import ExecutorError


def sample(chat, tmp_path):
    client, factory = chat
    cid = create(client); tid = queued(factory, cid, 'unknown')
    path = tmp_path/cid; path.mkdir()
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id == cid).values(workspace_id=cid, thread_id='thread'))
        db.execute(update(turns).where(turns.c.id == tid).values(executor_turn_id='original')); db.commit()
    return factory, tid, path


def get(factory, tid):
    with factory() as db: return dict(db.execute(select(recoveries).where(recoveries.c.turn_id == tid)).mappings().one())


def test_permanent_failure_budget_and_restart(chat, tmp_path):
    factory, tid, path = sample(chat, tmp_path)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    for count in range(1, 7):
        with factory() as db: lease = recovery.claim(db, now=now)
        assert lease['attempt_count'] == count
        with factory() as db: assert recovery.claim(db, now=now) is None
        with factory() as db: assert recovery.finish(db, lease, 'no_terminal', now=now, jitter=0)
        row = get(factory, tid)
        if count < 6:
            with factory() as db: assert recovery.claim(db, now=now+timedelta(seconds=1)) is None
            now = datetime.fromisoformat(row['next_retry_at'])
    assert row['state'] == 'paused'
    for later in (330, 3600, 86400):
        with factory() as db: assert recovery.claim(db, now=now+timedelta(seconds=later)) is None
    with factory() as db:
        assert db.scalar(select(turns.c.status)) == 'unknown'
        assert db.scalar(select(conversations.c.active_turn_id)) == tid
        assert len(db.scalars(select(task_trace_spans.c.id)).all()) == 6


def test_time_budget_disabled_and_expired_lease(chat, tmp_path):
    factory, tid, path = sample(chat, tmp_path)
    now = datetime.now(timezone.utc).replace(microsecond=0)
    with factory() as db: first = recovery.claim(db, now=now)
    with factory() as db: second = recovery.claim(db, now=now+timedelta(seconds=121))
    assert second['attempt_count'] == 2 and second['lease_token'] != first['lease_token']
    with factory() as db: assert not recovery.fence(db, first)
    with factory() as db: assert not recovery.finish(db, first, 'no_terminal')
    with factory() as db: cleanup = recovery.claim(db, {**recovery_policy(), 'enabled': False}, now=now+timedelta(seconds=1801))
    assert cleanup['cleanup_only'] and cleanup['attempt_count'] == 2
    with factory() as db: recovery.finish(db, cleanup, 'budget_exhausted', now=now+timedelta(seconds=1801))
    assert get(factory, tid)['state'] == 'paused'


@pytest.mark.parametrize('terminal,expected', [('completed','completed'), ('failed','failed'), ('interrupted','stopped')])
def test_authoritative_terminal_only(chat, tmp_path, terminal, expected):
    factory, tid, path = sample(chat, tmp_path)
    with factory() as db: lease = recovery.claim(db)
    class Peer:
        def read_turn(self, thread, turn):
            assert (thread, turn) == ('thread', 'original')
            return {'status': terminal}
        def close(self): pass
    assert reconcile_unknown(factory, tid, path, lambda _: Peer(), recovery_lease=lease)
    with factory() as db:
        recovery.finish(db, lease, 'terminal')
        assert db.scalar(select(turns.c.status)) == expected
        assert db.scalar(select(conversations.c.active_turn_id)) is None
    assert get(factory, tid)['state'] == 'resolved'


def test_lost_lease_cannot_commit(chat, tmp_path):
    factory, tid, path = sample(chat, tmp_path)
    with factory() as db: lease = recovery.claim(db)
    class Peer:
        def read_turn(self, *_):
            with factory() as db:
                db.execute(update(recoveries).values(lease_token='new-owner')); db.commit()
            return {'status': 'completed'}
        def close(self): pass
    assert not reconcile_unknown(factory, tid, path, lambda _: Peer(), recovery_lease=lease)
    with factory() as db: assert db.scalar(select(turns.c.status)) == 'unknown'


def test_resume_permissions_generation_and_idempotency(chat, tmp_path):
    factory, tid, path = sample(chat, tmp_path)
    with factory() as db: lease = recovery.claim(db)
    with factory() as db: recovery.finish(db, lease, 'security_rejected')
    with factory() as db:
        with pytest.raises(PermissionError): recovery.resume(db, tid, 0, 'request', 'operator', 'configuration_fixed', authorize=lambda: False)
        assert recovery.resume(db, tid, 0, 'request', 'operator', 'configuration_fixed', authorize=lambda: True)
        assert not recovery.resume(db, tid, 0, 'request', 'operator', 'configuration_fixed', authorize=lambda: True)
        with pytest.raises(ValueError): recovery.resume(db, tid, 0, 'other', 'operator', 'configuration_fixed', authorize=lambda: True)
    assert get(factory, tid)['generation'] == 1
    with factory() as db:
        assert db.scalar(select(turns.c.status)) == 'unknown'
        assert db.scalar(select(resumes.c.reason)) == 'configuration_fixed'


def test_concurrent_claim_one_winner(chat, tmp_path):
    factory, tid, path = sample(chat, tmp_path)
    # Enrol independently; concurrent test includes competing generation CAS.
    with factory() as db: recovery.claim(db, {**recovery_policy(), 'enabled': False})
    def claim(_):
        with factory() as db: return recovery.claim(db)
    with ThreadPoolExecutor(max_workers=2) as pool: leases = list(pool.map(claim, range(2)))
    assert sum(value is not None for value in leases) == 1


@pytest.mark.parametrize('code,result', [('executor_rpc_rejected','rpc_rejected'), ('executor_timeout_thread_read','timeout'), ('workspace_binding_mismatch','workspace_identity'), ('container_sandbox_preflight_failed','security_rejected')])
def test_error_classification(code, result):
    assert recovery.classify(ExecutorError(code)) == result


@pytest.mark.parametrize('key,value', [('ATTEMPTS','0'), ('ATTEMPTS','11'), ('BUDGET_SECONDS','unlimited'), ('ENABLED','yes')])
def test_policy_rejects_unbounded(monkeypatch,key,value):
    monkeypatch.setenv('MOONBOX_CHAT_RECOVERY_'+key,value)
    with pytest.raises(ValueError): recovery_policy()


def test_trace_failure_does_not_lose_budget(chat,tmp_path,monkeypatch):
    factory,tid,path=sample(chat,tmp_path)
    with factory() as db: lease=recovery.claim(db)
    monkeypatch.setattr('app.chat.recovery_observability.insert',lambda *_: (_ for _ in ()).throw(RuntimeError('synthetic')))
    with factory() as db: assert recovery.finish(db,lease,'rpc_rejected')
    assert get(factory,tid)['attempt_count']==1
    assert get(factory,tid)['state']=='waiting'


def test_slot_does_not_block_normal_claim(chat,tmp_path,monkeypatch):
    from app.chat.recovery_worker import RecoverySlot
    from app.chat import worker
    factory,tid,path=sample(chat,tmp_path)
    entered=threading.Event();release=threading.Event()
    def slow(*_): entered.set();release.wait(5)
    monkeypatch.setattr('app.chat.recovery_worker.execute',slow)
    slot=RecoverySlot(factory,None,None,recovery_policy())
    try:
        slot.tick();assert entered.wait(2)
        cid=create(chat[0]);queued(factory,cid)
        start=time.monotonic()
        with factory() as db: assert worker.claim(db,'normal') is not None
        assert time.monotonic()-start<5
        slot.tick()
    finally: release.set();slot.close()


def test_chat_permission_error_is_classified():
    from app.chat.service import ChatError
    assert recovery.classify(ChatError(2503, 'synthetic', 403)) == 'security_rejected'


def test_expired_exhausted_lease_cleans_without_starting_new_container(chat,tmp_path,monkeypatch):
    from app.chat.recovery_worker import execute
    factory,tid,path=sample(chat,tmp_path)
    policy={**recovery_policy(),'attempts':1}
    with factory() as db: first=recovery.claim(db,policy)
    with factory() as db:
        db.execute(update(recoveries).values(lease_expires_at='2000-01-01T00:00:00+00:00'));db.commit()
        lease=recovery.claim(db,policy)
    assert lease['cleanup_only'] and lease['attempt_count']==1
    cleaned=[]
    monkeypatch.setattr('app.chat.recovery_runtime.Runtime.cleanup',lambda self,**kwargs:cleaned.append(kwargs.get('stale',False)))
    monkeypatch.setattr('app.chat.recovery_runtime.Runtime.collect_metrics',lambda self:None)
    execute(factory,lease,lambda _: (_ for _ in ()).throw(AssertionError('no workspace or server allowed')),None,policy)
    assert cleaned==[True,False]
    assert get(factory,tid)['state']=='paused'


def test_stale_job_cannot_cleanup_new_owner(chat,tmp_path,monkeypatch):
    from app.chat.recovery_worker import execute
    factory,tid,path=sample(chat,tmp_path)
    with factory() as db:first=recovery.claim(db)
    with factory() as db:
        db.execute(update(recoveries).values(lease_token='new-owner'));db.commit()
    monkeypatch.setattr('app.chat.recovery_runtime.Runtime.cleanup',lambda *a,**k: (_ for _ in ()).throw(AssertionError('stale cleanup')))
    execute(factory,first,None,None,recovery_policy())
    assert get(factory,tid)['lease_token']=='new-owner'


def test_recovery_ledger_is_purged_with_authorized_history(chat,tmp_path,monkeypatch):
    import json
    from app.chat.cleanup import delete_history
    factory,tid,path=sample(chat,tmp_path)
    with factory() as db: lease=recovery.claim(db)
    with factory() as db:
        recovery.finish(db,lease,'security_rejected')
        recovery.resume(db,tid,0,'delete-test','operator','operator_reviewed',authorize=lambda:True)
        db.execute(update(turns).where(turns.c.id==tid).values(status='stopped'))
        db.execute(update(conversations).values(active_turn_id=None,workspace_id=None));db.commit()
    monkeypatch.setenv('MOONBOX_CHAT_RETENTION',json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}))
    with factory() as db:
        cid=db.scalar(select(turns.c.conversation_id).where(turns.c.id==tid))
        delete_history(db,'alice',cid)
        assert db.scalar(select(recoveries.c.turn_id)) is None
        assert db.scalar(select(resumes.c.request_id)) is None


def test_deleted_recovery_ledger_does_not_return_after_backup_restore(chat,tmp_path,monkeypatch):
    import sqlite3
    from app.chat.backup import LocalBackupStore
    factory,tid,path=sample(chat,tmp_path)
    with factory() as db:
        if db.get_bind().dialect.name!='sqlite':pytest.skip('offline backup is SQLite-only; MySQL deletion tested separately')
        lease=recovery.claim(db)
        database=db.get_bind().url.database
    (tmp_path/'backups').mkdir(mode=0o700)
    store=LocalBackupStore(tmp_path/'backups',initialize=True)
    backup=store.create(Path(database))
    with factory() as db:cid=db.scalar(select(turns.c.conversation_id).where(turns.c.id==tid))
    store.record_deletion(cid,source=Path(database))
    destination=tmp_path/'restored.sqlite';store.restore(backup,destination)
    with sqlite3.connect(destination) as db:
        assert db.execute('SELECT count(*) FROM chat_turn_recoveries').fetchone()[0]==0
        assert db.execute('SELECT count(*) FROM chat_turns').fetchone()[0]==0


def test_multiple_unknown_have_independent_due_times(chat,tmp_path):
    factory,first,path=sample(chat,tmp_path)
    factory,second,path2=sample(chat,tmp_path)
    now=datetime.now(timezone.utc).replace(microsecond=0)
    with factory() as db:one=recovery.claim(db,now=now)
    with factory() as db:recovery.finish(db,one,'rpc_rejected',now=now,jitter=0)
    with factory() as db:two=recovery.claim(db,now=now)
    assert {one['turn_id'],two['turn_id']}=={first,second}
    with factory() as db:recovery.finish(db,two,'workspace_identity',now=now)
    assert get(factory,one['turn_id'])['state']=='waiting'
    assert get(factory,two['turn_id'])['state']=='paused'
