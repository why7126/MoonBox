"""Single-use authorization and project fencing, within the caller transaction.

File writers must hold writer.project_lock through recheck, mutation and reread.
A checkpoint is accepted only from an observation of the expected filesystem
state; unknown results cannot advance or release the project fence.
"""
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.schema import governance_project_locks as locks
from app.chat.service import identity
from .replacement_schema import proposals, commits, activations

STAGES = ('claimed', 'merge_verified', 'move_verified', 'synced', 'completed')


def claim(db, *, project, proposal_id, revision, actor, operation_id, input_hash,
          expected_hash, trust, now=None, request_id=None):
    current = now or datetime.now(timezone.utc)
    stamp = current.isoformat(timespec='seconds')
    previous = db.execute(select(commits).where(commits.c.id == operation_id)).mappings().first()
    if previous:
        if (previous['proposal_id'], previous['scope_key'], previous['actor_id'], previous['input_hash'], previous['expected_hash']) != (proposal_id, project.key, actor, input_hash, expected_hash):
            raise ValueError('operation_identity_conflict')
        return dict(previous)
    policy = db.execute(select(activations).where(activations.c.scope_key == project.key)).mappings().first()
    if not policy or policy['state'] != 'active' or policy['policy_version'] != trust.policy_version or policy['binding_revision'] != project.binding_revision:
        raise ValueError('policy_not_active')
    row = db.execute(select(proposals).where(proposals.c.id == proposal_id, proposals.c.scope_key == project.key)).mappings().first()
    if not row or row['state'] != 'approved' or row['revision'] != revision or row['binding_revision'] != project.binding_revision:
        raise ValueError('authorization_changed')
    trust.verify(json.loads(row['receipt']), purpose='replacement.approve', bindings={
        'project_id': project.key, 'binding_revision': project.binding_revision, 'proposal_id': proposal_id,
        'proposal_digest': row['digest'], 'revision': revision, 'actor_id': row['owner_id'],
        'policy_version': trust.policy_version, 'release_digest': trust.release_digest}, now=current)
    # Caller must reauthorize both current writer and recorded approving owner.
    from sqlalchemy import text
    owner = db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'), {'space': project.space_id})
    if owner != row['owner_id']:
        raise ValueError('authorization_owner_changed')
    if db.scalar(select(locks.c.scope_key).where(locks.c.scope_key == project.key)) is None:
        try:
            with db.begin_nested():
                db.execute(insert(locks).values(scope_key=project.key, fencing_token=0, updated_at=stamp))
        except IntegrityError:
            pass
    won = db.execute(update(locks).where(locks.c.scope_key == project.key, locks.c.operation_id.is_(None)).values(
        operation_id=operation_id, fencing_token=locks.c.fencing_token+1, worker_id=actor, updated_at=stamp)).rowcount
    if won != 1:
        raise ValueError('project_archive_busy')
    fence = db.scalar(select(locks.c.fencing_token).where(locks.c.scope_key == project.key))
    won = db.execute(update(proposals).where(proposals.c.id == proposal_id,
        proposals.c.revision == revision, proposals.c.state == 'approved').values(
            state='claimed', revision=revision+1, operation_id=operation_id, updated_at=stamp)).rowcount
    if won != 1:
        raise ValueError('authorization_changed')
    operation = {**identity(), 'id': operation_id, 'scope_key': project.key, 'proposal_id': proposal_id,
                 'actor_id': actor, 'stage': 'claimed', 'fence': fence,
                 'lease_until': (current+timedelta(minutes=5)).isoformat(timespec='seconds'),
                 'input_hash': input_hash, 'expected_hash': expected_hash, 'revision': 1}
    db.execute(insert(commits).values(**operation))
    from .replacement_observability import trace
    trace(db, proposal_id, 'claimed', actor=actor, request_id=request_id)
    return operation


def assert_fence(db, operation_id, fence, *, now=None):
    current = now or datetime.now(timezone.utc)
    row = db.execute(select(commits).where(commits.c.id == operation_id)).mappings().one()
    lock = db.execute(select(locks).where(locks.c.scope_key == row['scope_key'])).mappings().one()
    if (row['fence'] != fence or lock['fencing_token'] != fence or lock['operation_id'] != operation_id
            or datetime.fromisoformat(row['lease_until']) <= current or row['stage'] == 'completed'):
        raise ValueError('stale_archive_executor')
    return row


def checkpoint(db, *, operation_id, fence, expected_revision, stage, observed_hash, now=None, request_id=None):
    row = assert_fence(db, operation_id, fence, now=now)
    if stage not in STAGES or STAGES.index(stage) != STAGES.index(row['stage'])+1 or row['revision'] != expected_revision:
        raise ValueError('invalid_archive_checkpoint')
    if not observed_hash or observed_hash != row['expected_hash']:
        raise ValueError('archive_effect_unverified')
    won = db.execute(update(commits).where(commits.c.id == operation_id, commits.c.revision == expected_revision,
        commits.c.fence == fence).values(stage=stage, revision=expected_revision+1, observed_hash=observed_hash)).rowcount
    if won != 1: raise ValueError('stale_archive_executor')
    if stage == 'completed':
        if db.execute(update(proposals).where(proposals.c.id == row['proposal_id'], proposals.c.operation_id == operation_id,
            proposals.c.state == 'claimed').values(state='completed')).rowcount != 1:
            raise ValueError('archive_authorization_changed')
        if db.execute(update(locks).where(locks.c.scope_key == row['scope_key'], locks.c.operation_id == operation_id,
            locks.c.fencing_token == fence).values(operation_id=None, worker_id=None)).rowcount != 1:
            raise ValueError('archive_fence_changed')
    from .replacement_observability import trace
    trace(db, row['proposal_id'], stage, actor=row['actor_id'], request_id=request_id)
