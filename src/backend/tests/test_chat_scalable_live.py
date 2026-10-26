"""Opt-in real model round trips with synthetic identity and disposable storage."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import hashlib
import pytest
from sqlalchemy import select
from test_chat import chat, create
from app.chat import settings, worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.container_server import persistent_container_server, ContainerAppServer
from app.chat.schema import turns
from app.governance.prepare_recovery import request

@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE') != '1', reason='explicit disposable live probe required')
def test_real_first_and_same_turn_preparation_resume(chat,tmp_path,monkeypatch):
    tmp_path=tmp_path.resolve()
    client,factory=chat;runtime=tmp_path/'runtime';runtime.mkdir(mode=0o700)
    monkeypatch.delenv('MOONBOX_CHAT_LIMITS',raising=False)
    monkeypatch.setattr('app.chat.isolated.allowed',lambda *args:True)
    # The subprocess deliberately has a private HOME. Pin the already selected
    # local Docker socket so it does not depend on a personal Docker config there.
    endpoint=subprocess.run(['docker','context','inspect','--format','{{.Endpoints.docker.Host}}'],
        capture_output=True,text=True,check=True).stdout.strip()
    assert endpoint.startswith('unix://')
    for name in ('version_command','launch_command'):
        original=getattr(ContainerAppServer,name)
        def command(self,executable,original=original):
            args=original(self,executable)
            return [args[0],'--host',endpoint,*args[1:]]
        monkeypatch.setattr(ContainerAppServer,name,command)
    report={'real_model':True,'identity':'synthetic isolated API actor','rounds':[]}
    from app.chat import execution
    original_failure=execution.mark_setup_failed
    def diagnostic(*args,**kwargs):
        import traceback
        cause=kwargs.get('cause')
        if cause:
            print('PREPARATION_FRAMES',[(Path(frame.filename).name,frame.lineno,frame.name)
                for frame in traceback.extract_tb(cause.__traceback__)],flush=True)
        return original_failure(*args,**kwargs)
    monkeypatch.setattr(execution,'mark_setup_failed',diagnostic)
    def server(path):return persistent_container_server(path,runtime,Path.home()/'.codex/auth.json')
    try:
        for recovery in (False,True):
            cid=create(client);work=tmp_path/cid
            if not recovery:work.mkdir()
            if work.exists(): subprocess.run(['git','init','-q',str(work)],check=True)
            with factory() as db:
                row=enqueue(db,'alice',cid,'live','Reply exactly: storage probe complete. Do not use tools or modify files.',settings.execution_limits())
                token=worker.claim(db,'live-capacity-probe')
            attempt=None
            if recovery:
                assert run_claim(factory,token,work,server,max_seconds=120)=='failed'
                work.mkdir()
                subprocess.run(['git','init','-q',str(work)],check=True)
                with factory() as db:
                    result=request(db,'alice',row['id'],'resume_prepare','live-resume')
                    attempt=result['attempt_id'];assert result['turn_id']==row['id']
                    token=worker.claim(db,'live-capacity-probe-resume')
            status=run_claim(factory,token,work,server,max_seconds=120)
            with factory() as db:
                error=db.scalar(select(turns.c.error_code).where(turns.c.id==row['id']))
            assert status=='completed',error
            response=client.get(f'/api/v1/chat/turns/{row["id"]}/results',params={'stream_id':'final'})
            assert response.status_code==200
            data=response.json()['data']
            assert 'storage probe complete' in ''.join(item['text'] for item in data['items']).lower()
            assert data['has_final']
            # Close/reopen DB sessions and read the same persisted result independently.
            again=client.get(f'/api/v1/chat/turns/{row["id"]}/results',params={'stream_id':'final'}).json()['data']
            assert again['items']==data['items']
            with factory() as db:
                database_url = str(db.get_bind().url)
            reader = '''import hashlib,json,sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.chat.result_reader import results
with Session(create_engine(sys.argv[1])) as db:
 page=results(db,'alice',sys.argv[2],stream='final')
 print(hashlib.sha256(''.join(item['text'] for item in page['items']).encode()).hexdigest())
'''
            restarted = subprocess.run([sys.executable,'-c',reader,database_url,row['id']],
                capture_output=True,text=True,check=True)
            expected = hashlib.sha256(''.join(item['text'] for item in data['items']).encode()).hexdigest()
            assert restarted.stdout.strip() == expected
            report['rounds'].append({'turn_id':row['id'],'attempt_id':attempt,'recovered':recovery,
                'status':status,'committed_sequence':data['committed_sequence'],'reread_matches':True,
                'fresh_process_read_matches':True,'result_sha256':expected})
    finally:
        shutil.rmtree(runtime)
    report['runtime_removed']=not runtime.exists()
    print('LIVE_SCALABLE',json.dumps(report),flush=True)
