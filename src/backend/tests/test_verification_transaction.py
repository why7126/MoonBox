"""Real independent database connections cover the BUG-0068 lock mechanism."""
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep
import pytest
from sqlalchemy import event, select, text, update
from sqlalchemy.exc import OperationalError
from test_chat import chat
from test_governance_writer import writing
from test_direct_completion import direct_scene, OID
from app.governance import execution_context as context, execution_guard as guards
from app.governance.verification_transaction import VerificationPlan, lock_code, diagnostic


def test_terminal_noop_never_starts_write_transaction(direct_scene):
    factory, project, tid, _, _ = direct_scene
    engine = factory.kw['bind']
    writes = []
    def capture(conn, cursor, sql, params, ctx, many):
        if sql.lstrip().upper().startswith('UPDATE'):
            writes.append(sql)
    event.listen(engine, 'before_cursor_execute', capture)
    try:
        with factory() as db:
            assert guards.terminal(db, tid, 'completed') == 0
            with factory() as other:
                other.execute(text("UPDATE admin_spaces SET name='independent' WHERE id='space'"))
                other.commit()
        assert len(writes) == 1  # Only the independent writer, no guard UPDATE.
    finally:
        event.remove(engine, 'before_cursor_execute', capture)


def test_scanning_does_not_hold_write_lock_and_rejects_stale_plan(direct_scene, monkeypatch):
    factory, project, tid, _, version = direct_scene
    original = context.stable
    scans = []
    def scanning(root):
        with factory() as writer:
            if writer.bind.dialect.name == 'sqlite':
                writer.execute(text('PRAGMA busy_timeout=200'))
            writer.execute(update(guards.execution_guards).where(
                guards.execution_guards.c.operation_id == tid).values(version=version+1))
            writer.commit()
        scans.append(True)
        return original(root)
    monkeypatch.setattr(context, 'stable', scanning)
    with factory() as db:
        context.reconcile(db, 'alice', project)
        row = guards.read(db, project.key, OID)
        assert row['version'] == version+1
        assert row['state'] == 'needs_review'
    assert scans


def test_twenty_rounds_two_readers_and_writer(direct_scene, monkeypatch):
    factory, project, tid, _, _ = direct_scene
    original = context.stable
    with factory() as db:
        db.execute(update(guards.execution_guards).where(
            guards.execution_guards.c.operation_id == tid).values(state='running'))
        db.commit()
    barrier = Barrier(3)
    def scanning(root):
        barrier.wait(timeout=10)
        # Both readers remain inside filesystem work while the writer commits.
        barrier.wait(timeout=10)
        return original(root)
    monkeypatch.setattr(context, 'stable', scanning)
    # Missing completion proof keeps each round exercising the scan path.
    monkeypatch.setattr(context.store, 'read', lambda *a: {})
    def reader():
        with factory() as db:
            context.reconcile(db, 'alice', project)
    timings = []
    def writer():
        from time import perf_counter
        barrier.wait(timeout=10)
        started = perf_counter()
        with factory() as db:
            if db.bind.dialect.name == 'sqlite':
                db.execute(text('PRAGMA busy_timeout=200'))
            db.execute(text("UPDATE admin_spaces SET name='concurrent' WHERE id='space'"))
            db.commit()
        timings.append((perf_counter()-started)*1000)
        barrier.wait(timeout=10)
    with ThreadPoolExecutor(max_workers=3) as pool:
        for _ in range(20):
            futures = [pool.submit(reader), pool.submit(reader), pool.submit(writer)]
            for future in futures:
                future.result(timeout=15)
    import json, os, statistics
    from pathlib import Path
    output = os.environ.get('BUG0068_CONCURRENCY_EVIDENCE')
    if output:
        Path(output).write_text(json.dumps({'rounds':20,'readers':2,'writers':1,
            'failed':0,'writer_p50_ms':statistics.median(timings),
            'writer_p95_ms':sorted(timings)[18]}))
    with factory() as db:
        row = guards.read(db, project.key, OID)
        assert row['state'] == 'needs_review'
        assert row['operation_id'] == tid


def make_plan(factory, project, tid):
    db = factory()
    row = dict(guards.read(db, project.key, OID)); db.rollback()
    plan = VerificationPlan(db)
    plan.execute(update(guards.execution_guards).where(
        guards.execution_guards.c.operation_id == tid).values(reason_code='checked'))
    return db, plan, {'actor':'alice', 'project':project, 'expected':{'object_id':OID,'_row':row}}


def busy():
    error = sqlite3.OperationalError('secret SQL parameters')
    error.sqlite_errorcode = 5
    return OperationalError('secret statement', {'secret':'value'}, error)


@pytest.mark.parametrize('persistent', [False, True])
def test_retry_is_bounded_and_only_for_uncommitted_lock(direct_scene, monkeypatch, persistent):
    factory, project, tid, _, _ = direct_scene
    db, plan, args = make_plan(factory, project, tid)
    original = db.execute
    attempts = []
    def execute(statement, *a, **kw):
        if getattr(statement, 'is_update', False):
            attempts.append(1)
            if persistent or len(attempts) == 1:
                raise busy()
        return original(statement, *a, **kw)
    monkeypatch.setattr(db, 'execute', execute)
    try:
        if persistent:
            with pytest.raises(OperationalError): plan.apply(**args)
            assert len(attempts) == 3
        else:
            assert plan.apply(**args)
            assert len(attempts) == 3  # failed fence + successful fence and mutation
    finally:
        db.close()


def test_commit_unknown_never_replayed_and_readback_is_authoritative(direct_scene, monkeypatch):
    factory, project, tid, _, _ = direct_scene
    db, plan, args = make_plan(factory, project, tid)
    original = db.commit
    commits = []
    def commit():
        original(); commits.append(1); raise busy()
    monkeypatch.setattr(db, 'commit', commit)
    try:
        with pytest.raises(OperationalError): plan.apply(**args)
        assert len(commits) == 1
    finally: db.close()
    with factory() as other:
        assert guards.read(other, project.key, OID)['reason_code'] == 'checked'


def test_revoked_permission_prevents_planned_write(direct_scene):
    from app.chat.service import ChatError
    factory, project, tid, _, _ = direct_scene
    db, plan, args = make_plan(factory, project, tid)
    with factory() as writer:
        writer.execute(text("UPDATE admin_spaces SET status='FROZEN'")); writer.commit()
    try:
        with pytest.raises(ChatError): plan.apply(**args)
    finally: db.close()
    with factory() as other:
        assert guards.read(other, project.key, OID)['reason_code'] != 'checked'


def test_diagnostics_never_leak_sql_and_sink_failure_is_safe(monkeypatch):
    from app.chat.resource_guard import database_failure_details
    assert lock_code(busy()) == 5
    error = OperationalError('private', {}, Exception('private'))
    assert lock_code(error) is None
    assert database_failure_details(busy()) == {'database_code':5, 'frames':[]}
    monkeypatch.setattr('logging.Logger.info', lambda *a, **kw: (_ for _ in ()).throw(RuntimeError()))
    diagnostic('test', code=5)


def test_two_second_scan_allows_independent_writer(direct_scene, monkeypatch):
    from threading import Event
    factory, project, tid, _, _ = direct_scene
    scanning, release = Event(), Event()
    original = context.stable
    def slow(root):
        scanning.set()
        assert release.wait(5)
        return original(root)
    monkeypatch.setattr(context, 'stable', slow)
    monkeypatch.setattr(context.store, 'read', lambda *a: {})
    def reader():
        with factory() as db: context.reconcile(db, 'alice', project)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(reader)
        try:
            assert scanning.wait(5)
            with factory() as db:
                if db.bind.dialect.name == 'sqlite': db.execute(text('PRAGMA busy_timeout=200'))
                db.execute(text("UPDATE admin_spaces SET name='during_scan' WHERE id='space'"))
                db.commit()
            sleep(2)
        finally: release.set()
        future.result(timeout=10)


def test_epoch_change_rejects_old_plan(direct_scene):
    from app.chat.schema import governance_project_locks as locks
    factory, project, tid, _, _ = direct_scene
    db, plan, args = make_plan(factory, project, tid)
    # Different observed generation is enough to reject without a guard write.
    try:
        assert not plan.apply(**args, expected_epoch=999)
    finally: db.close()
    with factory() as other:
        assert guards.read(other, project.key, OID)['reason_code'] != 'checked'


def test_actual_lock_timeout_is_bounded(direct_scene):
    factory, project, tid, _, _ = direct_scene
    db, plan, args = make_plan(factory, project, tid)
    with factory() as owner:
        # Lock the target row (MySQL) and database (SQLite) without changing the fence.
        owner.execute(update(guards.execution_guards).where(
            guards.execution_guards.c.operation_id == tid).values(reason_code='result_unverified'))
        from time import monotonic
        started = monotonic()
        try:
            with pytest.raises(OperationalError): plan.apply(**args)
            assert monotonic() - started < 4
        finally:
            owner.rollback(); db.close()


def test_repeated_failure_reason_does_not_write_again(direct_scene):
    from app.governance import store
    factory, project, tid, rid, _ = direct_scene
    record = store.read(rid, 'operation'); record['steps'] = []; store.write(rid, 'operation', record)
    with factory() as db: context.reconcile(db, 'alice', project)
    writes = []
    engine = factory.kw['bind']
    def capture(conn, cursor, sql, params, ctx, many):
        if sql.lstrip().upper().startswith(('UPDATE', 'INSERT')): writes.append(sql)
    event.listen(engine, 'before_cursor_execute', capture)
    try:
        with factory() as db: context.reconcile(db, 'alice', project)
        assert not writes
    finally: event.remove(engine, 'before_cursor_execute', capture)
