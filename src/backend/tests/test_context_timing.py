"""Normal HTTP correlation, stage accounting and safe failure timing."""
import json
import logging
from sqlalchemy import select
from app.chat.schema import audit
from test_chat import chat
from test_governance_scope import bind, fixture_tree
from test_context_resources import database_columns


def test_http_stage_accounting_and_error_correlation(chat, tmp_path, monkeypatch, caplog):
    client, factory = chat
    database_columns(factory)
    root = fixture_tree(tmp_path / 'source')
    bind(monkeypatch, root)
    caplog.set_level(logging.INFO, logger='moonbox.requirement_center')
    from app.governance.reader import ProjectReader
    import time
    original = ProjectReader.call
    def with_endpoint_tail(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        time.sleep(.025)
        return result
    monkeypatch.setattr(ProjectReader, 'call', with_endpoint_tail)
    response = client.get('/api/v1/requirement-center/context', params={'space_id': 'space', 'repository_id': 'repo'})
    assert response.status_code == 200
    metrics = {item.strip().split(';dur=')[0]: float(item.split(';dur=')[1])
               for item in response.headers['Server-Timing'].split(',')}
    exclusive = ('snapshot_and_fences', 'materialize', 'object_authorization', 'parse', 'cleanup',
                 'reconcile', 'external_reconcile', 'card_projection_exclusive',
                 'projection_commit', 'document_projection', 'reader_orchestration')
    assert abs(sum(metrics[key] for key in exclusive) - metrics['total']) < .1
    assert abs(metrics['snapshot'] + metrics['fences_exclusive'] - metrics['snapshot_and_fences']) < .1
    route_parts = sum(metrics[key] for key in ('dependencies', 'total', 'response_finalize', 'request_audit', 'request_audit_dispatch', 'endpoint_overhead'))
    assert abs(metrics['route_total'] - route_parts) < 10
    assert metrics['endpoint_overhead'] >= 20
    assert metrics['request_audit'] == 0
    logs = [json.loads(record.getMessage().split(' ', 1)[1]) for record in caplog.records
            if record.getMessage().startswith('requirement_center.http_timing ')]
    assert logs[-1]['request_id'] == response.headers['X-Request-ID']
    with factory() as db:
        recorded = db.execute(select(audit).where(audit.c.request_id == response.headers['X-Request-ID'])).mappings().one()
        assert recorded['status_code'] == 200
    assert str(root) not in json.dumps(logs)
    (root / 'issues/bugs/_registry.yaml').write_text('entries: [private-invalid-body')
    error = client.get('/api/v1/requirement-center/context', params={'space_id': 'space', 'repository_id': 'repo'})
    assert error.status_code == 503
    assert error.json()['data']['request_id'] == error.headers['X-Request-ID']
    assert 'private-invalid-body' not in caplog.text


def test_audit_is_durable_before_response_without_blocking_event_loop(chat):
    import asyncio
    import threading
    import httpx
    from sqlalchemy import event
    client, factory = chat
    with factory() as db: engine = db.get_bind()
    threads = []
    def executing(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('INSERT INTO CHAT_REQUEST_LOGS'):
            threads.append(threading.get_ident())
    event.listen(engine, 'before_cursor_execute', executing)
    async def request():
        loop_thread = threading.get_ident()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=client.app), base_url='http://test') as http:
            response = await http.get('/api/v1/chat/conversations', params={'space_id': 'space'})
        assert response.status_code == 200
        assert threads and all(thread != loop_thread for thread in threads)
        with factory() as db:
            row = db.execute(select(audit).where(audit.c.request_id == response.headers['X-Request-ID'])).mappings().one()
            assert row['status_code'] == 200
    try:
        asyncio.run(request())
    finally:
        event.remove(engine, 'before_cursor_execute', executing)


def test_audit_skips_unchanged_metadata_and_targets_only_inserted_row(chat, monkeypatch):
    from fastapi import FastAPI, APIRouter, Request
    from fastapi.testclient import TestClient
    from sqlalchemy import event, insert
    from app.chat.api import ChatRoute
    from app.chat import service
    client, factory = chat
    with factory() as db:
        engine = db.get_bind()
        history = service.identity()
        db.execute(insert(audit).values(**history, request_id='historical',
            route_template='/old', method='GET', status_code=200, duration_ms=1,
            metadata='{"preserve":"history"}'))
        db.commit()
    updates = []
    def executing(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith('UPDATE CHAT_REQUEST_LOGS'):
            updates.append(statement)
    event.listen(engine, 'before_cursor_execute', executing)
    try:
        response = client.get('/api/v1/chat/conversations', params={'space_id': 'space'})
        assert response.status_code == 200
        assert updates == []
        router = APIRouter(route_class=ChatRoute)
        @router.post('/api/v1/chat/conversations/{cid}/turns')
        def synthetic(request: Request):
            request.state.chat_actor = 'alice'
            return {'code': 0, 'data': {'id': 'synthetic-turn', 'image_count': 1,
                'skill_count': 2, 'effective_config': {'model': 'synthetic-model'}}}
        observed = []
        monkeypatch.setattr('app.chat.observability.behavior', lambda *args: observed.append(args))
        test_app = FastAPI(); test_app.include_router(router)
        with TestClient(test_app) as http:
            response = http.post('/api/v1/chat/conversations/synthetic/turns', headers={'X-Chat-Client': 'web'})
        assert response.status_code == 200 and len(observed) == 1
        assert len(updates) == 1 and 'WHERE chat_request_logs.id =' in updates[0]
        with factory() as db:
            old = db.execute(select(audit).where(audit.c.id == history['id'])).mappings().one()
            assert old['metadata'] == '{"preserve":"history"}'
            row = db.execute(select(audit).where(audit.c.request_id == response.headers['X-Request-ID'])).mappings().one()
            assert json.loads(row['metadata']) == {'image_count': 1, 'skill_count': 2, 'model': 'synthetic-model'}
    finally:
        event.remove(engine, 'before_cursor_execute', executing)
