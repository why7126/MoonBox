"""Observe ASGI send ordering against real audit inserts, including backpressure."""
import asyncio
import json
import logging
from threading import BoundedSemaphore
import pytest
from fastapi import FastAPI, APIRouter
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse
from sqlalchemy import event, select
from app.chat.api import ChatRoute
from app.chat.schema import audit
from test_chat import chat


@pytest.mark.parametrize('method,path,deferred', [
    ('GET', '/api/v1/requirement-center/probe', True),
    ('PUT', '/api/v1/requirement-center/probe', False),
    ('GET', '/api/v1/chat/probe', False),
])
def test_response_send_and_audit_commit_order(chat, method, path, deferred):
    _, factory = chat
    with factory() as db: engine = db.get_bind()
    seen = []
    def insert_seen(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('INSERT INTO CHAT_REQUEST_LOGS'):
            seen.append('audit')
    router = APIRouter(route_class=ChatRoute)
    async def endpoint():
        return JSONResponse({'code': 0, 'data': {}}, background=BackgroundTask(lambda: seen.append('existing')))
    router.add_api_route(path, endpoint, methods=[method])
    app = FastAPI(); app.include_router(router)
    headers = {}
    async def invoke():
        async def receive(): return {'type': 'http.request', 'body': b'', 'more_body': False}
        async def send(message):
            if message['type'] == 'http.response.start': headers.update(dict(message['headers']))
            if message['type'] == 'http.response.body' and not message.get('more_body'):
                seen.append('body')
        await app({'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':method,
                   'scheme':'http','path':path,'raw_path':path.encode(),'query_string':b'',
                   'root_path':'','headers':[],'client':('test',1),'server':('test',80)}, receive, send)
    event.listen(engine, 'before_cursor_execute', insert_seen)
    try: asyncio.run(invoke())
    finally: event.remove(engine, 'before_cursor_execute', insert_seen)
    assert seen == (['body','audit','existing'] if deferred else ['audit','body','existing'])
    with factory() as db:
        row = db.execute(select(audit).where(audit.c.request_id == headers[b'x-request-id'].decode())).mappings().one()
        assert row['status_code'] == 200 and row['method'] == method


def test_capacity_fallback_does_not_drop_audit(chat, monkeypatch, caplog):
    from app.chat import request_audit
    slot = BoundedSemaphore(1); slot.acquire()
    monkeypatch.setattr(request_audit, '_slots', slot)
    with caplog.at_level(logging.WARNING, logger='moonbox.chat'):
        # This uses the same behavioral ordering check with an exhausted slot.
        test_response_send_and_audit_commit_order(chat, 'GET', '/api/v1/requirement-center/probe', False)
    assert 'chat.request_audit_capacity_fallback' in caplog.text


def test_deferred_failure_warns_releases_capacity_and_keeps_existing_task(monkeypatch, caplog):
    from app.chat import request_audit
    from starlette.requests import Request
    slots = BoundedSemaphore(1); monkeypatch.setattr(request_audit, '_slots', slots)
    seen = []
    response = JSONResponse({}, background=BackgroundTask(lambda: seen.append('existing')))
    request = Request({'type':'http','method':'GET','scheme':'http','path':'/api/v1/requirement-center/status','headers':[],'server':('test',80)})
    def fail(): raise RuntimeError('private failure must not be logged')
    with caplog.at_level(logging.INFO):
        assert request_audit.defer_read_audit(request, response, fail, 'safe-id')
        asyncio.run(response.background())
    assert seen == ['existing'] and slots.acquire(blocking=False)
    assert 'chat.request_log_unavailable' in caplog.text
    assert 'private failure' not in caplog.text
    row = next(json.loads(r.getMessage().split(' ',1)[1]) for r in caplog.records
               if r.getMessage().startswith('requirement_center.deferred_audit '))
    assert row['request_id'] == 'safe-id' and row['success'] is False and row['duration_ms'] >= 0


def test_abandoned_response_does_not_leak_reservation(monkeypatch):
    from app.chat import request_audit
    from starlette.requests import Request
    slots = BoundedSemaphore(1); monkeypatch.setattr(request_audit, '_slots', slots)
    request = Request({'type':'http','method':'GET','scheme':'http','path':'/api/v1/requirement-center/status','headers':[],'server':('test',80)})
    response = JSONResponse({})
    assert request_audit.defer_read_audit(request, response, lambda: True, 'safe-id')
    del response
    assert slots.acquire(blocking=False)
