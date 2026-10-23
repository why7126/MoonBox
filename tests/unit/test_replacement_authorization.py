"""Transactional receipts, replay, revocation and historical trust checks."""
import base64
from datetime import datetime, timedelta, timezone
import json
import os
from types import SimpleNamespace

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import Session
from app.chat.service import identity, ChatError
from app.governance.replacement_proof import canonical
from app.governance.replacement_trust import Trust
from app.governance.replacement_schema import TABLES, proposals, events, activations
from app.governance.rule_change_schema import events as rule_change_events
from app.governance.replacement_authorization import decide


@pytest.fixture
def context(tmp_path):
    url = os.environ.get('MOONBOX_REPLACEMENT_TEST_DATABASE') or 'sqlite:///'+str(tmp_path/'authorization.sqlite')
    engine = create_engine(url)
    if engine.dialect.name != 'sqlite':
        assert engine.url.database == 'req0050_test', 'isolated database required'
    for table in TABLES: table.create(engine, checkfirst=True)
    rule_change_events.create(engine, checkfirst=True)
    from app.governance.replacement_schema import install_audit_guards
    install_audit_guards(engine)
    install_audit_guards(engine)
    key = Ed25519PrivateKey.generate()
    pub = base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
    trust = Trust({'test-key': pub}, frozenset(), {}, 'policy-v1', 'f'*64, {f'replacement.{action}': ['test-key'] for action in ('approve', 'reject', 'revoke')})
    def sign(payload):
        return {'key_id': 'test-key', 'payload': payload, 'signature': base64.b64encode(key.sign(canonical(payload))).decode()}
    project = SimpleNamespace(key='a'*64, binding_revision='b'*64)
    db = Session(engine)
    db.execute(insert(activations).values(**identity(),scope_key=project.key,binding_revision=project.binding_revision,
        policy_version=trust.policy_version,state='active',manifest_hash='d'*64,manifest='{}',revision=1))
    db.execute(insert(proposals).values(**(identity() | {'id': 'proposal'}), scope_key=project.key, space_id='space',
        repository_id='repo', binding_revision=project.binding_revision, change_id='sample', digest='c'*64,
        body='{}', prepared_by='owner', revision=1, state='prepared'))
    db.commit()
    yield db, project, trust, sign
    db.close()
    for table in reversed(TABLES): table.drop(engine, checkfirst=True)
    rule_change_events.drop(engine, checkfirst=True)
    from app.chat.schema import governance_project_locks
    governance_project_locks.drop(engine, checkfirst=True)
    from sqlalchemy import text
    with engine.begin() as connection: connection.execute(text('DROP TABLE IF EXISTS admin_spaces'))
    engine.dispose()


def decision(context, **kw):
    db, project, trust, sign = context
    args = dict(project=project, proposal_id='proposal', actor_id='owner', action='approve', expected_revision=1,
                proposal_digest='c'*64, request_key='first', sign=sign, trust=trust)
    return decide(db, **(args|kw))


def test_atomic_approval_replay_and_revoke(context):
    db, project, trust, sign = context
    result = decision(context); db.commit()
    assert result['revision'] == 2
    assert decision(context)['replayed']
    with pytest.raises(ChatError): decision(context, proposal_digest='d'*64)
    decision(context, action='revoke', expected_revision=2, request_key='second'); db.commit()
    assert db.scalar(select(proposals.c.state)) == 'revoked'
    assert len(db.execute(select(events)).all()) == 2
    with pytest.raises(ChatError): decision(context, request_key='third')


@pytest.mark.parametrize('state',['prepared','authorized','activating'])
def test_ordinary_approval_requires_completed_policy_installation(context,state):
    from sqlalchemy import update
    db,*_=context
    db.execute(update(activations).values(state=state));db.commit()
    with pytest.raises(ValueError,match='policy_not_active'):decision(context)
    db.rollback()
    assert db.scalar(select(proposals.c.state))=='prepared'
    assert not db.execute(select(events)).first()


def test_receipt_expiry_history_and_revoked_key(context):
    db, project, trust, sign = context
    now = datetime(2026, 10, 22, tzinfo=timezone.utc)
    receipt = decision(context, now=now)['receipt']
    trust.verify(receipt, purpose='replacement.approve', bindings={'project_id': project.key}, now=now+timedelta(hours=23))
    with pytest.raises(ValueError): trust.verify(receipt, purpose='replacement.approve', bindings={}, now=now+timedelta(hours=24))
    trust.verify(receipt, purpose='replacement.approve', bindings={}, historical=True, now=now+timedelta(days=365))
    revoked = Trust(trust.keys, frozenset({'test-key'}), {}, trust.policy_version, trust.release_digest, trust.purpose_keys)
    with pytest.raises(ValueError): revoked.verify(receipt, purpose='replacement.approve', bindings={}, historical=True)
    with pytest.raises(ValueError): trust.verify(receipt, purpose='bootstrap.owner', bindings={}, historical=True)
    with pytest.raises(ValueError): trust.verify(receipt, purpose='replacement.approve', bindings={'project_id': 'other'}, historical=True)


def test_signature_failure_does_not_write(context):
    db, *_ = context
    with pytest.raises(ValueError): decision(context, sign=lambda payload: {'key_id':'test-key', 'payload':payload, 'signature':'eA=='})
    db.rollback()
    assert db.scalar(select(proposals.c.state)) == 'prepared'
    assert not db.execute(select(events)).first()


def test_stale_revision_cannot_overwrite_decision(context):
    db, *_ = context
    decision(context); db.commit()
    with pytest.raises(ChatError): decision(context, action='reject', reason='拒绝', request_key='other')
    assert db.scalar(select(proposals.c.state)) == 'approved'


def test_authorization_events_are_database_immutable(context):
    from sqlalchemy import update, delete
    from sqlalchemy.exc import DatabaseError
    db,*_=context
    decision(context);db.commit()
    for statement in (update(events).values(actor_id='forged'),delete(events)):
        with pytest.raises(DatabaseError): db.execute(statement)
        db.rollback()
    assert db.scalar(select(events.c.actor_id))=='owner'


def test_concurrent_decisions_have_one_winner(context):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy.exc import OperationalError
    db,project,trust,sign=context
    engine=db.get_bind();barrier=Barrier(2)
    def run(action):
        with Session(engine) as session:
            def synchronized(payload):
                result=sign(payload);barrier.wait(timeout=10);return result
            try:
                decide(session,project=project,proposal_id='proposal',actor_id='owner',action=action,
                    expected_revision=1,proposal_digest='c'*64,request_key=action,sign=synchronized,trust=trust,reason='独立审阅')
                session.commit();return 'won'
            except (ChatError,OperationalError):
                session.rollback();return 'blocked'
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(run,['approve','reject']))
    assert sorted(results)==['blocked','won']
    db.rollback()
    assert len(db.execute(select(events)).all())==1
    assert db.scalar(select(proposals.c.revision))==2
