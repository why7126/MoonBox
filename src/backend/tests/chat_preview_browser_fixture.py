"""Opt-in local UI fixture. Temporary DB/auth only; never imports product data.
Run with PYTHONPATH=src/backend:src/backend/tests and point Vite at port 39047.
"""
import sys, tempfile, threading, json
from pathlib import Path
import pytest, uvicorn
from sqlalchemy import insert, update
from test_chat import chat, create, queued
from test_chat_final_answer import publish
from app.main import app
from app.chat import content_store, service, worker
from app.chat.content_schema import segments
from app.chat.schema import events, turns
from fastapi.responses import JSONResponse
mp=pytest.MonkeyPatch(); temp=tempfile.TemporaryDirectory(prefix='bug0067-'); fixture=chat.__wrapped__(Path(temp.name),mp);client,factory=next(fixture)
scenes={}
for mode in ['short','limited','error','final']:
 cid=create(client);tid=queued(factory,cid,'running')
 with factory() as db:
  text='中文流式输出，换行保留。\n' if mode=='short' else '这是已保存的过程输出。\n'
  oid=content_store.put(db,cid,'result',[text.encode()])
  count=294 if mode=='short' else 4097
  db.execute(insert(segments),[dict(**service.identity(),turn_id=tid,stream_id='output',source_event_id=f'{i:064x}',source_offset=0,sequence=i+1,object_id=oid) for i in range(count)])
  db.execute(insert(events).values(**service.identity(),turn_id=tid,sequence=1,source_id='fixture:output',event_type='execution.output',payload='{"text":"合成验收输出"}'))
  if mode=='final':
   publish(db,cid,tid,'verified',['最终答复：合法重复。合法重复。\n']*22)
   db.execute(update(turns).where(turns.c.id==tid).values(status='completed'))
  db.commit()
 scenes[mode]={'cid':cid,'tid':tid}
@app.get('/api/fixture/scenes')
def scene():return scenes
app.middleware_stack=None
@app.middleware('http')
async def error_scene(request,call_next):
 if request.url.path==f"/api/v1/chat/turns/{scenes['error']['tid']}/results":return JSONResponse({'code':2504,'message':'测试环境模拟读取失败，请重试'},status_code=503)
 return await call_next(request)
try:uvicorn.run(app,host='127.0.0.1',port=39047,lifespan='off',log_level='error')
finally:
 try:next(fixture)
 except StopIteration:pass
 mp.undo();temp.cleanup()
