"""Capture instrumentation stores only opaque identifiers, bounded counts and phase names."""
import json
import logging
import re
from uuid import uuid4
from sqlalchemy import insert,select,update
from app.chat import service
from app.chat.api import ChatRoute
from app.chat.schema import audit,usage_events,task_traces,task_trace_spans


def opaque(value):
    return value if isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,64}',value) else None


def trace(db,tid,stage,*,actor=None,request_id=None,kind='capture_organize'):
    if not opaque(tid) or not re.fullmatch(r'(queued|running|ready|failed|prepared|applying|recovering|verified|conflict|recovery_blocked|file-\d{1,3})',stage):return
    try:
        with db.begin_nested():
            key='capture:'+tid
            row=db.execute(select(task_traces).where(task_traces.c.turn_id==key)).mappings().first()
            if row:trace_id=row['task_trace_id']
            else:
                trace_id=str(uuid4())
                db.execute(insert(task_traces).values(**service.identity(),task_trace_id=trace_id,turn_id=key,
                    parent_request_id=request_id,task_type=kind,task_name=kind,actor_user_id=actor,status=stage,metadata='{}'))
            db.execute(update(task_traces).where(task_traces.c.task_trace_id==trace_id).values(status=stage,updated_at=service.now(),
                finished_at=service.now() if stage in ('ready','verified','failed','conflict') else None))
            db.execute(insert(task_trace_spans).values(**service.identity(),task_trace_id=trace_id,span_name='capture.'+stage,status=stage,metadata='{}'))
    except Exception:logging.getLogger('moonbox.capture').warning('capture.trace_unavailable')


class CaptureRoute(ChatRoute):
    def get_route_handler(self):
        handler=super().get_route_handler()
        async def tracked(request):
            response=await handler(request)
            if self.path=='/api/v1/requirement-center/capture-materials/{media_id}/content':
                response.headers['Cache-Control']='private, no-store'
            bid=opaque(request.headers.get('X-Behavior-Event-ID'))
            chain=opaque(request.headers.get('X-Behavior-Trace-ID'))
            if not bid or not chain or request.headers.get('X-Chat-Client')!='web':return response
            names={'materials':'capture.upload','organize':'capture.organize','confirmations':'capture.confirm','retries':'capture.retry'}
            event=names.get(self.path.rsplit('/',1)[-1])
            if request.method=='PATCH':event='capture.review_save'
            if not event or request.method not in ('POST','PATCH'):return response
            actor=getattr(request.state,'chat_actor',None)
            if not actor:return response
            try:
                from app.chat.api import get_session_factory
                with get_session_factory()() as db:
                    rid=request.state.chat_request_id
                    old=db.scalar(select(audit.c.metadata).where(audit.c.request_id==rid))
                    metadata=json.loads(old or '{}');metadata.update(behavior_trace_id=chain,parent_behavior_event_id=bid)
                    db.execute(update(audit).where(audit.c.request_id==rid).values(metadata=json.dumps(metadata)))
                    existing=db.scalar(select(usage_events.c.id).where(usage_events.c.behavior_event_id==bid))
                    if not existing:
                        db.execute(insert(usage_events).values(**service.identity(),behavior_event_id=bid,event_name=event,
                            client_type='web',actor_user_id=actor,parent_request_id=rid,result='success' if response.status_code<400 else 'failure',
                            properties=json.dumps({'behavior_trace_id':chain})))
                    db.commit()
            except Exception:logging.getLogger('moonbox.capture').warning('capture.behavior_unavailable')
            return response
        return tracked
