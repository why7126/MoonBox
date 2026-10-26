"""Proven pre-execution recovery under the existing conversation/operation fences."""
from datetime import datetime, timezone
from sqlalchemy import insert, select, update
from app.chat import service
from app.chat.schema import conversations, turns, events, reservations, usage_accounts
from app.chat.content_schema import prepare_attempts


def request(db, actor, tid, mode, key, request_id=None):
    original = service.turn(db, actor, tid)
    parent = service.conversation(db, actor, original['conversation_id'])
    # Serialize both check and resume with admission/deletion.
    db.execute(update(conversations).where(conversations.c.id == parent['id'],
        conversations.c.deleted_at.is_(None)).values(updated_at=conversations.c.updated_at))
    original = service.turn(db, actor, tid)
    parent = service.conversation(db, actor, parent['id'])
    old = db.execute(select(prepare_attempts).where(prepare_attempts.c.turn_id == tid,
        prepare_attempts.c.request_key == key)).mappings().first()
    if old and mode == 'resume_prepare':
        return {'turn_id': tid, 'attempt_id': old['id'], 'eligibility': False,
                'state': old['state'], 'reason': 'request_replayed'}
    failed = db.scalar(select(events.c.id).where(events.c.turn_id == tid,
        events.c.source_id.startswith('workspace-prepare-failed')).limit(1))
    submitted = db.scalar(select(events.c.id).where(events.c.turn_id == tid,
        events.c.source_id.in_(('runner:start-requested', 'runner:started'))).limit(1))
    reason = None
    if original['status'] != 'failed' or not failed or submitted or original['executor_turn_id']:
        reason = 'execution_state_unknown' if original['status'] == 'unknown' or submitted else 'not_preparation_failure'
    elif parent['active_turn_id'] or parent['archived']:
        reason = 'conversation_unavailable'
    from app.governance.recovery_schema import operations
    operation = db.execute(select(operations).where(operations.c.origin_turn_id == tid)).mappings().first()
    if operation:
        from app.governance.recovery_service import authorize
        _, _, project = authorize(db, actor, operation['id'], write=mode == 'resume_prepare')
        if operation['lease_owner'] or operation['application_id'] or project.binding_revision != operation['binding_revision']:
            reason = 'operation_changed'
    response = {'turn_id': tid, 'attempt_id': None, 'eligibility': reason is None,
                'state': original['status'], 'reason': reason}
    if mode == 'check':
        from app.chat.observability import storage_span
        storage_span(db, tid, 'recovery_check', result='eligible' if reason is None else 'unavailable',
            metadata={'error_code': reason})
        db.commit(); return response
    if reason:
        db.rollback(); raise service.ChatError(2506, '当前轮次不可续接，请先核验执行状态', details={'reason': reason})
    from app.chat.isolated import allowed
    if not allowed(db, actor, parent['space_id'], parent['repository_id']):
        db.rollback(); raise service.ChatError(2505, '执行环境尚未就绪', 503)
    from app.chat.settings import execution_limits
    from app.chat.admission import _account
    limits = execution_limits()
    if limits is None: raise service.ChatError(2505, '执行配置无效', 503)
    reservation = db.execute(select(reservations).where(reservations.c.turn_id == tid).with_for_update()).mappings().first()
    if not reservation or reservation['status'] != 'settled' or reservation['actual_tokens'] != 0:
        raise service.ChatError(2506, '准备阶段用量尚未核验')
    period = datetime.now(timezone.utc).strftime('%Y-%m')
    for kind, identifier in (('space', parent['space_id']), ('user', actor)):
        base = f'{kind}:{identifier}'; _account(db, base); _account(db, f'{base}:{period}')
        conditions = [usage_accounts.c.id == base]
        for field, setting in (('active_runs', 'concurrency'), ('used_bytes', 'storage_bytes')):
            cap = limits[f'{kind}_{setting}']
            if cap is not None:
                used = usage_accounts.c[field] + usage_accounts.c.reserved_bytes if setting == 'storage_bytes' else usage_accounts.c[field]
                conditions.append(used < cap)
        if db.execute(update(usage_accounts).where(*conditions).values(active_runs=usage_accounts.c.active_runs+1)).rowcount != 1:
            raise service.ChatError(2508, '运营额度不足，已保存内容保留')
        monthly = db.execute(select(usage_accounts).where(usage_accounts.c.id == f'{base}:{period}').with_for_update()).mappings().one()
        cap = limits[f'{kind}_monthly_tokens']
        if cap is not None and monthly['used_tokens'] + monthly['reserved_tokens'] >= cap:
            raise service.ChatError(2508, '月度运营额度不足')
    attempt = service.identity()
    db.execute(insert(prepare_attempts).values(**attempt, turn_id=tid, request_key=key,
        generation=original['generation'], prior_status=original['status'], prior_error=original['error_code'],
        prior_bytes=reservation['actual_bytes'] or 0, state='queued', request_id=request_id))
    db.execute(update(reservations).where(reservations.c.turn_id == tid).values(status='reserved',
        period=period, tokens=0, bytes=0, concurrency_released=0, actual_tokens=None,
        actual_bytes=None, updated_at=service.now()))
    db.execute(update(turns).where(turns.c.id == tid).values(status='queued', error_code=None,
        worker_id=None, reserved_bytes=0, updated_at=service.now()))
    db.execute(update(conversations).where(conversations.c.id == parent['id']).values(active_turn_id=tid))
    if operation:
        from app.chat.schema import governance_candidates as candidates
        db.execute(update(candidates).where(candidates.c.id == operation['candidate_id'],
            candidates.c.state == 'rejected').values(state='prepared', error_code=None))
        db.execute(update(operations).where(operations.c.id == operation['id']).values(state='active',
            reason_code=None, version=operations.c.version+1))
    from app.governance.execution_guard import execution_guards
    db.execute(update(execution_guards).where(execution_guards.c.operation_id == tid,
        execution_guards.c.state == 'needs_review', execution_guards.c.terminal_status == 'failed').values(
            state='running', terminal_status=None, reason_code=None,
            version=execution_guards.c.version+1, updated_at=service.now()))
    from app.chat.observability import trace
    trace(db, tid, 'queued', actor=actor, request_id=request_id)
    db.commit()
    return {**response, 'attempt_id': attempt['id'], 'state': 'queued', 'eligibility': False}
