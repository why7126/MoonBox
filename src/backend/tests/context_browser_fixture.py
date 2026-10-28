"""Explicit isolated HTTP fixture for BUG-0056; no product DB or auth data.

Run in the registered test container with BUG_READ_SOURCE pointing at the frozen
governance copy. Fixture routes are never imported by the application server.
"""
import os
import json
from pathlib import Path
import tempfile
import time
import asyncio

import pytest
import uvicorn
from sqlalchemy import text
from test_chat import chat
from test_governance_scope import bind
from app.main import app
from app.governance import snapshot, read_snapshot, read_memo


def clear_caches():
    read_snapshot.clear()
    read_memo.clear()
    with snapshot._validation_lock:
        snapshot._validated.clear()
    with snapshot._tree_lock:
        for directory, _, _ in snapshot._trees.values():
            directory.cleanup()
        snapshot._trees.clear()


def main():
    monkeypatch = pytest.MonkeyPatch()
    with tempfile.TemporaryDirectory(prefix='context-ui-') as directory:
        fixture = chat.__wrapped__(Path(directory), monkeypatch)
        _, factory = next(fixture)
        bind(monkeypatch, Path(os.environ['BUG_READ_SOURCE']))
        with factory() as db:
            for name, kind in [('code', 'TEXT'), ('description', 'TEXT'), ('member_count', 'INTEGER'), ('created_at', 'TEXT')]:
                db.execute(text(f'ALTER TABLE admin_spaces ADD COLUMN {name} {kind}'))
            for name in ('username', 'nickname', 'status', 'deleted_at'):
                db.execute(text(f'ALTER TABLE admin_users ADD COLUMN {name} TEXT'))
            db.execute(text('CREATE TABLE admin_space_products (space_id TEXT)'))
            db.commit()

        active = 0
        peak_active = 0

        @app.middleware('http')
        async def observe_load(request, call_next):
            nonlocal active, peak_active
            if request.url.path != '/api/v1/requirement-center/context':
                return await call_next(request)
            active += 1
            peak_active = active if active == 1 else max(peak_active, active)
            wall, cpu = time.perf_counter(), time.process_time()
            response = None
            try:
                response = await call_next(request)
                return response
            finally:
                record = {'request_id': response.headers.get('X-Request-ID') if response else None,
                          'wall_ms': (time.perf_counter()-wall)*1000,
                          'process_cpu_ms': (time.process_time()-cpu)*1000,
                          'peak_inflight': peak_active}
                active -= 1
                with Path('/results/http-load.jsonl').open('a') as stream:
                    stream.write(json.dumps(record) + '\n')

        @app.post('/api/fixture/context/reset')
        async def reset():
            # The browser first unmounts the previous page. Wait for any request
            # already admitted by that page before clearing application caches.
            while active:
                await asyncio.sleep(.01)
            clear_caches()
            return {'reset': True, 'os_page_cache_cleared': False}

        @app.post('/api/fixture/context/measurement')
        def measurement(value: dict):
            # Test-only numeric evidence sink; never persist document content.
            allowed = {'first_card_ms', 'context_ms', 'visible_cards', 'cold',
                       'os_page_cache_cleared', 'request_id', 'server_timing', 'status',
                       'first_card_in_viewport', 'viewport_width', 'viewport_height'}
            assert set(value) <= allowed
            with Path('/results/browser-final.jsonl').open('a') as stream:
                stream.write(json.dumps(value) + '\n')
            return {'recorded': True}

        try:
            uvicorn.run(app, host='0.0.0.0', port=8000, lifespan='off', log_level='error')
        finally:
            try:
                next(fixture)
            except StopIteration:
                pass
            monkeypatch.undo()


if __name__ == '__main__':
    main()
