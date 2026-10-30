"""Read-only current-object archive view. No ledger writes or execution on GET."""
from datetime import datetime, timezone
import re
from sqlalchemy import select
from app.chat.service import ChatError
from . import scope
from .reader import ProjectReader
from .archive_dispatch import changes_for_object, controlled_candidate
from .replacement_schema import archive_operations, commits
from .archive_finalization import build_report
from .archive_diagnostics import safe_diagnostics
from .replacement_permissions import authorize_write


def executor_idle(project):
    """Probe an existing OS fence without creating or modifying lock files."""
    import os
    import stat
    import fcntl
    from . import store
    try:
        fd = os.open(store.root()/('project-'+project.key+'.lock'), os.O_RDONLY | os.O_NOFOLLOW)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                return False
            fcntl.flock(fd, fcntl.LOCK_SH | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return True
        finally:
            os.close(fd)
    except OSError:
        return False


def operation_for_change(db, project, target):
    candidate = controlled_candidate(db, project, target)
    ordinary = db.execute(select(archive_operations).where(
        archive_operations.c.scope_key == project.key, archive_operations.c.change_id == target)).mappings().first()
    if candidate:
        if ordinary:
            raise ValueError('replacement_candidate_ambiguous')
        row = db.execute(select(commits).where(commits.c.scope_key == project.key,
            commits.c.proposal_id == candidate['id'])).mappings().first()
        if row and candidate['operation_id'] != row['id']:
            raise ValueError('original_operation_required')
        return row, 'controlled', candidate['binding_revision']
    return ordinary, 'sprint' if re.fullmatch(r'sprint-\d{3}', target) else 'ordinary', ordinary['binding_revision'] if ordinary else None


def targets_for_object(db, project, actor, object_id):
    if not re.fullmatch(r'sprint-\d{3}', object_id):
        return changes_for_object(db, project, actor, object_id, write=False)
    from app.chat.relations import _authorize_object
    from .sprint_object import resolve, scope_ids
    _authorize_object(db, actor, project.space_id, project.repository_id, object_id)
    members = scope_ids(resolve(project.root, object_id)['plan'])
    targets = set(members['changes'])
    for oid in members['requirements'] | members['bugs']:
        targets.update(changes_for_object(db, project, actor, oid, write=False))
    return [object_id, *sorted(targets)]


def view(db, *, actor, space_id, repository_id, object_id):
    project = scope.authorize(db, actor, space_id, repository_id)
    visibility = scope.RequestVisibility(db, actor, project)
    reader = ProjectReader(db, actor, project)
    before = reader.snapshot()
    targets = targets_for_object(db, project, actor, object_id)
    if len(targets) > 100:
        raise ValueError('archive_query_scope_too_large')
    operations, versions, reports = [], [], {}
    for target in targets:
        is_sprint = bool(re.fullmatch(r'sprint-\d{3}', target))
        if not is_sprint:
            reader.authorize_object(before, target, change=True, root=project.root)
        row, kind, binding = operation_for_change(db, project, target)
        versions.append((target, row['id'] if row else None, row['revision'] if row else None))
        if not row:
            continue
        verification = {'status': 'pending', 'checked_at': datetime.now(timezone.utc).isoformat(),
                        'input_fingerprint': before.revision, 'findings': []}
        if row['stage'] in {'synced', 'completed'}:
            if is_sprint:
                from .sprint_object import require_final
                try:
                    require_final(project.root, target, allow_closing=True)
                    verification['status'] = 'passed'
                except (ValueError, ChatError):
                    verification['status'] = 'review'
            else:
                report = build_report(project.root, target)
                reports[target] = report
                verification.update(status='passed' if report['status'] == 'finalized' else 'blocked',
                                    findings=safe_diagnostics(report).get('findings', []))
        if binding != project.binding_revision:
            verification['status'] = 'stale'
        denial = None
        actions = ['refresh']
        if row['stage'] != 'completed':
            try:
                authorize_write(db, project, actor, lock=False)
                if row['actor_id'] != actor or binding != project.binding_revision:
                    raise ValueError('original_operation_required')
                from app.chat.schema import governance_project_locks as locks
                owner = db.scalar(select(locks.c.operation_id).where(locks.c.scope_key == project.key))
                if owner != row['id']:
                    raise ValueError('executor_occupancy_unknown')
                # Eligibility is advisory. The execution path obtains the OS lock
                # and checks original identity, history, admission and fence again.
                if not executor_idle(project):
                    raise ValueError('executor_occupancy_unknown')
                actions.append('resume')
            except (ValueError, TypeError, ChatError):
                denial = 'original_operation_recheck_required'
        operations.append({'operation_id': row['id'], 'operation_kind': kind, 'target_id': target,
                           'stage': row['stage'], 'revision': row['revision'], 'verification': verification,
                           'allowed_actions': actions, 'denial_reason': denial})
    reports_changed = any(build_report(project.root, target) != report for target, report in reports.items())
    after = reader.snapshot()
    visibility.assert_current(db)
    current = [(target, r['id'] if r else None, r['revision'] if r else None)
               for target in targets for r, _, _ in [operation_for_change(db, project, target)]]
    stale = (before.revision != after.revision or versions != current
             or reports_changed)
    if stale:
        for op in operations:
            op['verification']['status'] = 'stale'
            op['allowed_actions'] = ['refresh']
            op['denial_reason'] = 'archive_inputs_changed'
    return {'object_id': object_id, 'object_type': 'sprint' if object_id.startswith('sprint-') else
            'requirement' if object_id.startswith('REQ-') else 'bug' if object_id.startswith('BUG-') else 'change',
            'association_scope': 'current_object', 'operations': operations,
            'not_started_targets': [target for target, oid, _ in versions if oid is None],
            'summary': 'stale' if stale else 'not_started' if not operations else
            'completed' if len(operations) == len(targets) and all(o['stage'] == 'completed' and o['verification']['status'] == 'passed' for o in operations) else 'needs_attention'}


def resume(db, *, actor, space_id, repository_id, object_id, operation_id, request_id=None):
    """Resume one original operation; never expand a multi-object request."""
    project = scope.authorize(db, actor, space_id, repository_id, write=True)
    if re.fullmatch(r'sprint-\d{3}', object_id):
        targets_for_object(db, project, actor, object_id)
    else:
        changes_for_object(db, project, actor, object_id, write=True)
    row, kind, binding = operation_for_change(db, project, object_id)
    if (not row or row['id'] != operation_id or row['actor_id'] != actor
            or binding != project.binding_revision or row['stage'] == 'completed'):
        raise ValueError('original_operation_required')
    # Coordinators hold the project lock and recheck the stored original identity.
    if kind == 'sprint':
        from .sprint_archive_coordinator import execute
        return execute(db, actor=actor, space_id=space_id, repository_id=repository_id,
                       sprint=object_id, operation_id=operation_id)
    from .archive_dispatch import execute_change
    return execute_change(db, project, actor, object_id, request_id=request_id, expected_operation_id=operation_id)
