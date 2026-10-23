"""Additional recovery references; never deletes shared journals or source files.

Existing artifact retention remains authoritative. A half-applied operation can
only release its extra hold after an authorized operator proves source consistency.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, update, text, delete
from app.chat import service
from app.chat.schema import turns, governance_applications as applications
from app.governance.recovery_schema import operations, attempts
from app.governance import durable_recovery as policy


def classify(db, operation):
    if operation['lease_owner']:
        return 'active_protected'
    terminal = db.scalar(select(turns.c.status).where(turns.c.id == operation['origin_turn_id']))
    if terminal not in ('completed', 'failed', 'stopped'):
        return 'active_protected'
    app = db.execute(select(applications).where(applications.c.id == operation['application_id'])).mappings().first()
    if app and app['state'] in ('applying', 'recovering', 'recovery_blocked'):
        return 'cleanup_blocked'
    if operation['retention_until'] and operation['retention_until'] > service.now():
        return 'retained'
    if operation['state'] == 'completed':
        return 'released'
    if operation['recovery_expires_at'] and operation['recovery_expires_at'] <= service.now():
        return 'cleanup_blocked'
    return 'retained'


def sweep(db):
    """Release only this feature's reference hold, not another owner's artifacts."""
    for operation in db.execute(select(operations)).mappings():
        state = classify(db, operation)
        if state == operation['retention_state']:
            continue
        changed = db.execute(update(operations).where(operations.c.id == operation['id'],
            operations.c.version == operation['version']).values(retention_state=state,
            artifacts_released_at=service.now() if state == 'released' else None,
            version=operations.c.version + 1, updated_at=service.now())).rowcount
        if changed:
            from app.governance.observability import trace
            trace(db, operation['id'], 'cleanup_blocked' if state == 'cleanup_blocked' else 'released' if state == 'released' else 'retained',
                  actor=operation['actor_id'], metadata={'operation_id':operation['id'], 'result':state})
    cutoff = policy.stamp(datetime.now(timezone.utc) - timedelta(days=90))
    expired = list(db.scalars(select(operations.c.id).where(
        operations.c.retention_state == 'released', operations.c.updated_at < cutoff)))
    if expired:
        db.execute(delete(attempts).where(attempts.c.operation_id.in_(expired)))
        db.execute(delete(operations).where(operations.c.id.in_(expired)))
    db.commit()


def dispose(db, actor, oid, expected_version, disposition):
    """Admin-only explicit recheck. Does not restore privileges, extend recovery or delete files."""
    from app.governance import scope
    operation = policy.row(db, oid)
    if not operation:
        raise service.ChatError(2502, '操作不存在或无权访问', 404)
    project = scope.authorize(db, actor, operation['space_id'], operation['repository_id'], write=True)
    if not scope.visible(db, actor, project, operation['object_id']):
        raise service.ChatError(2502, '操作不存在或无权访问', 404)
    administrator = db.scalar(text("""SELECT id FROM admin_spaces WHERE id=:space AND
        (owner_id=:actor OR EXISTS (SELECT 1 FROM admin_space_members WHERE space_id=:space
        AND user_id=:actor AND role='管理员'))"""), {'space': operation['space_id'], 'actor': actor})
    if not administrator or disposition not in ('recheck', 'retain_7_days'):
        raise service.ChatError(2601, '需要项目管理员明确处置', 403)
    from app.governance.writer import project_lock
    with project_lock(project):
        current = policy.row(db, oid)
        if current['version'] != expected_version:
            raise service.ChatError(2606, '操作版本已变化', 409)
        state = classify(db, current)
        if state == 'active_protected':
            raise service.ChatError(2607, '活动或未知事务不能处置', 409)
        values = {'retention_state':state}
        if disposition == 'retain_7_days':
            values['retention_until'] = policy.stamp(datetime.now(timezone.utc) + timedelta(days=7))
        elif state == 'cleanup_blocked':
            raise service.ChatError(2604, '半迁移尚未核验一致，保留最小证据', 409)
        else:
            values.update(retention_state='released', artifacts_released_at=service.now())
        db.execute(update(operations).where(operations.c.id == oid,
            operations.c.version == expected_version).values(**values,
            version=expected_version + 1, updated_at=service.now()))
        from app.governance.observability import trace
        trace(db, oid, 'recovery_blocked' if state == 'cleanup_blocked' else 'applied',
              actor=actor, metadata={'operation_id':oid, 'result':disposition})
        db.commit()
    return {'operation_id':oid, 'retention_state':values['retention_state']}
