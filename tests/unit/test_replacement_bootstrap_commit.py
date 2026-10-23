"""The new policy stays hidden until every observed installation checkpoint."""
from datetime import datetime,timedelta,timezone
import json
from sqlalchemy import insert,select,delete
import pytest
from test_replacement_authorization import context
from app.chat.service import identity
from app.chat.schema import governance_project_locks as locks
from app.governance.replacement_schema import activations
from app.governance import replacement_bootstrap_commit as bootstrap


def prepare(context):
    db,project,*_=context
    locks.create(db.get_bind(),checkfirst=True)
    db.execute(delete(activations))
    db.execute(insert(activations).values(**identity(),scope_key=project.key,binding_revision=project.binding_revision,
        policy_version='policy-v1',state='authorized',manifest_hash='d'*64,
        manifest=json.dumps({'expected_digest':'e'*64}),operation_id='install',revision=2))
    db.commit();return db,project


def test_only_completed_installation_publishes_active(context):
    db,project=prepare(context)
    fence=bootstrap.claim(db,project,'install',2,'a'*64);db.commit()
    for stage in ('merge_verified','move_verified','synced'):
        bootstrap.checkpoint(db,project,'install',fence,stage,'e'*64,'e'*64);db.commit()
        assert db.scalar(select(activations.c.state))=='activating'
    bootstrap.checkpoint(db,project,'install',fence,'completed','e'*64,'e'*64);db.commit()
    assert db.scalar(select(activations.c.state))=='active'
    assert db.scalar(select(locks.c.operation_id)) is None


def test_unknown_effect_and_out_of_order_checkpoint_stay_blocked(context):
    db,project=prepare(context)
    fence=bootstrap.claim(db,project,'install',2,'a'*64);db.commit()
    with pytest.raises(ValueError):bootstrap.checkpoint(db,project,'install',fence,'completed','e'*64,'e'*64)
    with pytest.raises(ValueError):bootstrap.checkpoint(db,project,'install',fence,'merge_verified','f'*64,'f'*64)
    assert db.scalar(select(activations.c.state))=='activating'


def test_expired_worker_is_fenced_and_only_original_operation_renews(context):
    db,project=prepare(context)
    fence=bootstrap.claim(db,project,'install',2,'a'*64);db.commit()
    with pytest.raises(ValueError):bootstrap.assert_fence(db,project,'install',fence,now=datetime.now(timezone.utc)+timedelta(minutes=6))
    with pytest.raises(ValueError):bootstrap.renew(db,project,'another-install')
    new_fence=bootstrap.renew(db,project,'install');db.commit()
    assert new_fence>fence
    with pytest.raises(ValueError):bootstrap.assert_fence(db,project,'install',fence)
    assert bootstrap.assert_fence(db,project,'install',new_fence)['state']=='activating'
