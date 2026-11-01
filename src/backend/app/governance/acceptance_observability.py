"""Bounded optional UI check telemetry; never an authorization input."""
import json
import logging
from sqlalchemy import insert
from app.chat import service
from app.chat.schema import usage_events
from app.governance.capture_observability import opaque


def record_check(db, request, actor, *, event_name="requirement_center.acceptance_check"):
    if event_name not in ("requirement_center.acceptance_check", "requirement_center.priority_save"):
        return
    event = opaque(request.headers.get('X-Behavior-Event-ID'))
    chain = opaque(request.headers.get('X-Behavior-Trace-ID'))
    if request.headers.get('X-Chat-Client') != 'web' or not event or not chain:
        return
    try:
        with db.begin_nested():
            db.execute(insert(usage_events).values(
                **service.identity(), behavior_event_id=event,
                event_name=event_name, client_type='web',
                actor_user_id=actor, parent_request_id=request.state.chat_request_id,
                result='success', properties=json.dumps({'behavior_trace_id': chain})))
        db.commit()
    except Exception:
        logging.getLogger('moonbox.requirement_center').warning('acceptance_check.behavior_unavailable')
