"""Persistent object admission; terminal execution alone never proves delivery.

All mutations participate in the caller's transaction. A lease timeout cannot
release a guard. Operation IDs fence delayed workers and recovery callbacks.
"""
from sqlalchemy import Column, Integer, String, Table, and_, or_, insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.schema import metadata
from app.chat import service

execution_guards = Table(
    'governance_execution_guards', metadata,
    Column('scope_key', String(64), primary_key=True),
    Column('object_id', String(128), primary_key=True),
    Column('version', Integer, nullable=False, default=0),
    Column('operation_id', String(64)),
    Column('conversation_id', String(64)),
    Column('owner_id', String(64)),
    Column('action', String(64)),
    Column('client_request_id', String(64)),
    Column('request_fingerprint', String(64)),
    Column('state', String(32), nullable=False, default='idle'),
    Column('confirmed_stage', String(32)),
    Column('baseline_revision', String(64)),
    Column('result_revision', String(64)),
    Column('terminal_status', String(24)),
    Column('reason_code', String(64)),
    Column('updated_at', String(32), nullable=False),
)


execution_requests = Table(
    'governance_execution_requests', metadata,
    Column('scope_key', String(64), primary_key=True),
    Column('object_id', String(128), primary_key=True),
    Column('owner_id', String(64), primary_key=True),
    Column('client_request_id', String(64), primary_key=True),
    Column('request_fingerprint', String(64), nullable=False),
    Column('operation_id', String(64), nullable=False),
    Column('created_at', String(32), nullable=False),
)


def request(db, scope_key, object_id, owner_id, client_id, *, lock=False):
    r = execution_requests.c
    query = select(execution_requests).where(
        r.scope_key==scope_key, r.object_id==object_id,
        r.owner_id==owner_id, r.client_request_id==client_id)
    return db.execute(query.with_for_update() if lock else query).mappings().first()


class Replay(Exception):
    def __init__(self, operation_id):
        self.operation_id = operation_id


def read(db, scope_key, object_id):
    return db.execute(select(execution_guards).where(
        execution_guards.c.scope_key == scope_key,
        execution_guards.c.object_id == object_id)).mappings().first()


def acquire(db, *, scope_key, object_id, operation_id, conversation_id,
            owner_id, action, confirmed_stage, baseline_revision,
            client_request_id=None, request_fingerprint=None):
    """Acquire inside the same transaction that queues the turn (SQLite/MySQL)."""
    g = execution_guards.c
    if client_request_id:
        try:
            with db.begin_nested():
                db.execute(insert(execution_requests).values(
                    scope_key=scope_key, object_id=object_id, owner_id=owner_id,
                    client_request_id=client_request_id, request_fingerprint=request_fingerprint,
                    operation_id=operation_id, created_at=service.now()))
        except IntegrityError:
            previous = request(db, scope_key, object_id, owner_id, client_request_id, lock=True)
            if not previous or previous['request_fingerprint'] != request_fingerprint:
                raise service.ChatError(2504, '同一请求标识不能用于不同输入') from None
            raise Replay(previous['operation_id']) from None
    if read(db, scope_key, object_id) is None:
        try:
            with db.begin_nested():
                db.execute(insert(execution_guards).values(
                    scope_key=scope_key, object_id=object_id, state='idle',
                    version=0, updated_at=service.now()))
        except IntegrityError:
            pass
    won = db.execute(update(execution_guards).where(
        g.scope_key == scope_key, g.object_id == object_id,
        g.state.in_(('idle', 'validated', 'recovered_valid'))).values(
            version=g.version + 1, operation_id=operation_id,
            conversation_id=conversation_id, owner_id=owner_id, action=action,
            client_request_id=client_request_id, request_fingerprint=request_fingerprint,
            state='running', confirmed_stage=confirmed_stage,
            baseline_revision=baseline_revision, result_revision=None,
            terminal_status=None, reason_code=None, updated_at=service.now())).rowcount
    if won != 1:
        raise service.ChatError(2607, '该对象仍有执行或结果待核对，请查看原执行',
                                409, kind='governance_object_busy')
    return read(db, scope_key, object_id)


def terminal(db, operation_id, status):
    """Preserve artifacts and the original terminal, including failed/stopped."""
    if status not in ('completed', 'failed', 'stopped', 'unknown'):
        raise ValueError('unsupported terminal state')
    g = execution_guards.c
    return db.execute(update(execution_guards).where(
        g.operation_id == operation_id,
        or_(g.state == 'running', and_(g.state == 'needs_review', g.terminal_status == 'unknown'))).values(
            state='needs_review', terminal_status=status,
            reason_code='execution_unknown' if status == 'unknown' else 'result_unverified',
            updated_at=service.now())).rowcount


def confirm(db, *, scope_key, object_id, operation_id, version,
            result_revision, current_revision, stage, business_valid,
            sync_valid, execution_ended, recovery=False):
    """Internal verifier only: callers must obtain evidence, never user booleans."""
    if not (business_valid and sync_valid and execution_ended and result_revision
            and result_revision == current_revision):
        return False
    g = execution_guards.c
    conditions = [g.scope_key == scope_key, g.object_id == object_id,
                  g.operation_id == operation_id, g.version == version,
                  g.state == 'needs_review',
                  g.terminal_status.in_(('completed', 'failed', 'stopped') if recovery else ('completed',))]
    return db.execute(update(execution_guards).where(*conditions).values(
        state='recovered_valid' if recovery else 'validated',
        confirmed_stage=stage, result_revision=result_revision,
        reason_code=None, updated_at=service.now())).rowcount == 1


def public_state(row, actor):
    if not row:
        return {'execution_state': 'idle', 'can_send': True, 'reason_code': None}
    busy = row['state'] in ('running', 'needs_review')
    return {'execution_state': row['state'], 'can_send': not busy,
            'reason_code': row['reason_code'] or ('object_running' if busy else None),
            # Ownership is necessary but callers must also check conversation access.
            'view_conversation_id': row['conversation_id'] if row['owner_id'] == actor else None}


def observe(db, operation_id, event, *, object_id=None, action=None):
    """Best-effort bounded span, independent from the business guard record."""
    import logging
    from app.chat.schema import task_traces, task_trace_spans
    from app.chat.observability import _metadata
    try:
        with db.begin_nested():
            trace_id = db.scalar(select(task_traces.c.task_trace_id).where(task_traces.c.turn_id == operation_id))
            if trace_id:
                db.execute(insert(task_trace_spans).values(
                    **service.identity(), task_trace_id=trace_id,
                    span_name='governance.object_guard', status='completed',
                    metadata=_metadata({'turn_id': operation_id, 'object_id': object_id,
                                        'action_type': action, 'result': event})))
    except Exception:
        logging.getLogger(__name__).warning('governance.guard_observability_unavailable')


def restore_without_write(db, *, scope_key, object_id, operation_id, version, current_revision, verified_baseline_revision=None):
    """A confirmed ended attempt with unchanged facts can retry without advancing."""
    g = execution_guards.c
    return db.execute(update(execution_guards).where(
        g.scope_key==scope_key, g.object_id==object_id, g.operation_id==operation_id,
        g.version==version, g.state=='needs_review',
        g.terminal_status.in_(('completed','failed','stopped')),
        g.baseline_revision==(verified_baseline_revision or current_revision)
    ).values(state='idle', result_revision=current_revision,
             reason_code='no_governance_write', updated_at=service.now())).rowcount == 1
