"""Persistent recovery policy. Queries never advance stages or invoke the model."""
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from uuid import uuid4
from sqlalchemy import insert, select, update
from app.chat import service
from app.governance.recovery_schema import operations, attempts

ACTIONS = frozenset(('req-review', 'bug-review'))
STAGES = ('prepare', 'generation', 'validation', 'apply', 'readback', 'complete')
BACKOFF = (2, 10, 30)
TRANSIENT = frozenset(('storage_unavailable', 'connection_unavailable', 'uncommitted_timeout'))


def stamp(value=None):
    return (value or datetime.now(timezone.utc)).isoformat(timespec='seconds')


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def expiry(terminal_at, limits, existing=None):
    if not terminal_at or limits is None:
        return existing
    terminal = datetime.fromisoformat(terminal_at)
    deadlines = [terminal + timedelta(days=7)]
    for key in ('executor_delete_seconds', 'backup_expiry_seconds'):
        seconds = limits.get(key)
        if seconds is not None:
            deadlines.append(terminal + timedelta(seconds=seconds))
    if existing:
        deadlines.append(datetime.fromisoformat(existing))
    return stamp(min(deadlines))


def compatible(declarations, action):
    if len(declarations) != 3 or action not in ACTIONS:
        return False
    try:
        return all(d['schema_min'] <= 1 <= d['schema_max'] and action in d['actions'] for d in declarations)
    except (KeyError, TypeError):
        return False


def row(db, oid):
    return db.execute(select(operations).where(operations.c.id == oid)).mappings().first()


def create(db, *, actor, project, parent, action, object_id, request_key, request_hash,
           source_hash, candidate_id=None):
    if action not in ACTIONS:
        return None
    match = (operations.c.actor_id == actor, operations.c.scope_key == project.key,
             operations.c.action == action, operations.c.request_key == request_key)
    old = db.execute(select(operations).where(*match)).mappings().first()
    if old:
        if old['request_hash'] != request_hash:
            raise service.ChatError(2606, '同一操作标识不能用于不同输入', 409)
        return old['id']
    if candidate_id and db.scalar(select(operations.c.id).where(operations.c.candidate_id == candidate_id)):
        raise service.ChatError(2606, '准备成果已关联其他请求，请核查原操作', 409)
    previous = db.scalar(select(operations.c.id).where(
        operations.c.actor_id == actor, operations.c.scope_key == project.key,
        operations.c.object_id == object_id).order_by(operations.c.created_at.desc()).limit(1))
    values = dict(service.identity(), actor_id=actor, scope_key=project.key,
        space_id=parent['space_id'], repository_id=parent['repository_id'], conversation_id=parent['id'],
        action=action, object_id=object_id, request_key=request_key, request_hash=request_hash,
        source_hash=source_hash, binding_revision=project.binding_revision, candidate_id=candidate_id,
        parent_operation_id=previous)
    db.execute(insert(operations).values(**values))
    return values['id']


def advance(db, oid, stage, *, state='active', reason=None, **values):
    if stage not in STAGES:
        raise ValueError('invalid_recovery_stage')
    current = row(db, oid)
    if not current:
        return
    if current['state'] == 'completed':
        state, reason = 'completed', None
    if STAGES.index(stage) < STAGES.index(current['stage']):
        stage = current['stage']
    changed = db.execute(update(operations).where(operations.c.id == oid,
        operations.c.version == current['version']).values(stage=stage, state=state,
        reason_code=reason, version=current['version'] + 1, updated_at=service.now(), **values)).rowcount
    if not changed:
        raise service.ChatError(2606, '操作状态已变化，请刷新', 409)


def claim(db, oid, expected_version, key, *, kind='manual', request_id=None, now=None):
    """Caller verifies authorization and holds the existing project fence before claim."""
    if kind not in ('manual', 'auto'):
        raise ValueError('invalid_attempt_kind')
    now = now or datetime.now(timezone.utc)
    request_hash = fingerprint({'operation_id': oid, 'version': expected_version, 'kind': kind})
    old = db.execute(select(attempts).where(attempts.c.operation_id == oid,
        attempts.c.request_key == key)).mappings().first()
    if old:
        if old['request_hash'] != request_hash:
            raise service.ChatError(2606, '同一恢复请求不能用于不同输入', 409)
        return dict(old), False
    current = row(db, oid)
    if not current or current['version'] != expected_version:
        raise service.ChatError(2606, '操作版本已变化，请刷新', 409)
    if current['state'] == 'completed' or current['lease_owner']:
        raise service.ChatError(2607, '操作已结束或仍在执行', 409)
    if not current['recovery_expires_at'] or current['recovery_expires_at'] <= stamp(now):
        raise service.ChatError(2604, '恢复窗口已过期或保留策略不可确认', 409)
    if kind == 'auto' and (current['auto_retry_count'] >= 3 or
        current['reason_code'] not in TRANSIENT or current['execution_terminal'] == 'stopped' or
        (current['next_retry_at'] and current['next_retry_at'] > stamp(now))):
        raise service.ChatError(2604, '当前操作不允许自动重试', 409)
    token = current['fencing_token'] + 1
    aid = service.identity()
    count = 'auto_retry_count' if kind == 'auto' else 'manual_count'
    updated = db.execute(update(operations).where(operations.c.id == oid,
        operations.c.version == expected_version, operations.c.lease_owner.is_(None)).values(
        state='active', lease_owner=aid['id'], lease_until=stamp(now + timedelta(seconds=30)),
        fencing_token=token, version=expected_version + 1, updated_at=stamp(now),
        **{count: current[count] + 1})).rowcount
    if not updated:
        # Refresh the transaction snapshot after losing a concurrent CAS.
        db.rollback()
        replay = db.execute(select(attempts).where(attempts.c.operation_id == oid,
            attempts.c.request_key == key)).mappings().first()
        if replay and replay['request_hash'] == request_hash:
            return dict(replay), False
        raise service.ChatError(2607, '操作已被其他执行器领取', 409)
    attempt = dict(aid, operation_id=oid, request_key=key, request_hash=request_hash,
                   kind=kind, fencing_token=token, state='claimed', request_id=request_id)
    db.execute(insert(attempts).values(**attempt))
    return attempt, True


def release(db, oid, attempt, *, state, reason=None, now=None):
    now = now or datetime.now(timezone.utc)
    current = row(db, oid)
    delay = BACKOFF[current['auto_retry_count']] if current['auto_retry_count'] < 3 else None
    retry_at = stamp(now + timedelta(seconds=delay)) if delay is not None and reason in TRANSIENT else None
    changed = db.execute(update(operations).where(operations.c.id == oid,
        operations.c.lease_owner == attempt['id'], operations.c.fencing_token == attempt['fencing_token']).values(
        state=state, reason_code=reason, lease_owner=None, lease_until=None,
        next_retry_at=retry_at, version=operations.c.version + 1, updated_at=stamp(now))).rowcount
    if not changed:
        raise service.ChatError(2607, '恢复领取权已失效', 409)
    db.execute(update(attempts).where(attempts.c.id == attempt['id']).values(
        state=state, reason_code=reason, updated_at=stamp(now)))
