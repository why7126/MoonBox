"""Human-confirmed integration, serialized by main workspace and durable operation identity."""
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4
from sqlalchemy import insert, select, update, delete, and_, or_
from app.chat import service as chat
from app.chat.settings import repository_binding
from app.chat.relations import _read_file
from app.moonbox_worktree import Repository, WorktreeConflict
from app.moonbox_worktree.git import _run
from app.moonbox_exec_server import validation
from . import service, workspaces
from .authority import delivery
from .schema import assignments, main_bindings, write_locks
from .integration_schema import candidates, operations
from .merge import CandidateInput, confirmable
from .observability import record


def _governance(project, context):
    from app.governance.sprint_object import resolve
    sprint = resolve(project.root, context['sprint_id'])
    value = [_read_file(project.root, 'openspec/changes/' + context['change_id'] + '/trace.md'),
        sprint['plan'], str(project.binding_revision), context]
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str, separators=(',', ':')).encode()).hexdigest()


def _scope(repo, source, target, change_id):
    from .delivery_policy import writable_roots
    baseline = _run(repo.root, 'merge-base', source, target).decode().strip()
    paths = _run(repo.root, 'diff', '--name-only', '-z', baseline, source).decode().split('\0')
    for path in filter(None, paths):
        if not any(path == root or path.startswith(root + '/') for root in writable_roots(change_id)):
            raise WorktreeConflict('shared_governance_change_forbidden')
        from app.moonbox_exec_server.scope import excluded
        if excluded(path) or path == 'docs/spec-logs' or path.startswith('docs/spec-logs/'):
            raise WorktreeConflict('shared_governance_change_forbidden')


def get(db, actor, space, repository, candidate_id, *, write=False):
    row = db.execute(select(candidates).where(candidates.c.id == candidate_id,
        candidates.c.space_id == space, candidates.c.repository_id == repository)).mappings().first()
    if not row:
        raise WorktreeConflict('merge_candidate_unavailable')
    project, _, _ = service.scoped(db, actor, space, repository, row['workspace_id'], write=write)
    from app.governance.scope import visible
    if not visible(db, actor, project, row['change_id']):
        raise chat.ChatError(2601, '无权查看此成果所属变更', 403)
    return dict(row)


def _current(db, actor, row):
    project, context = delivery(db, actor, row['space_id'], row['repository_id'], row['change_id'])
    _, source, assignment = service.scoped(db, actor, row['space_id'], row['repository_id'], row['workspace_id'], write=True)
    if not assignment or assignment['change_id'] != row['change_id'] or assignment['delivery_root'] != context['delivery_root']:
        raise WorktreeConflict('delivery_assignment_changed')
    main = workspaces.get(db, row['space_id'], row['repository_id'], row['main_workspace_id'])
    repo = Repository.open(main['root_locator'])
    child = repo.verify(source['root_locator'])
    if repo.identity != main['git_identity'] or child.identity != source['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    if _run(repo.root, 'symbolic-ref', '--quiet', 'HEAD').decode().strip() != row['target_ref']:
        raise WorktreeConflict('target_ref_changed')
    return project, context, main, source, repo, child


def _inputs(row, *, source=None, target=None, governance=None):
    return CandidateInput(space_id=row['space_id'], repository_id=row['repository_id'], workspace_id=row['workspace_id'],
        delivery_root=row['delivery_root'], change_id=row['change_id'], sprint_id=row['sprint_id'],
        source_commit=source or row['source_commit'], target_commit=target or row['target_commit'],
        candidate_commit=row['candidate_commit'], evidence_digest=row['evidence_digest'],
        runtime_digest=row['runtime_digest'], governance_digest=governance or row['governance_digest'])


def prepare(db, actor, space_id, repository_id, workspace_id, request_id):
    _, source, assignment = service.scoped(db, actor, space_id, repository_id, workspace_id, write=True)
    if not assignment or source['purpose'] != 'development' or assignment['state'] != 'developing':
        raise WorktreeConflict('delivery_workspace_not_developing')
    project, context = delivery(db, actor, space_id, repository_id, assignment['change_id'])
    previous = db.execute(select(candidates).where(candidates.c.workspace_id == workspace_id,
        candidates.c.actor_id == actor, candidates.c.request_id == request_id)).mappings().first()
    if previous:
        if previous['change_id'] != assignment['change_id']:
            raise WorktreeConflict('merge_request_conflict')
        return dict(previous)
    main_id = db.scalar(select(main_bindings.c.workspace_id).where(main_bindings.c.space_id == space_id,
        main_bindings.c.repository_id == repository_id))
    main = workspaces.get(db, space_id, repository_id, main_id)
    identifier = chat.identity()
    workspaces.acquire(db, main_id, identifier['id'], 1)
    workspaces.acquire(db, workspace_id, identifier['id'], 1)
    repo = Repository.open(main['root_locator']); child = repo.verify(source['root_locator'])
    repo.require_clean(); child.require_clean()
    if repo.identity != main['git_identity'] or child.identity != source['git_identity']:
        raise WorktreeConflict('repository_identity_mismatch')
    _scope(repo, child.head(), repo.head(), assignment['change_id'])
    row = dict(**identifier, space_id=space_id, repository_id=repository_id, workspace_id=workspace_id,
        main_workspace_id=main_id, integration_workspace_id=None, actor_id=actor, request_id=request_id,
        change_id=assignment['change_id'], delivery_root=context['delivery_root'], sprint_id=context['sprint_id'],
        source_commit=child.head(), target_commit=repo.head(), candidate_commit=None,
        target_ref=_run(repo.root, 'symbolic-ref', '--quiet', 'HEAD').decode().strip(),
        governance_digest=_governance(project, context), binding_revision=str(project.binding_revision),
        runtime_digest=None, evidence_digest=None, fingerprint=None, state='prepared', error_code=None, validation_result='{}')
    db.execute(insert(candidates).values(**row))
    from app.moonbox_rollout import catalog
    from app.moonbox_rollout.schema import points
    latest = db.scalar(select(points.c.id).where(points.c.workspace_id == workspace_id,
        points.c.state == 'complete', points.c.change_id == row['change_id'])
        .order_by(points.c.sequence.desc()).limit(1))
    if latest:
        catalog.reference(db, workspace_id, latest, 'merge_candidate', row['id'], 'candidate_validation')
    record(db, row['id'], actor, 'candidate', 'queued', workspace_id=workspace_id)
    db.commit()  # Git preparation can now be reconciled by candidate identity.
    return row


def validate(factory, actor, space, repository, candidate_id):
    with factory() as db:
        row = get(db, actor, space, repository, candidate_id, write=True)
        if row['state'] in ('validated', 'integrated', 'invalidated'):
            return public(row)
        workspaces.acquire(db, row['main_workspace_id'], candidate_id, 1)
        workspaces.acquire(db, row['workspace_id'], candidate_id, 1)
        project, context, main, source, repo, child = _current(db, actor, row)
        if (repo.head(), child.head(), _governance(project, context)) != (row['target_commit'], row['source_commit'], row['governance_digest']):
            raise WorktreeConflict('merge_candidate_stale')
        repo.require_clean(); child.require_clean()
        combined = row['candidate_commit'] or repo.candidate(row['source_commit'], row['target_commit'])
        db.execute(update(candidates).where(candidates.c.id == candidate_id).values(candidate_commit=combined, state='validating'))
        # Persist the integration checkout reservation before creating any directory.
        integration_id = row['integration_workspace_id'] or str(uuid4())
        config = repository_binding(repository, space)
        if not config or not config.get('workspace_root'):
            raise WorktreeConflict('managed_root_unavailable')
        from .schema import workspaces as workspace_table
        integration = db.execute(select(workspace_table).where(workspace_table.c.id == integration_id)).mappings().first()
        if not integration:
            integration = workspaces._row(integration_id, space, repository, repo.identity, 'integration',
                Path(config['workspace_root']) / integration_id, combined)
            integration['lifecycle'] = 'preparing'
            db.execute(insert(workspace_table).values(**integration))
            db.execute(update(candidates).where(candidates.c.id == candidate_id).values(integration_workspace_id=integration_id))
        db.commit()
        integration = workspaces.materialize(db, main, dict(integration))
        db.commit()
    result = validation.provider().validate(candidate_id=candidate_id, candidate_commit=combined,
        workspace=Path(integration['root_locator']), change_id=row['change_id'],
        factory=factory, space_id=space, repository_id=repository)
    with factory() as db:
        row = get(db, actor, space, repository, candidate_id, write=True)
        project, context, main, source, repo, child = _current(db, actor, row)
        if (repo.head(), child.head(), _governance(project, context)) != (row['target_commit'], row['source_commit'], row['governance_digest']):
            raise WorktreeConflict('merge_candidate_stale')
        repo.require_clean(); child.require_clean()
        checked = repo.verify(integration['root_locator']); checked.require_clean()
        if checked.head() != combined:
            raise WorktreeConflict('validation_candidate_changed')
        reason = result.get('reason_code', 'isolated_candidate_validation_unavailable')
        import re
        if not isinstance(reason, str) or not re.fullmatch(r'[a-z_]{1,64}', reason):
            reason = 'candidate_checks_failed'
        values = {'state': 'validation_blocked', 'error_code': reason,
            'validation_result': json.dumps({'status': result.get('status', 'blocked'),
                'reason_code': reason}), 'updated_at': chat.now()}
        if result.get('status') == 'passed':
            # Only the server-owned provider supplies this attestation. Neither browser
            # nor a file in the candidate checkout can declare validation successful.
            if result.get('candidate_commit') != combined or result.get('candidate_id') != candidate_id:
                raise WorktreeConflict('validation_identity_mismatch')
            safe = {key: result[key] for key in ('candidate_id', 'candidate_commit', 'environment_key', 'runtime_digest', 'evidence_digest', 'status')}
            for key in ('checks', 'template_digest'):
                if key in result:
                    safe[key] = result[key]
            import re
            if not re.fullmatch(r'[a-zA-Z0-9:_-]{1,128}', safe['environment_key']):
                raise WorktreeConflict('validation_environment_invalid')
            proposed = row | {'evidence_digest': safe['evidence_digest'], 'runtime_digest': safe['runtime_digest']}
            values.update(state='validated', error_code=None, evidence_digest=safe['evidence_digest'],
                runtime_digest=safe['runtime_digest'], fingerprint=_inputs(proposed).fingerprint(), validation_result=json.dumps(safe))
            from app.moonbox_rollout.schema import references
            db.execute(update(references).where(references.c.workspace_id == row['workspace_id'],
                references.c.owner_type == 'merge_candidate', references.c.owner_id == row['id'])
                .values(owner_type='acceptance', protection_reason='accepted_candidate'))
        db.execute(update(candidates).where(candidates.c.id == candidate_id).values(**values))
        record(db, candidate_id, actor, 'candidate', 'completed' if values['state'] == 'validated' else 'blocked',
            workspace_id=row['workspace_id'], error_code=values['error_code'])
        workspaces.release(db, row['main_workspace_id'], candidate_id, 1)
        workspaces.release(db, row['workspace_id'], candidate_id, 1)
        db.commit()
        return public(row | values)


def confirm(db, actor, space, repository, candidate_id, fingerprint, request_id):
    row = get(db, actor, space, repository, candidate_id, write=True)
    # Current Sprint operation authorization is evaluated even for idempotent replays.
    project, context, main, source, repo, child = _current(db, actor, row)
    existing = db.execute(select(operations).where(operations.c.candidate_id == candidate_id)).mappings().first()
    if existing:
        if existing['actor_id'] != actor or existing['confirmed_fingerprint'] != fingerprint:
            raise WorktreeConflict('merge_confirmation_conflict')
        return dict(existing)
    if row['state'] != 'validated' or row['fingerprint'] != fingerprint:
        raise WorktreeConflict('candidate_validation_required')
    recorded = _inputs(row)
    current = _inputs(row, source=child.head(), target=repo.head(), governance=_governance(project, context))
    repo.require_clean(); child.require_clean()
    confirmable(recorded, current, can_operate_sprint=True, validation_state='passed',
        evidence_candidate=json.loads(row['validation_result']).get('candidate_commit'), main_clean=True, source_clean=True)
    operation = dict(**chat.identity(), candidate_id=candidate_id, actor_id=actor, request_id=request_id,
        confirmed_fingerprint=fingerprint, capability_revision=_governance(project, context),
        confirmed_at=chat.now(), state='queued', actual_target=None, error_code=None)
    db.execute(insert(operations).values(**operation))
    record(db, operation['id'], actor, 'merge', 'queued', workspace_id=row['workspace_id'])
    db.commit()  # Human confirmation/audit is durable before first Git write.
    return operation


def integrate(factory, actor, space, repository, operation_id):
    result = _integrate(factory, actor, space, repository, operation_id)
    if result['state'] == 'completed':
        from .governance_projection import try_apply
        try_apply(factory, operation_id)
        with factory() as db:
            return operation_public(db.execute(select(operations).where(operations.c.id == operation_id)).mappings().one())
    return result


def _integrate(factory, actor, space, repository, operation_id):
    with factory() as db:
        operation = db.execute(select(operations).where(operations.c.id == operation_id,
            operations.c.actor_id == actor)).mappings().first()
        if not operation:
            raise WorktreeConflict('merge_operation_unavailable')
        row = get(db, actor, space, repository, operation['candidate_id'], write=True)
        if operation['state'] == 'completed':
            return operation_public(operation)
        project, context, main, source, repo, child = _current(db, actor, row)
        try:
            workspaces.acquire(db, main['id'], operation_id, 1)
            workspaces.acquire(db, source['id'], operation_id, 1)
        except WorktreeConflict as error:
            if str(error) != 'workspace_busy':
                raise
            db.rollback()
            return operation_public(operation)
        # Main lease serializes admission; an API retry cannot jump an older
        # confirmed operation for this same repository.
        older = db.scalar(select(operations.c.id).join(candidates, candidates.c.id == operations.c.candidate_id).where(
            candidates.c.main_workspace_id == main['id'], operations.c.id != operation_id,
            operations.c.state.in_(('queued', 'confirmed', 'applying')),
            or_(operations.c.created_at < operation['created_at'], and_(operations.c.created_at == operation['created_at'], operations.c.id < operation_id))).limit(1))
        if older:
            db.rollback()
            return operation_public(operation)
        # A row write serializes duplicate requests, including SQLite callers.
        db.execute(update(operations).where(operations.c.id == operation_id).values(updated_at=chat.now()))
        if repo.head() != row['candidate_commit']:
            repo.require_clean(); child.require_clean()
            confirmable(_inputs(row), _inputs(row, source=child.head(), target=repo.head(), governance=_governance(project, context)),
                can_operate_sprint=True, validation_state='passed' if row['state'] == 'validated' else 'blocked',
                evidence_candidate=json.loads(row['validation_result']).get('candidate_commit'), main_clean=True, source_clean=True)
            if operation['confirmed_fingerprint'] != row['fingerprint']:
                raise WorktreeConflict('merge_confirmation_stale')
        db.execute(update(operations).where(operations.c.id == operation_id).values(state='applying'))
        db.commit()
    with factory() as db:
        # Serialize duplicate execute requests around the external effect. The prior
        # intent remains durable even if this transaction is lost after Git succeeds.
        db.execute(update(operations).where(operations.c.id == operation_id).values(updated_at=chat.now()))
        current_operation = db.execute(select(operations).where(operations.c.id == operation_id).with_for_update()).mappings().one()
        if current_operation['state'] == 'completed':
            return operation_public(current_operation)
        project, context, main, source, repo, child = _current(db, actor, row)
        if repo.head() != row['candidate_commit']:
            repo.require_clean(); child.require_clean()
            confirmable(_inputs(row), _inputs(row, source=child.head(), target=repo.head(), governance=_governance(project, context)),
                can_operate_sprint=True, validation_state='passed' if row['state'] == 'validated' else 'blocked',
                evidence_candidate=json.loads(row['validation_result']).get('candidate_commit'), main_clean=True, source_clean=True)
        actual = repo.integrate(row['candidate_commit'], source_commit=row['source_commit'], target_commit=row['target_commit'])
        # Persist the proven Git effect before the separately resumable formal-file projection.
        db.execute(update(operations).where(operations.c.id == operation_id).values(state='completed', actual_target=actual,
            error_code=None, updated_at=chat.now()))
        db.execute(update(candidates).where(candidates.c.id == row['id']).values(state='integrated', updated_at=chat.now()))
        db.execute(update(assignments).where(assignments.c.workspace_id == row['workspace_id'],
            assignments.c.change_id == row['change_id']).values(state='integrated'))
        workspaces.release(db, main['id'], operation_id, 1)
        workspaces.release(db, source['id'], operation_id, 1)
        record(db, operation_id, actor, 'merge', 'completed', workspace_id=row['workspace_id'])
        db.commit()
        return operation_public(db.execute(select(operations).where(operations.c.id == operation_id)).mappings().one())


def invalidate(db, actor, space, repository, candidate_id):
    row = get(db, actor, space, repository, candidate_id, write=True)
    _current(db, actor, row)
    if row['state'] == 'integrated' or db.scalar(select(operations.c.id).where(operations.c.candidate_id == candidate_id)):
        raise WorktreeConflict('merge_operation_already_confirmed')
    if row['state'] == 'validating':
        raise WorktreeConflict('candidate_validation_still_running')
    db.execute(update(candidates).where(candidates.c.id == candidate_id).values(state='invalidated', fingerprint=None, updated_at=chat.now()))
    from sqlalchemy import delete
    from app.moonbox_rollout.schema import references
    db.execute(delete(references).where(references.c.workspace_id == row['workspace_id'],
        references.c.owner_id == candidate_id, references.c.owner_type.in_(('merge_candidate','acceptance'))))
    workspaces.release(db, row['main_workspace_id'], candidate_id, 1)
    workspaces.release(db, row['workspace_id'], candidate_id, 1)
    db.commit()
    return public(row | {'state': 'invalidated', 'fingerprint': None})


def public(row):
    value = {key: row[key] for key in ('id', 'workspace_id', 'change_id', 'sprint_id', 'source_commit', 'target_commit',
        'candidate_commit', 'state', 'error_code', 'fingerprint', 'created_at', 'updated_at')}
    value['validation'] = json.loads(row['validation_result'])
    return value


def operation_public(row):
    return {key: row[key] for key in ('id', 'candidate_id', 'state', 'governance_state', 'error_code', 'actual_target', 'confirmed_at', 'updated_at')}


def reconcile_applied(factory, operation_id):
    """Record an already performed effect; never runs Git writes or grants authority.

    Permission revocation cannot undo a committed Git effect. Only durable applying
    intent, both owned leases and the exact attested target permit this repair.
    """
    with factory() as db:
        db.execute(update(operations).where(operations.c.id == operation_id).values(updated_at=chat.now()))
        operation = db.execute(select(operations).where(operations.c.id == operation_id).with_for_update()).mappings().first()
        if not operation or operation['state'] not in ('applying', 'recovery_required'):
            return False
        row = db.execute(select(candidates).where(candidates.c.id == operation['candidate_id'])).mappings().one()
        if not row['candidate_commit'] or operation['confirmed_fingerprint'] != row['fingerprint']:
            return False
        for wid in (row['main_workspace_id'], row['workspace_id']):
            lease = db.execute(select(write_locks).where(write_locks.c.workspace_id == wid)).mappings().first()
            if not lease or lease['operation_id'] != operation_id or lease['generation'] != 1:
                return False
        main = workspaces.get(db, row['space_id'], row['repository_id'], row['main_workspace_id'])
        repo = Repository.open(main['root_locator'])
        if (repo.identity != main['git_identity'] or repo.head() != row['candidate_commit']
                or _run(repo.root, 'symbolic-ref', '--quiet', 'HEAD').decode().strip() != row['target_ref']):
            return False
        repo.require_clean()
        parents = _run(repo.root, 'show', '-s', '--format=%P', repo.head()).decode().split()
        if parents != [row['target_commit'], row['source_commit']]:
            return False
        db.execute(update(operations).where(operations.c.id == operation_id).values(
            state='completed', actual_target=row['candidate_commit'], error_code=None, updated_at=chat.now()))
        db.execute(update(candidates).where(candidates.c.id == row['id']).values(state='integrated', updated_at=chat.now()))
        db.execute(update(assignments).where(assignments.c.workspace_id == row['workspace_id'],
            assignments.c.change_id == row['change_id']).values(state='integrated'))
        workspaces.release(db, row['main_workspace_id'], operation_id, 1)
        workspaces.release(db, row['workspace_id'], operation_id, 1)
        record(db, operation_id, operation['actor_id'], 'merge', 'completed', workspace_id=row['workspace_id'])
        db.commit()
        return True
