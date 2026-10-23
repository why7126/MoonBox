"""Observed filesystem transitions for an already claimed archive operation.

Only the archive coordinator calls this under the shared project OS lock. It
never infers success from subprocess exit status, nor silently overwrites an
unknown tree. Each observation is recomputed from the source filesystem.
"""
from .replacement_inputs import replacement_delivery_hash
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update
from .replacement_schema import commits
from app.chat.schema import governance_project_locks as locks
from .archive_recovery import tree_hash, archive_paths, delta_operations, verify_delta_effects, completed_archive, delivery_input_hash


def observe(project, proposal, operation):
    root=project.root
    active=root/'openspec/changes'/proposal.successor
    archived=archive_paths(root,proposal.successor)
    if active.is_symlink() or len(archived)>1 or (active.exists() and archived):
        raise ValueError('archive_identity_ambiguous')
    folder=active if active.is_dir() else archived[0] if len(archived)==1 else None
    if folder is None or folder.is_symlink(): raise ValueError('archive_identity_missing')
    if tree_hash(folder/'specs')!=proposal.delta_sha256 or replacement_delivery_hash(folder)!=proposal.delivery_sha256:
        raise ValueError('archive_candidate_changed')
    actual=tree_hash(root/'openspec/specs')
    if actual!=operation['expected_hash']:
        if operation['stage']=='claimed' and active.is_dir():
            from .replacement_inputs import fingerprint
            if fingerprint(project,proposal)==operation['input_hash']:
                return 'unmerged'
        raise ValueError('archive_result_unknown')
    verify_delta_effects(folder/'specs',root/'openspec/specs')
    if active.is_dir(): return 'merged'
    return 'synced' if completed_archive(folder,proposal.successor) else 'moved'


def resume(db, *, project, proposal, operation_id, actor, trust, now=None):
    """Rotate fence only for the same operation after direct observation and auth.

    Lease expiry does not make the project free for another archive. Ordinary
    approval expiry does not erase a legitimately claimed operation.
    """
    from .scope import authorize
    current=authorize(db,actor,project.space_id,project.repository_id,write=True)
    if current.binding_revision!=project.binding_revision: raise ValueError('binding_changed')
    operation=db.execute(select(commits).where(commits.c.id==operation_id,commits.c.scope_key==project.key)).mappings().one()
    from .replacement_schema import proposals
    authorization=db.execute(select(proposals).where(proposals.c.id==operation['proposal_id'])).mappings().one()
    import json
    trust.verify(json.loads(authorization['receipt']),purpose='replacement.approve',bindings={
        'project_id':project.key,'binding_revision':project.binding_revision,'proposal_digest':authorization['digest'],
        'policy_version':proposal.policy_version},historical=True)
    state=observe(project,proposal,operation)
    current_time=now or datetime.now(timezone.utc)
    old_fence=operation['fence']
    # The OS lock is a required outer precondition: even a slow still-alive
    # executor retains that lock until its write and observation have ended.
    won=db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id==operation_id,
        locks.c.fencing_token==old_fence).values(fencing_token=old_fence+1,worker_id=actor,
        updated_at=current_time.isoformat(timespec='seconds'))).rowcount
    if won!=1: raise ValueError('archive_fence_changed')
    won=db.execute(update(commits).where(commits.c.id==operation_id,commits.c.fence==old_fence,
        commits.c.revision==operation['revision']).values(fence=old_fence+1,revision=operation['revision']+1,
        lease_until=(current_time+timedelta(minutes=5)).isoformat(timespec='seconds'))).rowcount
    if won!=1: raise ValueError('archive_operation_changed')
    return state,old_fence+1
