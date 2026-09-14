"""显式本地登录验证；独立测试DB和合成业务身份，不启用正式服务。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import pytest
from sqlalchemy import select
from test_chat import chat, governance, create, allow_governed_write
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.local_probe import local_executor
from app.chat.schema import turns, conversations, reservations

LIMITS = dict(user_concurrency=1,space_concurrency=1,user_monthly_tokens=200000,space_monthly_tokens=200000,
 user_storage_bytes=20000000,space_storage_bytes=20000000,turn_reserved_tokens=40000,turn_reserved_bytes=4000000)

@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1',reason='Explicit local authentication and execution authorization required')
def test_local_auth_isolation_two_turns_stop(chat,tmp_path,governance):
    client,factory=chat;cid=create(client);path=tmp_path.resolve()/cid;path.mkdir()
    allow_governed_write(client,cid,governance)
    subprocess.run(['git','init','-q',str(path)],check=True)
    (path/'counter.txt').write_text('0\n')
    peer=tmp_path.resolve()/'peer.txt';peer.write_text('synthetic peer')
    report={'auth_source':'authorized local login in disposable runtime','platform_deployment_verified':False,'identity_boundary':'synthetic API actor and disposable DB','rounds':[]}
    def reserve(key,prompt):
        with factory() as db:
            row=enqueue(db,'alice',cid,key,prompt,LIMITS);token=worker.claim(db,'local-isolated-probe')
        return row,token
    with local_executor([path],executable=shutil.which('codex'),auth_source=Path.home()/'.codex/auth.json') as (server_factory,auth_home):
        # Verify access without reading or printing any credential contents.
        targets={'credential_read_denied':str(auth_home/'worker-0/auth.json'),'peer_read_denied':str(peer),'database_read_denied':str(tmp_path.resolve()/'chat.db')}
        code='''import os,json,socket
from pathlib import Path
checks={}
for key,path in TARGETS.items():
 try:fd=os.open(path,os.O_RDONLY);os.close(fd);checks[key]=False
 except PermissionError:checks[key]=True
p=Path('proof');p.write_text('own');checks['own_write']=p.read_text()=='own';p.unlink()
try:Path('.git/forbidden').write_text('bad');checks['git_readonly']=False
except PermissionError:checks['git_readonly']=True
s=socket.socket();s.settimeout(1)
try:s.connect(('1.1.1.1',443));checks['network_denied']=False
except OSError:checks['network_denied']=True
finally:s.close()
assert all(checks.values()),checks
print(json.dumps(checks))
'''
        native=subprocess.run([shutil.which('codex'),'sandbox','-P','moonbox-write','-C',str(path),'/usr/bin/python3','-c','TARGETS='+repr(targets)+'\n'+code],env={'PATH':'/usr/bin:/bin','HOME':str(auth_home),'CODEX_HOME':str(auth_home/'worker-0')},capture_output=True,text=True,timeout=30)
        assert native.returncode==0,'native permissions failed; raw output withheld'
        report['native_isolation']=json.loads(native.stdout)
        readonly_code="from pathlib import Path\ntry:Path('readonly-forbidden').write_text('bad')\nexcept PermissionError:print('denied')\nelse:raise AssertionError('read-only write succeeded')"
        readonly=subprocess.run([shutil.which('codex'),'sandbox','-P','moonbox-read','-C',str(path),'/usr/bin/python3','-c',readonly_code],env={'PATH':'/usr/bin:/bin','HOME':str(auth_home),'CODEX_HOME':str(auth_home/'worker-0')},capture_output=True,text=True,timeout=30)
        assert readonly.returncode==0 and readonly.stdout.strip()=='denied'
        report['readonly_write_denied']=True
        for value in ('1','2'):
            row,token=reserve('local-'+value,f'Bounded integration test: set counter.txt to exactly {value} followed by newline. Change no other files. Do not commit. Reply only done.')
            state=run_claim(factory,token,path,server_factory,max_seconds=180)
            with factory() as db:
                error=db.scalar(select(turns.c.error_code).where(turns.c.id==row['id']))
                thread=db.scalar(select(conversations.c.thread_id).where(conversations.c.id==cid))
            assert state=='completed',error
            assert (path/'counter.txt').read_text()==value+'\n'
            diff=client.get(f"/api/v1/chat/turns/{row['id']}/diff").json()['data']
            report['rounds'].append({'round':int(value),'state':state,'file_matches':True})
            if value=='1':first_thread=thread
            else:assert thread==first_thread
        assert '-1\n+2\n' in diff['files'][0]['patch']
        assert '-0\n+2\n' in diff['cumulative_files'][0]['patch']
        report['thread_resume_after_process_restart']=True
        row,token=reserve('local-stop','Bounded interruption test: execute /bin/sleep 45 as your first action. Do not modify files. After sleep reply done.')
        result={}
        def execute():result['state']=run_claim(factory,token,path,server_factory,max_seconds=90,stop_seconds=25)
        runner=threading.Thread(target=execute);runner.start()
        try:
            deadline=time.monotonic()+40;executor_turn=None
            while time.monotonic()<deadline:
                with factory() as db:executor_turn=db.scalar(select(turns.c.executor_turn_id).where(turns.c.id==row['id']))
                if executor_turn:break
                time.sleep(.2)
            assert executor_turn,'real turn did not start'
            assert client.post(f"/api/v1/chat/turns/{row['id']}/interrupt").status_code==200
        finally:runner.join(timeout=95)
        assert not runner.is_alive()
        assert result['state']=='stopped',result
        assert (path/'counter.txt').read_text()=='2\n'
        report['interrupt_terminal_confirmed']=True
        with factory() as db:
            assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id==cid)) is None
            accounting=[dict(item) for item in db.execute(select(turns.c.status.label('terminal'),turns.c.error_code,reservations.c.status.label('reservation'),reservations.c.actual_tokens).join(reservations, reservations.c.turn_id==turns.c.id)).mappings()]
            assert len(accounting)==3
            for item in accounting:
                if item['terminal']=='completed':
                    assert item['reservation']=='settled' and item['actual_tokens'] is not None
                elif item['error_code']=='usage_unavailable':
                    assert item['reservation']=='reserved' and item['actual_tokens'] is None
                else:
                    assert item['reservation']=='settled'
            report['accounting']=accounting
            report['reservations_settled']=all(item['reservation']=='settled' for item in accounting)
    assert not auth_home.exists();report['temporary_credentials_removed']=True
    Path('/tmp/moonbox-chat-local-execution.json').write_text(json.dumps(report,indent=2))
