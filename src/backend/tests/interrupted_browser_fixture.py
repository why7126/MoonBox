"""Explicit isolated HTTP sample: real verification API, synthetic stopped turn."""
import asyncio
import tempfile
from pathlib import Path
import pytest
import uvicorn
from test_chat import chat
from test_governance_writer import writing
from test_direct_completion import direct_scene, CHANGE
from test_successor_completion import successor_scene
from test_interrupted_successor import interrupted
from app.main import app


def main():
    mp = pytest.MonkeyPatch()
    with tempfile.TemporaryDirectory(prefix='bug0069-browser-') as directory:
        root = Path(directory).resolve()
        fixture = chat.__wrapped__(root, mp)
        pair = next(fixture)
        writer = writing.__wrapped__(pair, root, mp)
        scene = interrupted.__wrapped__(successor_scene.__wrapped__(direct_scene.__wrapped__(writer, pair)))
        _, project, tid, _, _ = scene
        design = project.root / 'openspec/changes' / CHANGE / 'design.md'
        original = design.read_bytes()

        @app.get('/api/fixture/scene')
        def metadata():
            return {'turn_id': tid, 'synthetic_identity': True, 'real_api': True}

        @app.post('/api/fixture/stale/{enabled}')
        def stale(enabled: bool):
            design.write_bytes(b'stale input' if enabled else original)
            return {'stale': enabled}

        app.middleware_stack = None

        @app.middleware('http')
        async def visible_busy(request, call_next):
            if request.method == 'POST' and request.url.path.endswith('/completion-verification'):
                await asyncio.sleep(2)
            return await call_next(request)

        try:
            uvicorn.run(app, host='127.0.0.1', port=39048, lifespan='off', log_level='error')
        finally:
            try:
                next(fixture)
            except StopIteration:
                pass
            mp.undo()


if __name__ == '__main__':
    main()
