"""Durable bounded recovery scheduling. No prompts or execution replay."""
import hashlib
import json
import logging
import random
import re
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import select, insert, update, func, or_, and_
from sqlalchemy.exc import IntegrityError
from app.chat.schema import turns, conversations
from app.chat.recovery_schema import recoveries, resumes
from app.chat.settings import recovery_policy


def timestamp(value):
    return value.replace(tzinfo=timezone.utc).isoformat(timespec='seconds')


def clock(db):
    value = db.scalar(select(func.utc_timestamp() if db.get_bind().dialect.name == 'mysql' else func.current_timestamp()))
    return value if isinstance(value, datetime) else datetime.fromisoformat(value)


def plus(value, seconds):
    return timestamp(datetime.fromisoformat(value) + timedelta(seconds=seconds))


def claim(db, policy=None, *, now=None):
    policy = policy or recovery_policy()
    now = timestamp(now or clock(db))
    # Bounded lazy enrolment; paused rows are never selected again.
    missing = db.scalars(select(turns.c.id).outerjoin(recoveries, turns.c.id == recoveries.c.turn_id)
        .where(turns.c.status == 'unknown', recoveries.c.turn_id.is_(None))
        .order_by(turns.c.created_at, turns.c.id).limit(32))
    for tid in list(missing):
        try:
            with db.begin_nested():
                db.execute(insert(recoveries).values(turn_id=tid, state='waiting', generation=0,
                    attempt_count=0, next_retry_at=now, updated_at=now))
        except IntegrityError: pass
    eligible = or_(recoveries.c.state == 'waiting', and_(recoveries.c.state == 'leased', recoveries.c.lease_expires_at <= now))
    rows = db.execute(select(recoveries).where(eligible).order_by(recoveries.c.next_retry_at, recoveries.c.turn_id).limit(32)).mappings().all()
    for row in rows:
        match = [recoveries.c.turn_id == row['turn_id'], recoveries.c.generation == row['generation'],
                 recoveries.c.state == row['state'], recoveries.c.attempt_count == row['attempt_count']]
        if row['lease_token']: match.append(recoveries.c.lease_token == row['lease_token'])
        expired = row['first_attempt_at'] and plus(row['first_attempt_at'], policy['budget_seconds']) <= now
        exhausted = row['attempt_count'] >= policy['attempts'] or expired
        cleanup_only = exhausted and row['state'] == 'leased'
        if exhausted and not cleanup_only:
            db.execute(update(recoveries).where(*match).values(state='paused', last_result='budget_exhausted', updated_at=now))
            continue
        if not cleanup_only and (not policy['enabled'] or row['next_retry_at'] > now): continue
        token = uuid4().hex
        values = dict(state='leased', attempt_count=row['attempt_count']+(0 if cleanup_only else 1), first_attempt_at=row['first_attempt_at'] or now,
                      lease_token=token, lease_expires_at=plus(now, 120), updated_at=now)
        if db.execute(update(recoveries).where(*match).values(**values)).rowcount:
            db.commit()
            return {**dict(row), **values, 'cleanup_only': cleanup_only}
    db.commit()
    return None


def fence(db, lease):
    """Conditional write holds the row lock through the caller's terminal transaction."""
    now = timestamp(clock(db))
    return bool(db.execute(update(recoveries).where(recoveries.c.turn_id == lease['turn_id'],
        recoveries.c.state == 'leased', recoveries.c.generation == lease['generation'],
        recoveries.c.lease_token == lease['lease_token'], recoveries.c.lease_expires_at > now)
        .values(updated_at=now)).rowcount)


def finish(db, lease, result, policy=None, *, now=None, jitter=None, metrics=None):
    policy = policy or recovery_policy()
    now = timestamp(now or clock(db))
    row = db.execute(select(recoveries).where(recoveries.c.turn_id == lease['turn_id'])).mappings().one()
    if row['lease_token'] != lease['lease_token'] or row['state'] != 'leased': return False
    terminal = db.scalar(select(turns.c.status).where(turns.c.id == row['turn_id'])) != 'unknown'
    exhausted = row['attempt_count'] >= policy['attempts'] or plus(row['first_attempt_at'], policy['budget_seconds']) <= now
    state = 'resolved' if terminal else 'paused' if exhausted or result in ('workspace_identity','security_rejected','cleanup_failed') else 'waiting'
    delay = min(policy['cap_seconds'], policy['base_seconds'] * 2 ** (row['attempt_count']-1))
    delay *= 1 + (random.random() if jitter is None else jitter) * .1
    next_at = plus(now, delay) if state == 'waiting' else None
    changed = db.execute(update(recoveries).where(recoveries.c.turn_id == row['turn_id'],
        recoveries.c.lease_token == lease['lease_token'], recoveries.c.state == 'leased')
        .values(state=state, last_result=result, next_retry_at=next_at, lease_token=None,
                lease_expires_at=None, updated_at=now)).rowcount
    if changed:
        from app.chat.recovery_observability import record
        record(db, row['turn_id'], state, result, row['attempt_count'], next_at, metrics or {})
    db.commit()
    return bool(changed)


def classify(error):
    if getattr(error, 'status', None) in (401, 403, 404): return 'security_rejected'
    if type(error).__name__ == 'WorkspaceError': return 'workspace_identity'
    code = str(getattr(error, 'code', ''))
    if 'timeout' in code or isinstance(error, TimeoutError): return 'timeout'
    if 'workspace' in code: return 'workspace_identity'
    if any(word in code for word in ('sandbox', 'preflight', 'credential', 'auth', 'permission')): return 'security_rejected'
    if code == 'executor_rpc_rejected': return 'rpc_rejected'
    if code in ('executor_turn_missing', 'executor_thread_missing'): return 'record_missing'
    return 'internal_error'


def resume(db, tid, expected_generation, request_id, actor, reason, *, authorize):
    if not authorize(): raise PermissionError('recovery_operator_required')
    if not all(isinstance(v, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}', v) for v in (request_id, reason)):
        raise ValueError('invalid_recovery_request')
    actor_hash = hashlib.sha256(actor.encode()).hexdigest()
    previous = db.execute(select(resumes).where(resumes.c.request_id == request_id)).mappings().first()
    if previous:
        if previous['turn_id'] != tid or previous['generation'] != expected_generation or previous['actor_hash'] != actor_hash or previous['reason'] != reason:
            raise ValueError('recovery_request_conflict')
        return False
    row = db.execute(select(recoveries).where(recoveries.c.turn_id == tid)).mappings().one()
    turn = db.execute(select(turns).where(turns.c.id == tid)).mappings().one()
    parent = db.execute(select(conversations).where(conversations.c.id == turn['conversation_id'])).mappings().one()
    if turn['status'] != 'unknown' or parent['active_turn_id'] != tid or not parent['thread_id'] or not turn['executor_turn_id']:
        raise ValueError('recovery_identity_changed')
    now = timestamp(clock(db))
    changed = db.execute(update(recoveries).where(recoveries.c.turn_id == tid,
        recoveries.c.state == 'paused', recoveries.c.generation == expected_generation,
        or_(recoveries.c.lease_expires_at.is_(None), recoveries.c.lease_expires_at <= now))
        .values(state='waiting', generation=expected_generation+1, attempt_count=0, first_attempt_at=None,
                next_retry_at=now, lease_token=None, lease_expires_at=None, updated_at=now)).rowcount
    if not changed: db.rollback(); raise ValueError('recovery_generation_conflict')
    summary = {key: row[key] for key in ('state','attempt_count','first_attempt_at','last_result')}
    db.execute(insert(resumes).values(request_id=request_id, turn_id=tid, generation=expected_generation,
        actor_hash=actor_hash, reason=reason, previous=json.dumps(summary), created_at=now))
    db.commit()
    return True
