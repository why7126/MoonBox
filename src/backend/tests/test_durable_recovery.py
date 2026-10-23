"""REQ-0047 persistent policy invariants with real SQL transactions."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
import os
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.chat.service import ChatError
from app.governance import durable_recovery as p
from app.governance.recovery_schema import operations, attempts


@pytest.fixture
def database(tmp_path):
    engine = create_engine(os.environ.get('CHAT_TEST_DATABASE_URL') or 'sqlite:///' + str(tmp_path / 'recovery.sqlite'))
    # CHAT_TEST_DATABASE_URL is supplied only by the disposable matrix runner.
    attempts.drop(engine, checkfirst=True); operations.drop(engine, checkfirst=True)
    operations.create(engine); attempts.create(engine)
    with Session(engine) as db:
        oid = p.create(db, actor='actor', project=SimpleNamespace(key='scope', binding_revision='binding'),
            parent={'id':'conversation','space_id':'space','repository_id':'repository'},
            action='req-review', object_id='REQ-9000-isolated', request_key='first', request_hash='hash', source_hash='source')
        db.execute(update(operations).where(operations.c.id == oid).values(
            recovery_expires_at=p.stamp(datetime.now(timezone.utc)+timedelta(days=1)),
            state='blocked', reason_code='storage_unavailable', execution_terminal='failed'))
        db.commit()
    yield engine, oid
    engine.dispose()


def test_claim_is_idempotent_and_different_input_conflicts(database):
    engine, oid = database
    with Session(engine) as db:
        attempt, won = p.claim(db, oid, 1, 'retry')
        db.commit()
    with Session(engine) as db:
        same, won_again = p.claim(db, oid, 1, 'retry')
        assert same['id'] == attempt['id'] and won and not won_again
        with pytest.raises(ChatError): p.claim(db, oid, 2, 'retry')
        with pytest.raises(ChatError): p.claim(db, oid, 1, 'other')
        assert p.row(db, oid)['manual_count'] == 1


def test_retry_budget_survives_connections_and_stage_changes(database):
    engine, oid = database
    clock = datetime.now(timezone.utc)
    for i in range(3):
        clock += timedelta(seconds=31)
        with Session(engine) as db:
            current = p.row(db, oid)
            attempt, _ = p.claim(db, oid, current['version'], f'retry-{i}', kind='auto', now=clock)
            p.release(db, oid, attempt, state='blocked', reason='storage_unavailable', now=clock)
            db.commit()
    with Session(engine) as db:
        current = p.row(db, oid)
        assert current['auto_retry_count'] == 3 and current['next_retry_at'] is None
        with pytest.raises(ChatError): p.claim(db, oid, current['version'], 'fourth', kind='auto', now=clock)
        manual, _ = p.claim(db, oid, current['version'], 'explicit', now=clock)
        p.release(db, oid, manual, state='blocked')
        assert p.row(db, oid)['auto_retry_count'] == 3
        assert p.row(db, oid)['manual_count'] == 1


def test_stopped_and_expired_never_auto_resume(database):
    engine, oid = database
    with Session(engine) as db:
        db.execute(update(operations).values(execution_terminal='stopped'))
        with pytest.raises(ChatError): p.claim(db, oid, 1, 'auto', kind='auto')
        db.execute(update(operations).values(recovery_expires_at='2000-01-01T00:00:00+00:00'))
        with pytest.raises(ChatError): p.claim(db, oid, 1, 'manual')


def test_stale_fence_cannot_release_new_claim(database):
    engine, oid = database
    with Session(engine) as db:
        attempt, _ = p.claim(db, oid, 1, 'first')
        p.release(db, oid, attempt, state='blocked')
        newer, _ = p.claim(db, oid, p.row(db, oid)['version'], 'second')
        with pytest.raises(ChatError): p.release(db, oid, attempt, state='completed')
        assert p.row(db, oid)['lease_owner'] == newer['id']


def test_earliest_expiry_and_compatibility():
    terminal='2026-10-19T00:00:00+00:00'
    assert p.expiry(terminal, {'executor_delete_seconds':3600,'backup_expiry_seconds':None}) == '2026-10-19T01:00:00+00:00'
    assert p.expiry(terminal, None) is None
    assert p.expiry(terminal, {'executor_delete_seconds':None,'backup_expiry_seconds':None}, '2026-10-19T00:30:00+00:00') == '2026-10-19T00:30:00+00:00'
    version={'schema_min':1,'schema_max':2,'actions':['req-review']}
    assert p.compatible([version,version,version], 'req-review')
    assert not p.compatible([version,{},version], 'req-review')
    assert not p.compatible([version,version,version], 'opsx-apply')


def test_mysql_schema_keeps_unique_constraints():
    for table in (operations, attempts):
        sql=str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert 'UNIQUE' in sql and 'PRIMARY KEY' in sql


def test_runtime_capabilities_fail_closed_and_accept_live_peers(tmp_path, monkeypatch):
    from app.governance import recovery_capabilities as c
    private=tmp_path/'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    with pytest.raises(ChatError): c.require('req-review')
    c.publish('worker')
    with pytest.raises(ChatError): c.require('req-review')
    c.publish('controller')
    c.require('req-review')
    now=c.time.time()
    monkeypatch.setattr(c.time, 'time', lambda: now+31)
    c.publish('controller')
    with pytest.raises(ChatError): c.require('req-review')
    # A live worker returning from a slow workspace copy refreshes itself.
    c.publish('worker');c.require('req-review')
    monkeypatch.setattr(c.time, 'time', lambda: now+62)
    c.publish('worker')
    with pytest.raises(ChatError): c.require('req-review')


def test_late_collection_cannot_reopen_completed_operation(database):
    engine, oid=database
    with Session(engine) as db:
        p.advance(db,oid,'complete',state='completed')
        p.advance(db,oid,'validation',state='active',execution_terminal='stopped')
        current=p.row(db,oid)
        assert current['stage']=='complete' and current['state']=='completed'
        assert current['execution_terminal']=='stopped'


@pytest.mark.parametrize('keys', [['one','two'], ['one','one']])
def test_concurrent_different_keys_have_single_claim(database,keys):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    engine, oid = database
    ready=Barrier(2)
    def worker(key):
        with Session(engine) as db:
            ready.wait()
            try:
                attempt, won=p.claim(db,oid,1,key)
                db.commit()
                return won
            except ChatError:
                db.rollback()
                return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes=list(pool.map(worker,keys))
    assert outcomes.count(True)==1
    with Session(engine) as db:
        assert p.row(db,oid)['manual_count']==1
        assert len(db.execute(select(attempts)).all())==1


def test_operation_creation_replay_conflict_and_candidate_ownership(database):
    engine, oid=database
    options=dict(actor='actor',project=SimpleNamespace(key='scope',binding_revision='binding'),parent={'id':'conversation','space_id':'space','repository_id':'repository'},action='req-review',object_id='REQ-9000-isolated',request_key='first',request_hash='hash',source_hash='source')
    with Session(engine) as db:
        assert p.create(db,**options)==oid
        with pytest.raises(ChatError):p.create(db,**dict(options,request_hash='changed'))
        db.execute(update(operations).where(operations.c.id==oid).values(candidate_id='candidate'))
        with pytest.raises(ChatError):p.create(db,**dict(options,request_key='different',candidate_id='candidate'))


def test_request_key_identity_is_case_and_whitespace_sensitive(database):
    engine,oid=database
    with Session(engine) as db:
        for key in ('Case','case','case '):
            attempt,won=p.claim(db,oid,p.row(db,oid)['version'],key)
            assert won
            p.release(db,oid,attempt,state='blocked')
        db.commit()
        assert len(db.execute(select(attempts)).all())==3
