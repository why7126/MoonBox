"""Fenced ordinary archive path sharing the replacement controller's write boundary.

It never waives a rule. Controlled candidates are routed to their signed proposal;
all other candidates retain ordinary acceptance and continuous-history checks.
"""
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.service import identity
from app.chat.schema import governance_project_locks as locks
from .replacement_schema import archive_operations as operations, proposals, activations
from .replacement_proof import canonical, digest, parse
from .replacement_trust import load
from .replacement_inputs import replacement_delivery_hash
from .compatible_successor import acceptance_binding
from .replacement_permissions import authorize_write
from .archive_recovery import tree_hash, archive_paths, completed_archive, verify_delta_effects, recovery_admission
from .archive_admission import change_acceptance
from .controlled_successor import authority
from .replacement_executor import ArchiveDriver
from .writer import project_lock
from . import scope
from .archive_finalization import needs_finalize, require_finalized

STAGES = ('claimed', 'merge_verified', 'move_verified', 'synced', 'completed')


def evidence_digest(project, folder):
    if not (folder/'acceptance-plan.json').is_file():
        return None  # Legacy admission retains its independent task/sign-off gate.
    return acceptance_binding(project.root,folder,source_root=project.source_root)


def assert_fence(db, project, operation_id, fence, *, now=None):
    row=db.execute(select(operations).where(operations.c.id==operation_id,operations.c.scope_key==project.key)).mappings().one()
    lock=db.execute(select(locks).where(locks.c.scope_key==project.key)).mappings().one()
    if (row['binding_revision']!=project.binding_revision or row['fence']!=fence
            or lock['operation_id']!=operation_id or lock['fencing_token']!=fence
            or row['stage']=='completed' or datetime.fromisoformat(row['lease_until']) <= (now or datetime.now(timezone.utc))):
        raise ValueError('stale_archive_executor')
    return row


def checkpoint(db,project,operation_id,fence,stage):
    row=assert_fence(db,project,operation_id,fence)
    if stage not in STAGES or STAGES.index(stage)!=STAGES.index(row['stage'])+1:
        raise ValueError('invalid_archive_checkpoint')
    if db.execute(update(operations).where(operations.c.id==operation_id,operations.c.fence==fence,
            operations.c.revision==row['revision']).values(stage=stage,revision=row['revision']+1)).rowcount!=1:
        raise ValueError('stale_archive_executor')
    if stage=='completed':
        if db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id==operation_id,
                locks.c.fencing_token==fence).values(operation_id=None,worker_id=None)).rowcount!=1:
            raise ValueError('archive_fence_changed')
    db.commit()


def observe(project,row):
    manifest=json.loads(row['manifest']);change=row['change_id']
    active=project.root/'openspec/changes'/change;archives=archive_paths(project.root,change)
    if active.is_symlink() or len(archives)>1 or active.exists() and archives:
        raise ValueError('archive_identity_ambiguous')
    folder=active if active.is_dir() else archives[0] if len(archives)==1 else None
    if (folder is None or folder.is_symlink() or tree_hash(folder/'specs')!=manifest['delta']
            or replacement_delivery_hash(folder)!=manifest['delivery']
            or evidence_digest(project,folder)!=manifest['acceptance']):
        raise ValueError('archive_inputs_changed')
    current=tree_hash(project.root/'openspec/specs')
    if row['stage']=='claimed' and active.is_dir() and current==manifest['baseline']:
        return 'unmerged'
    if current!=manifest['expected']:raise ValueError('archive_result_unknown')
    verify_delta_effects(folder/'specs',project.root/'openspec/specs')
    return 'merged' if active.is_dir() else 'synced' if completed_archive(folder,change) else 'moved'


def acquire(db,project,actor,change,operation_id,manifest,row):
    now=datetime.now(timezone.utc);stamp=now.isoformat()
    lock=db.execute(select(locks).where(locks.c.scope_key==project.key)).mappings().first()
    if not lock:
        try:
            with db.begin_nested():db.execute(insert(locks).values(scope_key=project.key,fencing_token=0,updated_at=stamp))
        except IntegrityError:pass
        lock=db.execute(select(locks).where(locks.c.scope_key==project.key)).mappings().one()
    if lock['operation_id'] not in (None,operation_id) or row and lock['operation_id']!=operation_id:
        raise ValueError('project_archive_busy')
    fence=lock['fencing_token']+1
    if db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.fencing_token==lock['fencing_token'],
            locks.c.operation_id.is_(None) if lock['operation_id'] is None else locks.c.operation_id==operation_id).values(
                fencing_token=fence,operation_id=operation_id,worker_id=actor,updated_at=stamp)).rowcount!=1:
        raise ValueError('archive_fence_changed')
    lease=(now+timedelta(minutes=5)).isoformat()
    if row:
        if db.execute(update(operations).where(operations.c.id==operation_id,operations.c.revision==row['revision']).values(
                fence=fence,lease_until=lease,revision=row['revision']+1)).rowcount!=1:raise ValueError('archive_operation_changed')
    else:
        db.execute(insert(operations).values(**(identity()|{'id':operation_id}),scope_key=project.key,
            binding_revision=project.binding_revision,change_id=change,actor_id=actor,stage='claimed',
            manifest=canonical(manifest).decode(),fence=fence,lease_until=lease,revision=1))
    db.commit()
    return fence


def execute(db,*,actor,space_id,repository_id,change,operation_id,driver_type=ArchiveDriver):
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    with project_lock(project):
        db.commit();project=scope.authorize(db,actor,space_id,repository_id,write=True)
        # Ordinary archive admission does not depend on the retired first-installation flow.
        # Historical operations continue to verify their original release below.
        row=db.execute(select(operations).where(operations.c.scope_key==project.key,operations.c.change_id==change)).mappings().first()
        if row and (row['id']!=operation_id or row['actor_id']!=actor or row['binding_revision']!=project.binding_revision):
            raise ValueError('original_operation_required')
        with authority(db,project,actor):
            if row and row['stage']=='completed':
                manifest=json.loads(row['manifest']);folders=archive_paths(project.root,change)
                if len(folders)!=1 or (project.root/'openspec/changes'/change).exists():
                    raise ValueError('archive_history_changed')
                folder=folders[0]
                if (folder.is_symlink() or tree_hash(folder/'specs')!=manifest['delta']
                        or replacement_delivery_hash(folder)!=manifest['delivery']
                        or evidence_digest(project,folder)!=manifest['acceptance']):
                    raise ValueError('archive_history_changed')
                if not recovery_admission(project.root,change,source_root=project.source_root)['ready']:
                    raise ValueError('archive_history_changed')
                require_finalized(project.root,change)
                return {'operation_id':operation_id,'stage':'completed','replayed':True}
            driver=driver_type(project)
            if not row:
                # Approved controlled candidates must use their dedicated receipt
                # claim, never this ordinary path as an approval bypass.
                if db.scalar(select(proposals.c.id).where(proposals.c.scope_key==project.key,
                        proposals.c.change_id==change,proposals.c.state=='claimed')):
                    raise ValueError('controlled_proposal_required')
                admission=change_acceptance(project.root,change,source_root=project.source_root)
                if not admission['ready']:
                    raise ValueError(admission.get('recovery_reason') or 'independent_archive_gate_blocked')
                driver.validate_static(change)
                folder=project.root/'openspec/changes'/change
                manifest={'delta':tree_hash(folder/'specs'),'delivery':replacement_delivery_hash(folder),
                    'acceptance':evidence_digest(project,folder),
                    'baseline':tree_hash(project.root/'openspec/specs'),'expected':driver.prepare(change),
                    'release':'builtin-v2','policy':'builtin-v2'}
                state='unmerged'
            else:
                manifest=json.loads(row['manifest'])
                if manifest['release']!='builtin-v2' or manifest['policy']!='builtin-v2':
                    trust=load(project.root)
                    if manifest['release']!=trust.release_digest or manifest['policy']!=trust.policy_version:
                        raise ValueError('archive_policy_changed')
                state=observe(project,row)
        fence=acquire(db,project,actor,change,operation_id,manifest,row)
        with authority(db,project,actor,operation_id,fence):
            row=assert_fence(db,project,operation_id,fence)
            if state=='unmerged':
                authorize_write(db,project,actor)
                admission=change_acceptance(project.root,change,source_root=project.source_root)
                if observe(project,row)!='unmerged' or not admission['ready']:
                    raise ValueError(admission.get('recovery_reason') or 'independent_archive_gate_blocked')
                driver.recheck_tools();assert_fence(db,project,operation_id,fence)
                driver.merge_and_move(change);state=observe(project,row)
            if state=='merged':
                authorize_write(db,project,actor);assert_fence(db,project,operation_id,fence)
                driver.merge_and_move(change,move_only=True);state=observe(project,row)
            if state not in {'moved','synced'}:raise ValueError('archive_result_unknown')
            for stage in ('merge_verified','move_verified'):
                row=assert_fence(db,project,operation_id,fence)
                if STAGES.index(row['stage'])<STAGES.index(stage):checkpoint(db,project,operation_id,fence,stage)
            if row['stage']!='synced' and (state!='synced' or needs_finalize(project.root,change)):
                authorize_write(db,project,actor);assert_fence(db,project,operation_id,fence)
                driver.finalize(change)
            row=assert_fence(db,project,operation_id,fence)
            if observe(project,row)!='synced':raise ValueError('archive_sync_unverified')
            if row['stage']=='move_verified':checkpoint(db,project,operation_id,fence,'synced')
            require_finalized(project.root,change)
            authorize_write(db,project,actor);checkpoint(db,project,operation_id,fence,'completed')
        return {'operation_id':operation_id,'stage':'completed','replayed':False}
