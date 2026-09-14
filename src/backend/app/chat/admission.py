"""Transactional queue admission and settlement; API remains gated on executor verification."""
from datetime import datetime, timezone
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat import service
from app.chat.schema import conversations, turns, messages, usage_accounts, reservations


def _account(db, key):
    # Savepoint preserves the outer transaction if another request created the account.
    if db.scalar(select(usage_accounts.c.id).where(usage_accounts.c.id == key)) is None:
        try:
            with db.begin_nested():
                db.execute(insert(usage_accounts).values(id=key))
        except IntegrityError:
            pass


def enqueue(db, actor, cid, client_id, prompt, limits, *, retry_of=None, request_id=None):
    """Caller must first verify the isolated executor. This function never starts a process."""
    if not limits:
        raise service.ChatError(2505, '执行额度尚未配置', 503)
    row = service.conversation(db, actor, cid)
    # Serialize on the conversation before looking up idempotency, including concurrent duplicates.
    won = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.deleted_at.is_(None)).values(updated_at=service.now())).rowcount
    if won != 1:
        db.rollback(); raise service.ChatError(2504, '会话状态已变化')
    previous = db.execute(select(turns).where(turns.c.conversation_id == cid, turns.c.client_request_id == client_id).with_for_update()).mappings().first()
    if previous:
        db.rollback()
        if previous['prompt'] != prompt or previous['retry_of'] != retry_of: raise service.ChatError(2504, '同一请求标识不能用于不同输入')
        return service.public_turn(previous)
    if retry_of:
        original = service.turn(db, actor, retry_of)
        if original['conversation_id'] != cid or original['status'] not in ('failed','stopped') or original['prompt'] != prompt:
            db.rollback(); raise service.ChatError(2506, '只可重试已确认失败或停止的原轮次')
    token = service.identity(); tid = token['id']
    won = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.active_turn_id.is_(None), conversations.c.archived == 0,
        conversations.c.deleted_at.is_(None)).values(active_turn_id=tid)).rowcount
    if won != 1:
        db.rollback(); raise service.ChatError(2504, '会话只读或原运行尚未终止')
    period = datetime.now(timezone.utc).strftime('%Y-%m')
    reserve_tokens, reserve_bytes = limits['turn_reserved_tokens'] or 0, limits['turn_reserved_bytes']
    # Fixed space/user lock order also serializes different conversations sharing quotas.
    try:
        for kind, identifier in [('space', row['space_id']), ('user', actor)]:
            base = f'{kind}:{identifier}'
            for key in (base, f'{base}:{period}'):
                _account(db, key)
            capacity_conditions = [usage_accounts.c.id == base]
            if limits[f'{kind}_concurrency'] is not None:
                capacity_conditions.append(usage_accounts.c.active_runs < limits[f'{kind}_concurrency'])
            if limits[f'{kind}_storage_bytes'] is not None:
                capacity_conditions.append(usage_accounts.c.used_bytes + usage_accounts.c.reserved_bytes + reserve_bytes <= limits[f'{kind}_storage_bytes'])
            budget_conditions = [usage_accounts.c.id == f'{base}:{period}']
            if limits[f'{kind}_monthly_tokens'] is not None:
                budget_conditions.append(usage_accounts.c.used_tokens + usage_accounts.c.reserved_tokens + reserve_tokens <= limits[f'{kind}_monthly_tokens'])
            capacity = db.execute(update(usage_accounts).where(*capacity_conditions)
                .values(active_runs=usage_accounts.c.active_runs+1, reserved_bytes=usage_accounts.c.reserved_bytes+reserve_bytes)).rowcount
            budget = db.execute(update(usage_accounts).where(*budget_conditions)
                .values(reserved_tokens=usage_accounts.c.reserved_tokens+reserve_tokens)).rowcount
            if capacity != 1 or budget != 1:
                raise service.ChatError(2508, '并发、额度或存储容量不足')
        db.execute(insert(turns).values(**token, conversation_id=cid, client_request_id=client_id,
            status='queued', prompt=prompt, retry_of=retry_of, generation=0, reserved_bytes=reserve_bytes))
        db.execute(insert(reservations).values(**service.identity(), turn_id=tid, owner_id=actor,
            space_id=row['space_id'], period=period, tokens=reserve_tokens, bytes=reserve_bytes, status='reserved'))
        from app.chat.relations import capture_for_turn, copy_for_retry
        context = copy_for_retry(db, actor, retry_of, tid) if retry_of else capture_for_turn(db, actor, row, tid)
        import json
        if len(json.dumps(context,ensure_ascii=False).encode()) + len(prompt.encode()) >= reserve_bytes:
            raise service.ChatError(2508, '引用快照超过本轮存储预留')
        db.execute(insert(messages).values(**service.identity(), turn_id=tid, role='user', content=prompt))
        from app.chat.observability import trace
        trace(db,tid,'queued',actor=actor,request_id=request_id)
        db.commit()
    except Exception:
        db.rollback(); raise
    return service.public_turn(service.turn(db, actor, tid))


def release_concurrency(db, tid):
    """Release only a confirmed terminal's slot, once, in the caller's transaction."""
    won = db.execute(update(reservations).where(
        reservations.c.turn_id == tid, reservations.c.status == 'reserved',
        reservations.c.concurrency_released == 0,
        reservations.c.turn_id.in_(select(turns.c.id).where(turns.c.status.in_(service.TERMINAL)))
    ).values(concurrency_released=1, updated_at=service.now())).rowcount
    if won != 1: return False
    row = db.execute(select(reservations).where(reservations.c.turn_id == tid)).mappings().one()
    for kind, identifier in [('space', row['space_id']), ('user', row['owner_id'])]:
        changed = db.execute(update(usage_accounts).where(
            usage_accounts.c.id == f'{kind}:{identifier}', usage_accounts.c.active_runs > 0
        ).values(active_runs=usage_accounts.c.active_runs-1)).rowcount
        if changed != 1:
            db.rollback()
            raise service.ChatError(2506, '并发账本不一致，需核实后恢复')
    return True


def settle(db, tid, actual_tokens, actual_bytes):
    """Keep unknown/running reservations. Settlement requires a persisted confirmed terminal state."""
    if type(actual_tokens) is not int or type(actual_bytes) is not int or min(actual_tokens, actual_bytes) < 0:
        raise ValueError('nonnegative usage required')
    state = db.scalar(select(turns.c.status).where(turns.c.id == tid))
    if state not in service.TERMINAL:
        raise service.ChatError(2506, '原运行终态尚未确认，不能释放预留')
    release_concurrency(db, tid)
    row = db.execute(select(reservations).where(reservations.c.turn_id == tid)).mappings().first()
    if not row: return False
    won = db.execute(update(reservations).where(reservations.c.turn_id == tid, reservations.c.status == 'reserved')
        .values(status='settled', actual_tokens=actual_tokens, actual_bytes=actual_bytes, updated_at=service.now())).rowcount
    if won != 1:
        db.rollback(); return False
    for kind, identifier in [('space', row['space_id']), ('user', row['owner_id'])]:
        base = f'{kind}:{identifier}'
        db.execute(update(usage_accounts).where(usage_accounts.c.id == base).values(
            reserved_bytes=usage_accounts.c.reserved_bytes-row['bytes'], used_bytes=usage_accounts.c.used_bytes+actual_bytes))
        db.execute(update(usage_accounts).where(usage_accounts.c.id == f"{base}:{row['period']}").values(
            reserved_tokens=usage_accounts.c.reserved_tokens-row['tokens'], used_tokens=usage_accounts.c.used_tokens+actual_tokens))
    db.commit(); return True
