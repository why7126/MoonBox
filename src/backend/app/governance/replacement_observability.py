"""Non-authoritative telemetry. Signed authorization events are stored separately."""
import json
import logging
from uuid import uuid4
from sqlalchemy import insert, select, update
from app.chat.api import ChatRoute
from app.chat import service
from app.chat.schema import usage_events, audit, task_traces, task_trace_spans
from .capture_observability import opaque


def trace(db, proposal_id, stage, *, actor, request_id):
    if stage not in {'prepared','approved','rejected','revoked','claimed','merge_verified','move_verified','synced','completed'}:
        return
    try:
        with db.begin_nested():
            correlation='replacement:'+proposal_id
            tid=db.scalar(select(task_traces.c.task_trace_id).where(task_traces.c.turn_id==correlation))
            if not tid:
                tid=str(uuid4())
                db.execute(insert(task_traces).values(**service.identity(),task_trace_id=tid,turn_id=correlation,
                    parent_request_id=request_id,task_type='rule_replacement',task_name='replacement.authorization',
                    actor_user_id=actor,status=stage,metadata='{}'))
            db.execute(update(task_traces).where(task_traces.c.task_trace_id==tid).values(status=stage,updated_at=service.now()))
            db.execute(insert(task_trace_spans).values(**service.identity(),task_trace_id=tid,
                span_name='replacement.'+stage,status=stage,metadata='{}'))
    except Exception:
        logging.getLogger('moonbox.replacement').warning('replacement.trace_unavailable')


class ReplacementRoute(ChatRoute):
    def get_route_handler(self):
        handler=super().get_route_handler()
        async def tracked(request):
            response=await handler(request)
            response.headers['Cache-Control']='private, no-store'
            event_id=opaque(request.headers.get('X-Behavior-Event-ID'))
            trace_id=opaque(request.headers.get('X-Behavior-Trace-ID'))
            actor=getattr(request.state,'chat_actor',None)
            if not actor or request.method!='POST' or request.headers.get('X-Chat-Client')!='web' or not event_id or not trace_id:
                return response
            action=request.path_params.get('action')
            event='rule_change.decision' if self.path.endswith('/rule-changes/decision') else 'replacement.'+action if action in {'approve','reject','revoke'} else 'replacement.bootstrap_confirm' if self.path.endswith('/confirm') else 'replacement.bootstrap_resume' if self.path.endswith('/resume') else 'replacement.archive' if 'replacement-archive-operations' in self.path or 'archive-commands' in self.path else 'replacement.prepare'
            try:
                from app.db.session import get_session_factory
                with get_session_factory()() as db:
                    rid=request.state.chat_request_id
                    existing=db.scalar(select(usage_events.c.id).where(usage_events.c.behavior_event_id==event_id))
                    if not existing:
                        db.execute(insert(usage_events).values(**service.identity(),behavior_event_id=event_id,event_name=event,
                            client_type='web',actor_user_id=actor,parent_request_id=rid,result='success' if response.status_code<400 else 'failure',
                            properties=json.dumps({'behavior_trace_id':trace_id})))
                    meta=json.loads(db.scalar(select(audit.c.metadata).where(audit.c.request_id==rid)) or '{}')
                    meta.update(behavior_trace_id=trace_id,parent_behavior_event_id=event_id)
                    db.execute(update(audit).where(audit.c.request_id==rid).values(metadata=json.dumps(meta)))
                    db.commit()
            except Exception:
                logging.getLogger('moonbox.replacement').warning('replacement.telemetry_unavailable')
            return response
        return tracked
