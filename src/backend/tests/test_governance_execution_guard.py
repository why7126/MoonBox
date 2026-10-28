"""Guard behavior against a real transactional store, not UI button state."""
import unittest
import os
import tempfile
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.governance import execution_guard as guard
from app.chat import service



def acquire(db, op='first', **overrides):
    values = dict(scope_key='project', object_id='BUG-0044-test', operation_id=op,
                  conversation_id='conversation', owner_id='alice', action='sprint-propose',
                  confirmed_stage='approved', baseline_revision='before')
    return guard.acquire(db, **{**values, **overrides})


def confirm(db, row, **overrides):
    values = dict(scope_key=row['scope_key'], object_id=row['object_id'],
                  operation_id=row['operation_id'], version=row['version'],
                  result_revision='after', current_revision='after', stage='iteration',
                  business_valid=True, sync_valid=True, execution_ended=True)
    return guard.confirm(db, **{**values, **overrides})


def process_attempt(url, start, results, op):
    engine = create_engine(url)
    try:
        with sessionmaker(engine)() as db:
            start.wait(10)
            try:
                acquire(db, op)
                db.commit()
                results.put('accepted')
            except service.ChatError:
                db.rollback()
                results.put('busy')
    finally:
        engine.dispose()


class GuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.engine = create_engine(os.environ.get("GUARD_TEST_DATABASE_URL") or f'sqlite:///{Path(self.temp.name) / "guards.db"}')
        guard.execution_guards.create(self.engine)
        guard.execution_requests.create(self.engine)
        # The production migration uses the same additive, repeatable DDL.
        guard.execution_guards.create(self.engine, checkfirst=True)
        guard.execution_requests.create(self.engine, checkfirst=True)
        self.sessions = sessionmaker(self.engine)

    def tearDown(self):
        guard.execution_requests.drop(self.engine)
        guard.execution_guards.drop(self.engine)
        self.engine.dispose()
        self.temp.cleanup()

    def test_cross_session_and_user_busy_does_not_leak(self):
        with self.sessions() as db:
            acquire(db); db.commit()
        with self.sessions() as db:
            with self.assertRaises(service.ChatError):
                acquire(db, 'second', conversation_id='other', owner_id='bob')
            db.rollback()
            row = guard.read(db, 'project', 'BUG-0044-test')
            self.assertIsNone(guard.public_state(row, 'bob')['view_conversation_id'])
            self.assertFalse(guard.public_state(row, 'alice')['can_send'])

    def test_terminal_and_lease_loss_do_not_release(self):
        for status in ['failed', 'stopped', 'unknown']:
            with self.subTest(status=status), self.sessions() as db:
                acquire(db, status, object_id=status)
                guard.terminal(db, status, status); db.commit()
                row = guard.read(db, 'project', status)
                self.assertEqual(row['confirmed_stage'], 'approved')
                self.assertFalse(confirm(db, row))
                self.assertFalse(confirm(db, row, recovery=True, execution_ended=False))
                with self.assertRaises(service.ChatError): acquire(db, 'second', object_id=status)

    def test_success_needs_matching_business_and_sync_evidence(self):
        with self.sessions() as db:
            acquire(db); guard.terminal(db, 'first', 'completed'); db.commit()
            row = guard.read(db, 'project', 'BUG-0044-test')
            for override in [dict(business_valid=False), dict(sync_valid=False),
                             dict(current_revision='changed'), dict(execution_ended=False)]:
                self.assertFalse(confirm(db, row, **override))
            self.assertEqual(guard.read(db, 'project', 'BUG-0044-test')['state'], 'needs_review')
            self.assertTrue(confirm(db, row))

    def test_recovery_and_old_callback_fencing(self):
        with self.sessions() as db:
            acquire(db); guard.terminal(db, 'first', 'failed'); db.commit()
            old = guard.read(db, 'project', 'BUG-0044-test')
            self.assertTrue(confirm(db, old, recovery=True))
            self.assertEqual(guard.read(db, 'project', 'BUG-0044-test')['terminal_status'], 'failed')
            new = acquire(db, 'second'); db.commit()
            self.assertEqual(new['version'], old['version'] + 1)
            self.assertEqual(guard.terminal(db, 'first', 'completed'), 0)
            self.assertFalse(confirm(db, old, recovery=True))
            self.assertEqual(guard.read(db, 'project', 'BUG-0044-test')['operation_id'], 'second')

    def test_unknown_requires_authoritative_terminal_before_recovery(self):
        with self.sessions() as db:
            acquire(db)
            guard.terminal(db, 'first', 'unknown')
            row = guard.read(db, 'project', 'BUG-0044-test')
            self.assertFalse(confirm(db, row, recovery=True))
            guard.terminal(db, 'first', 'completed')
            self.assertTrue(confirm(db, row))
            self.assertEqual(guard.read(db, 'project', 'BUG-0044-test')['state'], 'validated')

    def test_cross_conversation_idempotency_survives_newer_operation(self):
        with self.sessions() as db:
            acquire(db, client_request_id='key', request_fingerprint='same')
            guard.terminal(db, 'first', 'completed')
            self.assertTrue(confirm(db, guard.read(db,'project','BUG-0044-test')))
            acquire(db, 'newer'); db.commit()
            with self.assertRaises(guard.Replay) as replay:
                acquire(db, 'duplicate', conversation_id='different', client_request_id='key', request_fingerprint='same')
            self.assertEqual(replay.exception.operation_id, 'first')
            db.rollback()
            with self.assertRaises(service.ChatError):
                acquire(db, 'conflict', client_request_id='key', request_fingerprint='different')

    def test_no_write_recovery_does_not_advance_stage(self):
        for status in ('completed', 'failed', 'stopped'):
            with self.subTest(status=status):
                with self.sessions() as db:
                    row = acquire(db, 'first-'+status, object_id='BUG-'+status)
                    guard.terminal(db, 'first-'+status, status)
                    values = dict(scope_key='project', object_id='BUG-'+status,operation_id='first-'+status,version=row['version'])
                    self.assertFalse(guard.restore_without_write(db, **values, current_revision='changed'))
                    self.assertTrue(guard.restore_without_write(db, **values, current_revision='before'))
                    restored = guard.read(db, 'project', 'BUG-'+status)
                    self.assertEqual(restored['confirmed_stage'], 'approved')
                    self.assertEqual(restored['terminal_status'], status)
                    self.assertEqual(acquire(db, 'second-'+status, object_id='BUG-'+status)['operation_id'], 'second-'+status)

    def test_verified_zero_write_retry_is_fenced_and_keeps_original_terminal(self):
        with self.sessions() as db:
            row = acquire(db, 'zero-write', object_id='REQ-zero-write')
            guard.terminal(db, 'zero-write', 'completed')
            values = dict(scope_key='project', object_id='REQ-zero-write', operation_id='zero-write', version=row['version'])
            self.assertFalse(guard.restore_without_write(db, **values, current_revision='new-ready', verified_baseline_revision='wrong'))
            self.assertTrue(guard.restore_without_write(db, **values, current_revision='new-ready', verified_baseline_revision='before'))
            restored = guard.read(db, 'project', 'REQ-zero-write')
            self.assertEqual(restored['result_revision'], 'new-ready')
            self.assertEqual(restored['terminal_status'], 'completed')
            self.assertEqual(restored['confirmed_stage'], 'approved')
            self.assertFalse(guard.restore_without_write(db, **values, current_revision='late', verified_baseline_revision='before'))

    def test_transaction_rollback_does_not_leave_claim(self):
        with self.sessions() as db:
            acquire(db); db.rollback()
        with self.sessions() as db:
            self.assertEqual(acquire(db, 'second')['operation_id'], 'second')
            db.commit()

    def test_request_rollback_keeps_admission_retryable(self):
        from sqlalchemy import update
        # Admission writes the conversation fence before acquiring the guard.
        with self.sessions() as db:
            db.execute(update(guard.execution_guards).values(updated_at='fence'))
            acquire(db, client_request_id='rolled-back', request_fingerprint='same')
            db.rollback()
        with self.sessions() as db:
            self.assertIsNone(guard.request(db, 'project', 'BUG-0044-test', 'alice', 'rolled-back'))
            acquire(db, 'retry', client_request_id='rolled-back', request_fingerprint='same')
            db.commit()

    def test_external_validation_requires_consistent_governance_facts(self):
        from types import SimpleNamespace
        from app.governance.execution_context import reconcile_external
        from app.governance.snapshot import Snapshot
        import yaml
        oid = 'BUG-0044-test'; base = f'issues/bugs/review/{oid}'
        def doc(data): return ('---\n'+yaml.safe_dump(data)+'---\n# 测试缺陷\n').encode()
        files = {'issues/bugs/_registry.yaml':yaml.safe_dump(dict(entries=[dict(id=oid,path=base,status='approved')])).encode(),
                 f'{base}/trace.md':doc(dict(status='approved')),
                 f'{base}/bug.md':doc(dict(status='approved',title='测试缺陷'))}
        project = SimpleNamespace(key='project')
        with self.sessions() as db:
            reconcile_external(db, project, oid, 'approved', Snapshot(files,'invalid'))
            self.assertEqual(guard.read(db,'project',oid)['state'], 'needs_review')
            files[f'{base}/review.md'] = doc(dict(status='approved'))
            reconcile_external(db, project, oid, 'approved', Snapshot(files,'valid'))
            row = guard.read(db,'project',oid)
            self.assertEqual(row['state'],'idle')
            self.assertIsNone(row['operation_id'])
            self.assertEqual(row['confirmed_stage'],'approved')
            acquire(db)
            reconcile_external(db, project, oid, 'approved', Snapshot(files,'later'))
            self.assertEqual(guard.read(db,'project',oid)['state'],'running')

    def test_projects_are_isolated_and_mysql_ddl_compiles(self):
        with self.sessions() as db:
            acquire(db); acquire(db, 'second', scope_key='another-project'); db.commit()
        ddl = str(CreateTable(guard.execution_guards).compile(dialect=mysql.dialect()))
        self.assertIn('PRIMARY KEY (scope_key, object_id)', ddl)

    def test_concurrent_connections_accept_only_one(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        barrier = Barrier(2)
        def attempt(op):
            with self.sessions() as db:
                barrier.wait(timeout=5)
                try:
                    acquire(db, op); db.commit(); return True
                except service.ChatError:
                    db.rollback(); return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(attempt, ['left', 'right']))
        self.assertEqual(sorted(results), [False, True])

    def test_competing_processes_accept_one_and_leave_durable_owner(self):
        import multiprocessing
        context = multiprocessing.get_context('spawn')
        start, results = context.Event(), context.Queue()
        url = self.engine.url.render_as_string(hide_password=False)
        processes = [context.Process(target=process_attempt, args=(url, start, results, op))
                     for op in ['process-left', 'process-right']]
        for process in processes:
            process.start()
        start.set()
        try:
            outcomes = [results.get(timeout=20) for _ in processes]
            self.assertEqual(sorted(outcomes), ['accepted', 'busy'])
            for process in processes:
                process.join(timeout=5)
                self.assertEqual(process.exitcode, 0)
            with self.sessions() as db:
                self.assertIn(guard.read(db, 'project', 'BUG-0044-test')['operation_id'],
                              ['process-left', 'process-right'])
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join()
            results.close()

    def test_result_validator_requires_sprint_bidirectional_membership(self):
        import yaml
        from app.governance.execution_validation import validate_result
        oid = 'BUG-0044-test'
        base = f'issues/bugs/review/{oid}'
        def doc(data): return ('---\n' + yaml.safe_dump(data) + '---\n# 测试缺陷\n').encode()
        files = {
            'issues/bugs/_registry.yaml': yaml.safe_dump({'entries': [dict(id=oid, path=base, status='in_sprint')]}).encode(),
            f'{base}/trace.md': doc(dict(status='in_sprint', iteration='sprint-010')),
            f'{base}/bug.md': doc(dict(title='测试缺陷', status='in_sprint')),
            'iterations/change/sprint-010/sprint.yaml': yaml.safe_dump(dict(bugs=[oid])).encode(),
        }
        self.assertTrue(validate_result(files, oid, 'sprint-propose'))
        files['iterations/change/sprint-010/sprint.yaml'] = b'bugs: []'
        self.assertFalse(validate_result(files, oid, 'sprint-propose'))
        files['issues/bugs/_registry.yaml'] = b'entries: ['
        self.assertFalse(validate_result(files, oid, 'sprint-propose'))

class AdmissionTests(unittest.TestCase):
    def test_enqueue_is_atomic_with_object_guard_and_worker_terminal(self):
        from sqlalchemy import text, select, func
        from unittest.mock import patch
        from app.chat.schema import migrate, conversations, turns
        from app.chat.admission import enqueue
        from app.chat import worker
        import json
        with tempfile.TemporaryDirectory() as directory:
            engine = create_engine(f'sqlite:///{directory}/chat.db')
            with engine.begin() as conn:
                conn.execute(text('CREATE TABLE admin_users (id VARCHAR(64) PRIMARY KEY)'))
                conn.execute(text("CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, name VARCHAR(80), owner_id VARCHAR(64), status VARCHAR(24), deleted_at VARCHAR(32), expires_at VARCHAR(32))"))
                conn.execute(text('CREATE TABLE admin_space_members (id VARCHAR(64) PRIMARY KEY, space_id VARCHAR(64), user_id VARCHAR(64), role VARCHAR(32))'))
                conn.execute(text("INSERT INTO admin_users VALUES ('alice')"))
                conn.execute(text("INSERT INTO admin_spaces (id,name,owner_id,status) VALUES ('space','Test','alice','ACTIVE')"))
            migrate(engine); migrate(engine)
            sessions = sessionmaker(engine)
            context = dict(scope_key='project', action='sprint-propose', baseline_revision='before', objects=[('BUG-0044-test','approved')])
            limits = dict(user_concurrency=5, space_concurrency=5, user_monthly_tokens=10000, space_monthly_tokens=20000,
                          user_storage_bytes=1000000, space_storage_bytes=2000000, turn_reserved_tokens=100, turn_reserved_bytes=100000)
            with patch.dict('os.environ', {'MOONBOX_CHAT_REPOSITORIES': json.dumps([dict(id='repo',space_id='space')])}), patch('app.governance.execution_context.prepare', return_value=context):
                with sessions() as db:
                    first = service.create_conversation(db, 'alice', 'space', 'repo', 'first')
                    second = service.create_conversation(db, 'alice', 'space', 'repo', 'second')
                    turn = enqueue(db, 'alice', first['id'], 'one', 'synthetic', limits)
                    self.assertEqual(enqueue(db, 'alice', first['id'], 'one', 'synthetic', limits)['id'], turn['id'])
                    from app.chat.schema import task_trace_spans
                    spans = list(db.scalars(select(task_trace_spans.c.metadata).where(task_trace_spans.c.span_name=='governance.object_guard')))
                    self.assertEqual(len(spans), 1)
                    self.assertEqual(json.loads(spans[0])['result'], 'admitted')
                    self.assertNotIn('synthetic', spans[0])
                    with patch('app.chat.observability._metadata', side_effect=ValueError('synthetic telemetry failure')):
                        with self.assertLogs('app.governance.execution_guard', level='WARNING'):
                            guard.observe(db, turn['id'], 'test_failure')
                    self.assertEqual(guard.read(db,'project','BUG-0044-test')['state'], 'running')
                    with self.assertRaises(service.ChatError): enqueue(db, 'alice', second['id'], 'two', 'synthetic', limits)
                    db.rollback()
                    self.assertEqual(db.scalar(select(func.count()).select_from(turns)), 1)
                    self.assertIsNone(db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==second['id'])))
                    token = worker.claim(db, 'test-worker')
                    self.assertTrue(worker.record_event(db, token, 'done', 'execution.state', {'status':'completed'}, terminal='completed'))
                    self.assertEqual(guard.read(db,'project','BUG-0044-test')['state'], 'needs_review')
                    with self.assertRaises(service.ChatError): enqueue(db, 'alice', second['id'], 'three', 'synthetic', limits)
                    # The files have advanced, but the product must keep the confirmed stage.
                    import yaml
                    from types import SimpleNamespace
                    from app.governance.reader import ProjectReader
                    from app.governance.snapshot import stable
                    root = Path(directory) / 'repo'
                    oid = 'BUG-0044-test'
                    base = f'issues/bugs/review/{oid}'
                    for folder in ['requirements','bugs']:
                        target = root / 'issues' / folder
                        target.mkdir(parents=True)
                        entries = [dict(id=oid, title='阶段门禁测试缺陷', status='in_sprint', path=base)] if folder=='bugs' else []
                        (target/'_registry.yaml').write_text(yaml.safe_dump(dict(entries=entries), allow_unicode=True))
                    for name in ['trace.md','bug.md','acceptance.md','root-cause.md']:
                        target = root / base / name; target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_text('---\ntitle: 阶段门禁测试缺陷\nstatus: in_sprint\niteration: sprint-010\n---\n# 阶段门禁测试缺陷\n')
                    project = SimpleNamespace(root=root, key='project', space_id='space', repository_id='repo', binding_revision='test', readonly=False)
                    reader = ProjectReader(db, 'alice', project)
                    with patch.object(reader, 'snapshot', return_value=stable(root)), patch('app.governance.scope.authorize', return_value=project):
                        card = reader.call('build_requirement_center_context').issues[0]
                    self.assertEqual(card.stage, 'approved')
                    self.assertEqual(card.execution_state, 'needs_review')
                    self.assertFalse(card.can_send)
                    self.assertEqual(card.view_conversation_id, first['id'])
                    from app.governance.preparation import prepare_object_session
                    bindings = json.dumps([dict(id='repo',space_id='space',governance_root=str(root))])
                    with patch.dict('os.environ', {'MOONBOX_CHAT_REPOSITORY_BINDINGS': bindings}), patch('app.governance.scope.authorize', return_value=project):
                        result = prepare_object_session(db, 'alice', 'space', 'repo', oid, action='open-chat')
                    self.assertEqual(result['conversation_id'], first['id'])
                    self.assertFalse(result['can_send'])
                    self.assertEqual(db.scalar(select(func.count()).select_from(conversations)), 2)
            engine.dispose()

if __name__ == '__main__':
    unittest.main()
