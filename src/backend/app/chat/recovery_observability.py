"""Allowlisted recovery diagnostics, independent of business terminal projection."""
import json
import logging
from sqlalchemy import select, insert
from app.chat import service
from app.chat.schema import task_traces, task_trace_spans


def record(db, tid, state, result, attempts, next_at, metrics):
    try:
        with db.begin_nested():
            trace_id = db.scalar(select(task_traces.c.task_trace_id).where(task_traces.c.turn_id == tid))
            if not trace_id:
                identity = service.identity(); trace_id = identity['id']
                db.execute(insert(task_traces).values(**identity, task_trace_id=trace_id, turn_id=tid,
                    task_type='chat_execution', task_name='chat.turn', status='unknown', metadata='{}'))
            safe = {'result': result, 'attempt_count': attempts, 'next_retry_at': next_at}
            for key in ('containers_created', 'containers_removed', 'cache_hit', 'duration_ms', 'container_metrics_available'):
                if type(metrics.get(key)) in (int, bool): safe[key] = metrics[key]
            db.execute(insert(task_trace_spans).values(**service.identity(), task_trace_id=trace_id,
                span_name='chat.unknown_recovery', status=state, metadata=json.dumps(safe)))
    except Exception:
        logging.getLogger('moonbox.chat').warning('chat.recovery_trace_unavailable')
