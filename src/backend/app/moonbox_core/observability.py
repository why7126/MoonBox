"""Best-effort workspace spans; durable operation records remain the business authority."""
import json
from contextvars import ContextVar
import logging
import re
from uuid import uuid4
from sqlalchemy import insert, select, update
from app.chat.service import identity, now
from app.chat.schema import task_traces, task_trace_spans


request_context = ContextVar('workspace_request_id', default=None)

def record(db, operation_id, actor, kind, state, *, workspace_id=None, error_code=None):
    if kind not in ('restore', 'merge', 'candidate'):
        return
    data = {key: value for key, value in {'operation_id': operation_id, 'workspace_id': workspace_id,
        'error_code': error_code}.items() if isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value)}
    try:
        with db.begin_nested():
            previous = db.execute(select(task_traces).where(task_traces.c.turn_id == operation_id)).mappings().first()
            trace_id = previous['task_trace_id'] if previous else str(uuid4())
            if previous:
                db.execute(update(task_traces).where(task_traces.c.id == previous['id']).values(status=state,
                    finished_at=now() if state in ('completed', 'blocked', 'failed') else None, updated_at=now()))
            else:
                db.execute(insert(task_traces).values(**identity(), task_trace_id=trace_id, turn_id=operation_id,
                    task_type='workspace_operation', task_name='workspace.' + kind, actor_user_id=actor,
                    parent_request_id=request_context.get(),
                    status=state, metadata=json.dumps(data)))
            db.execute(insert(task_trace_spans).values(**identity(), task_trace_id=trace_id,
                span_name='workspace.' + kind + '.' + state, status=state, metadata=json.dumps(data)))
    except Exception:
        logging.getLogger('moonbox.workspace').warning('workspace_trace_unavailable')
