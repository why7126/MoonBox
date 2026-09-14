"""Only opaque operation IDs and fixed stages; never record candidate/document bodies."""
import logging
from datetime import datetime,timedelta,timezone
from uuid import uuid4
from sqlalchemy import insert,select,update,delete
from app.chat import service
from app.chat.schema import task_traces,task_trace_spans
STAGES={'prepared','running','pending','rejected','queued','applying','recovering','applied','conflict','failed','recovery_blocked'}


def trace(db,oid,stage,*,actor=None,request_id=None):
    if stage not in STAGES:return
    try:
        with db.begin_nested():
            # Existing trace table's turn_id is a generic unique correlation slot.
            # Prefix prevents collisions with Chat UUIDs; task_type keeps consumers separate.
            identity='governance:'+oid
            row=db.execute(select(task_traces).where(task_traces.c.turn_id==identity)).mappings().first()
            if row:
                tid=row['task_trace_id']
                db.execute(update(task_traces).where(task_traces.c.id==row['id']).values(status=stage,updated_at=service.now(),
                    finished_at=service.now() if stage in ('applied','conflict','failed','rejected') else None))
            else:
                tid=str(uuid4())
                db.execute(insert(task_traces).values(**service.identity(),task_trace_id=tid,turn_id=identity,parent_request_id=request_id,
                    task_type='governance_application',task_name='governance.operation',actor_user_id=actor,status=stage,metadata='{}'))
            db.execute(insert(task_trace_spans).values(**service.identity(),task_trace_id=tid,span_name='governance.'+stage,status=stage,metadata='{}'))
    except Exception:logging.getLogger('moonbox.governance').warning('governance.trace_unavailable')


def prune(db):
    cutoff=(datetime.now(timezone.utc)-timedelta(days=90)).isoformat(timespec='seconds')
    ids=list(db.scalars(select(task_traces.c.task_trace_id).where(task_traces.c.task_type=='governance_application',task_traces.c.finished_at<cutoff)))
    if ids:
        db.execute(delete(task_trace_spans).where(task_trace_spans.c.task_trace_id.in_(ids)))
        db.execute(delete(task_traces).where(task_traces.c.task_trace_id.in_(ids)))
    db.commit()
