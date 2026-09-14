"""Allowlisted summaries only; instrumentation failure never replaces the business outcome."""
import json
import logging
import re
from datetime import datetime,timedelta,timezone
from uuid import uuid4
from sqlalchemy import delete,insert,select,update
from app.chat import service
from app.chat.schema import audit,usage_events,task_traces,task_trace_spans
EVENTS={'governance.capture','governance.prepare','governance.apply','governance.document_save','chat.send','chat.stop','chat.retry','chat.session_create','chat.session_update','chat.session_delete','chat.relations_save'}
STAGES={'queued','connecting','running','completed','failed','stopped','unknown','stopping'}


def behavior(db,event,actor,rid,result,client_type,resource=None):
    if event not in EVENTS or client_type not in ('web','api'):return
    properties={key:value for key,value in (resource or {}).items() if key in ('turn_id','conversation_id','operation_id') and isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',value)}
    db.execute(insert(usage_events).values(**service.identity(),behavior_event_id=str(uuid4()),event_name=event,
        client_type=client_type,actor_user_id=actor,parent_request_id=rid,result=result,properties=json.dumps(properties)))


def trace(db,tid,stage,*,actor=None,request_id=None):
    if stage not in STAGES:return
    try:
        with db.begin_nested():
            row=db.execute(select(task_traces).where(task_traces.c.turn_id==tid)).mappings().first()
            if row is None:
                trace_id=str(uuid4())
                db.execute(insert(task_traces).values(**service.identity(),task_trace_id=trace_id,turn_id=tid,
                    parent_request_id=request_id,task_type='chat_execution',task_name='chat.turn',actor_user_id=actor,
                    status=stage,metadata='{}'))
            else:
                trace_id=row['task_trace_id']
                db.execute(update(task_traces).where(task_traces.c.id==row['id']).values(status=stage,
                    finished_at=service.now() if stage in service.TERMINAL else None,updated_at=service.now()))
            db.execute(insert(task_trace_spans).values(**service.identity(),task_trace_id=trace_id,
                span_name='chat.'+stage,status=stage,metadata='{}'))
    except Exception:logging.getLogger('moonbox.chat').warning('chat.trace_unavailable')


def prune(db):
    """Standard retention for this consumer only; unrelated instrumentation is untouched."""
    now=datetime.now(timezone.utc)
    cutoff=(now-timedelta(days=90)).isoformat(timespec='seconds')
    expired=list(db.scalars(select(task_traces.c.task_trace_id).where(task_traces.c.task_type=='chat_execution',task_traces.c.finished_at<cutoff)))
    if expired:
        db.execute(delete(task_trace_spans).where(task_trace_spans.c.task_trace_id.in_(expired)))
        db.execute(delete(task_traces).where(task_traces.c.task_trace_id.in_(expired)))
    db.execute(delete(audit).where(audit.c.created_at<cutoff))
    db.execute(delete(usage_events).where(usage_events.c.event_name.in_(EVENTS),usage_events.c.created_at<(now-timedelta(days=180)).isoformat(timespec='seconds')))
    db.commit()
