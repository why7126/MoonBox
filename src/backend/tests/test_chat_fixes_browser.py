"""Opt-in real Chromium + HTTP + automatic controller, using isolated synthetic data."""
import os
import json
import socket
import subprocess
import threading
import time
from pathlib import Path
import pytest
from test_direct_completion import direct_scene
from test_governance_writer import writing
from test_chat import chat

@pytest.mark.skipif(os.environ.get('CHAT_BROWSER_TEST')!='1',reason='explicit browser integration run')
def test_browser_auto_verification_and_answer(direct_scene,chat,tmp_path):
    import uvicorn
    from app.main import app
    from app.governance import store
    from app.governance.completion_handoff import tick
    from app.chat import content_store,final_answer
    from app.chat.schema import turns
    from sqlalchemy import select
    factory,project,tid,rid,version=direct_scene
    record=store.read(rid,'operation');record['classification']='sync_completed_unverified';store.write(rid,'operation',record)
    with factory() as db:
        cid=db.scalar(select(turns.c.conversation_id).where(turns.c.id==tid))
        for source in ['final:same','recovered-final:same']:
            content_store.result(db,cid,tid,'final',source,0,'重复措辞。重复措辞。'.encode())
        final_answer.mark(db,tid,'final:same','begin');final_answer.mark(db,tid,'final:same','complete');db.commit()
    def port():
        with socket.socket() as s:s.bind(('127.0.0.1',0));return s.getsockname()[1]
    api_port,web_port=port(),port()
    server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=api_port,log_level='error',lifespan='off'))
    thread=threading.Thread(target=server.run,daemon=True);thread.start()
    root=Path(__file__).resolve().parents[3];web=root/'src/web'
    env={**os.environ,'VITE_API_BASE_URL':f'http://127.0.0.1:{api_port}'}
    log=(tmp_path/'vite.log').open('w')
    vite=subprocess.Popen([str(web/'node_modules/.bin/vite'),'--host','127.0.0.1','--port',str(web_port),'--strictPort'],cwd=web,env=env,stdout=log,stderr=log)
    timer=None
    try:
        import urllib.request
        for _ in range(100):
            try:
                urllib.request.urlopen(f'http://127.0.0.1:{web_port}/e2e/chat-fixes.html',timeout=.2)
                if server.started:break
            except Exception:time.sleep(.1)
        # Wait for the first actual GET before advancing the real controller.
        from app.governance import direct_completion
        original=direct_completion.status
        seen=threading.Event()
        def observed(*args,**kwargs):
            result=original(*args,**kwargs);seen.set();return result
        direct_completion.status=observed
        def verify():
            if seen.wait(15):
                time.sleep(1);tick(factory)
        timer=threading.Thread(target=verify,daemon=True);timer.start()
        env.update(CHAT_BROWSER_URL=f'http://127.0.0.1:{web_port}/e2e/chat-fixes.html?turn={tid}',
                   CHAT_BROWSER_SCREENSHOT=str(tmp_path/'browser.png'))
        result=subprocess.run(['node','e2e/chat-fixes.mjs'],cwd=web,env=env,capture_output=True,text=True,timeout=40)
        assert result.returncode==0,result.stderr
        evidence=Path(os.environ['CHAT_BROWSER_EVIDENCE']);evidence.mkdir(parents=True,exist_ok=True)
        (evidence/'browser.json').write_text(result.stdout)
        (evidence/'browser.png').write_bytes((tmp_path/'browser.png').read_bytes())
    finally:
        if timer:timer.join(timeout=20)
        if 'original' in locals():direct_completion.status=original
        vite.terminate();vite.wait(timeout=10);log.close()
        server.should_exit=True;thread.join(timeout=10)
