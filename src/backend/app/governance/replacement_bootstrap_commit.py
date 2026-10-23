"""Project-fenced first installation; active is published only after observed sync."""
from datetime import datetime,timedelta,timezone
import json
from sqlalchemy import insert,select,update
from sqlalchemy.exc import IntegrityError
from app.chat.schema import governance_project_locks as locks
from .replacement_schema import activations
from .replacement_commit import STAGES


def claim(db,project,operation_id,expected_revision,input_hash,*,now=None):
    current=now or datetime.now(timezone.utc);stamp=current.isoformat(timespec='seconds')
    row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
    if row['state']!='authorized' or row['operation_id']!=operation_id or row['revision']!=expected_revision:
        raise ValueError('bootstrap_authorization_changed')
    if db.scalar(select(locks.c.scope_key).where(locks.c.scope_key==project.key)) is None:
        try:
            with db.begin_nested():db.execute(insert(locks).values(scope_key=project.key,fencing_token=0,updated_at=stamp))
        except IntegrityError:pass
    won=db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id.is_(None)).values(
        operation_id=operation_id,fencing_token=locks.c.fencing_token+1,updated_at=stamp)).rowcount
    if won!=1:raise ValueError('project_archive_busy')
    fence=db.scalar(select(locks.c.fencing_token).where(locks.c.scope_key==project.key))
    won=db.execute(update(activations).where(activations.c.id==row['id'],activations.c.revision==expected_revision,
        activations.c.state=='authorized').values(state='activating',stage='claimed',fence=fence,
        lease_until=(current+timedelta(minutes=5)).isoformat(timespec='seconds'),input_hash=input_hash,
        revision=expected_revision+1)).rowcount
    if won!=1:raise ValueError('bootstrap_authorization_changed')
    return fence


def assert_fence(db,project,operation_id,fence,*,now=None):
    row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
    lock=db.execute(select(locks).where(locks.c.scope_key==project.key)).mappings().one()
    if (row['state']!='activating' or row['operation_id']!=operation_id or row['fence']!=fence
            or lock['operation_id']!=operation_id or lock['fencing_token']!=fence or not row['lease_until']
            or datetime.fromisoformat(row['lease_until'])<=(now or datetime.now(timezone.utc))):
        raise ValueError('stale_bootstrap_executor')
    return row


def renew(db,project,operation_id,*,now=None):
    current=now or datetime.now(timezone.utc)
    row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
    if row['state']!='activating' or row['operation_id']!=operation_id:raise ValueError('bootstrap_operation_changed')
    won=db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id==operation_id,
        locks.c.fencing_token==row['fence']).values(fencing_token=row['fence']+1)).rowcount
    if won!=1:raise ValueError('bootstrap_fence_changed')
    won=db.execute(update(activations).where(activations.c.id==row['id'],activations.c.revision==row['revision']).values(
        fence=row['fence']+1,revision=row['revision']+1,lease_until=(current+timedelta(minutes=5)).isoformat(timespec='seconds'))).rowcount
    if won!=1:raise ValueError('bootstrap_operation_changed')
    return row['fence']+1


def checkpoint(db,project,operation_id,fence,stage,observed_hash,expected_hash):
    row=assert_fence(db,project,operation_id,fence)
    if (stage not in STAGES or STAGES.index(stage)!=STAGES.index(row['stage'])+1 or observed_hash!=expected_hash
            or expected_hash!=json.loads(row['manifest'])['expected_digest']):
        raise ValueError('bootstrap_effect_unverified')
    values={'stage':stage,'revision':row['revision']+1}
    if stage=='completed':values.update(state='active',archive_hash=observed_hash)
    won=db.execute(update(activations).where(activations.c.id==row['id'],activations.c.revision==row['revision'],
        activations.c.fence==fence).values(**values)).rowcount
    if won!=1:raise ValueError('bootstrap_operation_changed')
    if stage=='completed':
        if db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id==operation_id,
            locks.c.fencing_token==fence).values(operation_id=None,worker_id=None)).rowcount!=1:
            raise ValueError('bootstrap_fence_changed')
