"""Opt-in loopback fixture: synthetic SQLite, real chat APIs, no model or product DB."""
import asyncio
import json
import tempfile
from pathlib import Path
import pytest
import uvicorn
from fastapi.responses import JSONResponse
from sqlalchemy import insert, update
from test_chat import chat, create, queued
from app.main import app
from app.chat import service
from app.chat.schema import events, messages, conversations, turns


def main():
    mp = pytest.MonkeyPatch()
    with tempfile.TemporaryDirectory(prefix='bug0058-history-') as directory:
        fixture = chat.__wrapped__(Path(directory), mp)
        client, factory = next(fixture)
        samples = []
        for count, size in [(1, 404), (10, 404), (1, 200), (1, 1001), (1, 2)]:
            cid = create(client)
            for index in range(count):
                tid = queued(factory, cid, 'queued' if size == 2 else 'completed')
                with factory() as db:
                    db.execute(insert(messages).values(**service.identity(), turn_id=tid,
                        role='assistant', content=f'合成历史第 {index+1} 轮：已保存的最终正文。'))
                    for sequence in range(1, size+1):
                        kind = 'execution.usage' if sequence == size else 'execution.tool'
                        payload = {'total_tokens': 404, 'duration_ms': 2400} if kind.endswith('usage') else {'name':'synthetic-check','status':'completed'}
                        db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=sequence,
                            source_id=str(sequence), event_type=kind, payload=json.dumps(payload)))
                    db.execute(update(conversations).where(conversations.c.id == cid).values(active_turn_id=None))
                    db.commit()
            samples.append({'id':cid, 'label':f'{count}轮 / {size}事件', 'turns':count, 'events':size})
        @app.get('/api/fixture/history-scenes')
        def scenes():
            return samples
        @app.post('/api/fixture/history-state/{cid}/{state}')
        def state(cid: str, state: str):
            if cid != samples[-1]['id'] or state not in ('queued','running','stopping','unknown','completed'):
                return JSONResponse({'error':'invalid synthetic scene'},status_code=400)
            with factory() as db:
                db.execute(update(turns).where(turns.c.conversation_id == cid).values(status=state,updated_at=service.identity()['updated_at']))
                db.commit()
            return {'state':state}
        app.middleware_stack = None
        @app.middleware('http')
        async def slow_operation(request, call_next):
            if request.url.path == '/api/v1/chat/governance-operations/synthetic-slow':
                await asyncio.sleep(5)
                return JSONResponse({'code':0,'message':'ok','data':{'id':'synthetic-slow','state':'completed',
                    'version':2,'stage':'complete','allowed_actions':[],'verification_actions':[],
                    'historical_result':'verified','object_id':'synthetic-history'}})
            return await call_next(request)
        try:
            uvicorn.run(app, host='127.0.0.1', port=39047, lifespan='off', log_level='error')
        finally:
            try:
                next(fixture)
            except StopIteration:
                pass
            mp.undo()

if __name__ == '__main__':
    main()
