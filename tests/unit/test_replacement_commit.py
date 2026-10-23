"""Authorization races and stale archive executors retain blocking facts."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert, select, text
import pytest
from test_replacement_authorization import context, decision
from app.chat.schema import governance_project_locks as locks
from app.chat.service import identity, ChatError
from app.governance.replacement_schema import activations, proposals
from app.governance.replacement_commit import claim, checkpoint, assert_fence


def ready(context):
    db, project, trust, sign=context
    project.space_id='space'; project.repository_id='repo'
    locks.create(db.get_bind(), checkfirst=True)
    db.execute(text('CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, owner_id VARCHAR(64))'))
    db.execute(text("INSERT INTO admin_spaces (id,owner_id) VALUES ('space','owner')"))
    decision(context); db.commit()
    return dict(project=project,proposal_id='proposal',revision=2,actor='owner',operation_id='operation',
        input_hash='e'*64,expected_hash='f'*64,trust=trust)


def test_claim_wins_revocation_cannot_report_rollback(context):
    db,*_=context; args=ready(context)
    op=claim(db,**args);db.commit()
    assert claim(db,**args)['id']==op['id']
    with pytest.raises(ChatError,match='已领取'): decision(context,action='revoke',expected_revision=3,request_key='revoke')
    assert db.scalar(select(proposals.c.state))=='claimed'


def test_revoke_wins_claim_does_not_write(context):
    db,*_=context;args=ready(context)
    decision(context,action='revoke',expected_revision=2,request_key='revoke');db.commit()
    with pytest.raises(ValueError,match='authorization_changed'): claim(db,**args)
    db.rollback();assert db.scalar(select(proposals.c.state))=='revoked'
    assert not db.execute(select(locks)).first()


def test_stale_fence_lease_and_unverified_results_block(context):
    db,*_=context;args=ready(context);op=claim(db,**args);db.commit()
    with pytest.raises(ValueError): assert_fence(db,op['id'],op['fence']+1)
    with pytest.raises(ValueError): assert_fence(db,op['id'],op['fence'],now=datetime.now(timezone.utc)+timedelta(minutes=6))
    with pytest.raises(ValueError,match='effect_unverified'):
        checkpoint(db,operation_id=op['id'],fence=op['fence'],expected_revision=1,stage='merge_verified',observed_hash='0'*64)
    assert db.scalar(select(proposals.c.state))=='claimed'


def test_owner_change_invalidates_unclaimed_authorization(context):
    db,*_=context;args=ready(context)
    db.execute(text("UPDATE admin_spaces SET owner_id='new-owner'"));db.commit()
    with pytest.raises(ValueError,match='owner_changed'):claim(db,**args)
