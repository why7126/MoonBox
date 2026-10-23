"""Authorized read/queue boundary for durable review recovery."""
from sqlalchemy import select, update
from app.chat import service
from app.chat.workspace import WorkspaceError
from app.chat.schema import turns, governance_candidates as candidates, governance_applications as applications
from app.chat.settings import retention_limits
from app.governance import scope, store, durable_recovery as policy
from app.governance.recovery_schema import operations, attempts


def authorize(db, actor, oid, *, write=False):
    operation = policy.row(db, oid)
    if not operation or operation['actor_id'] != actor:
        raise service.ChatError(2502, '操作不存在或无权访问', 404)
    parent = service.conversation(db, actor, operation['conversation_id'])
    project = scope.authorize(db, actor, operation['space_id'], operation['repository_id'], write=write)
    if not scope.visible(db, actor, project, operation['object_id']):
        raise service.ChatError(2502, '操作不存在或无权访问', 404)
    return operation, parent, project


def reason(db, operation, parent, project):
    if operation['schema_version'] != 1:
        return 'schema_incompatible'
    if project.readonly:
        return 'permission_revoked'
    if project.binding_revision != operation['binding_revision']:
        return 'binding_changed'
    if parent['active_turn_id'] or operation['lease_owner']:
        return 'executor_occupancy_unknown'
    if operation['state'] == 'completed':
        return None
    if retention_limits() is None:
        return 'retention_unconfigured'
    if not operation['recovery_expires_at']:
        return 'terminal_unknown'
    if operation['recovery_expires_at'] <= service.now():
        return 'recovery_expired'
    from app.governance.execution_guard import read
    guard = read(db, project.key, operation['object_id'])
    if guard and guard['operation_id'] not in (None, operation['origin_turn_id']):
        return 'object_operation_changed'
    candidate_state = db.scalar(select(candidates.c.state).where(candidates.c.id == operation['candidate_id']))
    if candidate_state == 'rejected':
        return operation['reason_code'] or 'candidate_rejected'
    try:
        baseline = store.read(operation['candidate_id'], 'baseline')
        if baseline['binding_revision'] != project.binding_revision:
            return 'binding_changed'
        result = store.read(operation['candidate_id'], 'result')
        if result['manifest_hash'] != operation['manifest_hash']:
            return 'artifact_changed'
        from app.governance.readiness import require_controller
        require_controller(project)
        from app.governance.recovery_capabilities import require as require_capabilities
        require_capabilities(operation['action'])
    except service.ChatError:
        return 'controller_unavailable'
    except (OSError, ValueError, KeyError, TypeError, WorkspaceError):
        return 'artifact_unavailable'
    return None


def detail(db, actor, oid):
    operation, parent, project = authorize(db, actor, oid)
    blocked = reason(db, operation, parent, project)
    if not blocked and operation['state'] != 'completed' and operation['manual_count'] >= 1:
        blocked = 'manual_attempt_exhausted'
    fields = ('id', 'object_id', 'action', 'stage', 'state', 'version', 'execution_terminal',
              'auto_retry_count', 'manual_count', 'next_retry_at', 'recovery_expires_at',
              'candidate_id', 'application_id')
    result = {key: operation[key] for key in fields}
    result['reason_code'] = blocked or operation['reason_code']
    from app.governance.execution_guard import read as read_guard, public_state
    from app.governance.completion_handoff import status as completion_status
    guard = read_guard(db, project.key, operation['object_id'])
    if guard and guard['operation_id'] == operation['origin_turn_id']:
        result.update(completion_status(db, actor, project, guard))
        result['admission_state'] = 'allowed' if public_state(guard, actor)['can_send'] else 'blocked'
        result['admission_reason'] = guard['reason_code']
    else:
        result.update(historical_result='unverified', admission_state='blocked', admission_reason='stale_operation')
    result['allowed_actions'] = ['refresh', 'evidence']
    if not blocked and operation['state'] != 'completed':
        result['allowed_actions'].append('resume')
    rejected = db.scalar(select(candidates.c.state).where(candidates.c.id == operation['candidate_id'])) == 'rejected'
    if blocked in ('recovery_expired', 'artifact_unavailable') or (rejected and blocked == operation['reason_code'] and not operation['application_id']):
        result['allowed_actions'].append('regenerate')
    return result


def request_recovery(db, actor, oid, expected_version, idempotency_key, confirmed, request_id=None):
    operation, parent, project = authorize(db, actor, oid, write=True)
    if confirmed is not True:
        raise service.ChatError(2604, '请明确确认继续剩余步骤', 409)
    # Replays return the original claim; they never create another write attempt.
    old = db.execute(select(attempts).where(attempts.c.operation_id == oid,
        attempts.c.request_key == idempotency_key)).mappings().first()
    if old:
        expected = policy.fingerprint({'operation_id': oid, 'version': expected_version, 'kind': 'manual'})
        if old['request_hash'] != expected:
            raise service.ChatError(2606, '同一恢复请求不能用于不同输入', 409)
        return {'operation_id': oid, 'attempt_id': old['id'], 'state': old['state']}
    blocked = reason(db, operation, parent, project)
    if blocked:
        raise service.ChatError(2604, '当前操作不能恢复，请刷新查看原因', 409, details={'reason': blocked})
    from app.governance.writer import project_lock
    with project_lock(project):
        # Claim is durable before a controller may attempt any mutation.
        attempt, _ = policy.claim(db, oid, expected_version, idempotency_key, request_id=request_id)
        from app.governance.observability import trace
        trace(db, oid, 'queued', actor=actor, request_id=request_id,
              metadata={'operation_id': oid, 'attempt_id': attempt['id']})
        db.commit()
    return {'operation_id': oid, 'attempt_id': attempt['id'], 'state': attempt['state']}


def checkpoint(db, candidate_id, stage, *, terminal=None, terminal_at=None):
    from app.governance.completion_handoff import enqueue
    enqueue(db, candidate_id)
    operation = db.execute(select(operations).where(operations.c.candidate_id == candidate_id)).mappings().first()
    if not operation:
        return
    if terminal is None and operation['execution_terminal'] is None and operation['origin_turn_id']:
        origin = db.execute(select(turns).where(turns.c.id == operation['origin_turn_id'])).mappings().first()
        if origin and origin['status'] in ('completed', 'failed', 'stopped'):
            terminal, terminal_at = origin['status'], origin['updated_at']
    candidate = db.execute(select(candidates).where(candidates.c.id == candidate_id)).mappings().one()
    app = db.execute(select(applications).where(applications.c.candidate_id == candidate_id)).mappings().first()
    values = {'manifest_hash': candidate['manifest_hash'], 'application_id': app['id'] if app else None}
    state = 'waiting' if terminal == 'stopped' else 'active'
    diagnostic = None
    if terminal:
        values['execution_terminal'] = terminal
        values['recovery_expires_at'] = policy.expiry(terminal_at, retention_limits(), operation['recovery_expires_at'])
    if candidate['state'] in ('applied', 'unchanged'):
        stage, state = 'complete', 'completed'
    elif app and app['state'] in ('conflict', 'recovery_blocked', 'failed'):
        state, diagnostic = 'blocked', app['error_code'] or 'application_unverified'
        if diagnostic in policy.TRANSIENT and not operation['next_retry_at'] and operation['auto_retry_count'] < 3:
            from datetime import datetime, timezone, timedelta
            values['next_retry_at'] = policy.stamp(datetime.now(timezone.utc) + timedelta(seconds=policy.BACKOFF[operation['auto_retry_count']]))
    elif candidate['state'] == 'rejected':
        state, diagnostic = 'blocked', candidate['error_code']
    policy.advance(db, operation['id'], stage, state=state, reason=diagnostic, **values)


def checkpoint_preparation_failure(db, turn_id, code):
    """Project a proven pre-model failure; retain its existing identity and baseline."""
    operation = db.execute(select(operations).where(operations.c.origin_turn_id == turn_id)).mappings().first()
    turn = db.execute(select(turns).where(turns.c.id == turn_id)).mappings().first()
    if not operation or not turn or turn['status'] != 'failed' or turn['executor_turn_id']:
        return
    if db.scalar(select(applications.c.id).where(applications.c.candidate_id == operation['candidate_id'])):
        return
    changed = db.execute(update(candidates).where(candidates.c.id == operation['candidate_id'],
        candidates.c.state == 'prepared').values(state='rejected', error_code=code, updated_at=service.now())).rowcount
    if changed:
        checkpoint(db, operation['candidate_id'], operation['stage'], terminal='failed', terminal_at=turn['updated_at'])


def prepare_explicit_regeneration(db, actor, parent, project, action, object_id, request_key):
    """An explicit new review send may replace an expired/unusable, uncommitted attempt.

    This only releases admission metadata. It never erases artifacts or takes over
    an application whose commit is uncertain; the new turn still runs all gates.
    """
    if action not in policy.ACTIONS or parent['active_turn_id']:
        return
    old = db.execute(select(operations).where(operations.c.actor_id == actor,
        operations.c.scope_key == project.key, operations.c.object_id == object_id,
        operations.c.action == action).order_by(operations.c.created_at.desc()).limit(1)).mappings().first()
    if not old or old['request_key'] == request_key or old['lease_owner'] or old['state'] == 'completed':
        return
    terminal = db.scalar(select(turns.c.status).where(turns.c.id == old['origin_turn_id']))
    if terminal not in ('completed', 'failed', 'stopped'):
        return
    if db.scalar(select(applications.c.id).where(applications.c.candidate_id == old['candidate_id']).limit(1)):
        return
    expired = old['recovery_expires_at'] and old['recovery_expires_at'] <= service.now()
    rejected = db.scalar(select(candidates.c.state).where(candidates.c.id == old['candidate_id'])) == 'rejected'
    if not expired and not rejected:
        return
    if old['reason_code'] == 'source_recovery_blocked':
        return
    from app.governance.execution_guard import execution_guards
    guard = db.execute(select(execution_guards).where(execution_guards.c.scope_key == project.key,
        execution_guards.c.object_id == object_id)).mappings().first()
    if guard and guard['operation_id'] == old['origin_turn_id'] and guard['state'] == 'needs_review':
        db.execute(update(execution_guards).where(execution_guards.c.scope_key == project.key,
            execution_guards.c.object_id == object_id, execution_guards.c.version == guard['version']).values(
                state='idle', version=guard['version']+1, reason_code='explicit_regeneration', updated_at=service.now()))
        db.execute(update(candidates).where(candidates.c.id == old['candidate_id']).values(
            state='rejected', error_code='recovery_expired' if expired else old['reason_code'], updated_at=service.now()))
