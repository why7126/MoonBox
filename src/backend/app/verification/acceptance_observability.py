"""Bounded task facts; observability failure never changes acceptance decisions."""
import json
from uuid import uuid4
from sqlalchemy import insert, select, update
from app.chat.schema import task_traces, task_trace_spans
from app.chat.service import identity, now


def transition(db,row,status,request_id=None):
    metadata=json.dumps({'operation_id':row['id'],'attempt_id':row['attempt_id'],
        'source_turn_id':row['source_turn_id'],'change_id':row['change_id'],
        'stage':status,'reason_code':row.get('reason_code'),'cleanup_state':row['cleanup_state']})
    try:
        with db.begin_nested():
            trace=db.execute(select(task_traces).where(task_traces.c.turn_id==row['id'])).mappings().first()
            terminal=status in {'passed','failed','cancelled','blocked'}
            if trace:
                trace_id=trace['task_trace_id']
                db.execute(update(task_traces).where(task_traces.c.id==trace['id']).values(
                    status=status,metadata=metadata,updated_at=now(),finished_at=now() if terminal else None))
            else:
                trace_id=str(uuid4())
                db.execute(insert(task_traces).values(**identity(),task_trace_id=trace_id,turn_id=row['id'],
                    parent_request_id=request_id,task_type='chat_acceptance',task_name='acceptance.operation',
                    actor_user_id=row['actor_id'],status=status,metadata=metadata))
            db.execute(insert(task_trace_spans).values(**identity(),task_trace_id=trace_id,
                span_name='acceptance.'+status,status=status,metadata=metadata))
    except Exception:
        pass
