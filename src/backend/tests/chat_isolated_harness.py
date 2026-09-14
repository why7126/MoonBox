"""显式真实E2E启动器：回环服务、真实登录、受控仓库和最终清理。"""
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import signal
import socket
from contextlib import contextmanager

PROJECT=Path(__file__).resolve().parents[3]
PORT=int(os.environ.get('HOST_PORT_CHAT_TEST','18121'))
if not 18101<=PORT<=18199:raise ValueError('test port must be in 18101-18199')
LIMITS=dict(user_concurrency=1,space_concurrency=1,user_monthly_tokens=400000,space_monthly_tokens=400000,
 user_storage_bytes=40000000,space_storage_bytes=40000000,turn_reserved_tokens=60000,turn_reserved_bytes=4000000)


def serve():
    from app.main import app
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    dist=Path(os.environ.get('MOONBOX_CHAT_TEST_WEB_DIST',str(PROJECT/'src/web/dist')))
    @app.get('/chat',include_in_schema=False)
    @app.get('/',include_in_schema=False)
    def index():return FileResponse(dist/'index.html')
    app.mount('/assets',StaticFiles(directory=dist/'assets'),name='test-assets')
    app.mount('/brand',StaticFiles(directory=dist/'brand'),name='test-brand')
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=PORT,access_log=False,log_level='error')


def seed(root,password):
    from app.db.session import init_database,get_session_factory
    from app.repositories.admin_auth import hash_password
    from app.chat.service import now
    from sqlalchemy import text
    init_database()
    with get_session_factory()() as db:
        for uid in ('alice','bob'):
            db.execute(text('''INSERT INTO admin_users(id,username,nickname,role,status,password_hash,created_at,updated_at)
                VALUES(:id,:id,:name,'前台用户','正常',:hash,:now,:now)'''),dict(id=uid,name='隔离测试'+uid,hash=hash_password(password),now=now()))
        db.execute(text('''INSERT INTO admin_spaces(id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at)
            VALUES('space','Chat隔离测试','chat-isolated','alice','ACTIVE','后台创建',2,2,1,400000,'long_term',:now,:now)'''),{'now':now()})
        db.execute(text("INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at) VALUES('bob-member','space','bob','查看者',:now,:now)"),{'now':now()})
        db.commit()
    governance=root/'governance';oid='REQ-9001-synthetic';relative=f'issues/requirements/review/{oid}'
    folder=governance/relative;folder.mkdir(parents=True)
    (folder/'requirement.md').write_text('受控测试：仅修改counter.txt。')
    entry=dict(id=oid,title='受控计数器测试',path=relative,status='in_sprint',related_change='synthetic-change',iteration='sprint-999')
    (governance/'issues/requirements/_registry.yaml').write_text(json.dumps({'entries':[entry]}))
    folder=governance/'openspec/changes/synthetic-change';folder.mkdir(parents=True)
    (folder/'trace.md').write_text(f'---\nstatus: in_progress\nrequirement: {oid}\nsprint: sprint-999\n---\n')
    folder=governance/'iterations/change/sprint-999';folder.mkdir(parents=True)
    (folder/'sprint.yaml').write_text(json.dumps({'changes':['synthetic-change'],'requirements':[oid]}))
    repo=root/'seed';repo.mkdir();(repo/'counter.txt').write_text('0\n')
    for args in (['init','-q',str(repo)],['-C',str(repo),'add','counter.txt'],['-C',str(repo),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','controlled seed']):
        subprocess.run(['git',*args],check=True,capture_output=True,env={'PATH':'/usr/bin:/bin','HOME':'/nonexistent','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null'})


@contextmanager
def control_channel():
    value=os.environ.get('MOONBOX_CHAT_CONTROL_SOCKET')
    if not value:
        yield None;return
    path=Path(value)
    from app.chat.deployment import private_root
    private_root(path.parent)
    if path.name!='control.sock' or path.exists():raise RuntimeError('control endpoint unavailable')
    listener=socket.socket(socket.AF_UNIX)
    try:
        listener.bind(str(path));path.chmod(0o600);listener.listen(5);listener.settimeout(.5)
        yield listener
    finally:
        listener.close();path.unlink(missing_ok=True)


def commands(listener, deadline):
    if listener is None:
        for line in sys.stdin:yield line.strip(),None
        return
    while time.time()<deadline:
        try:connection,_=listener.accept()
        except socket.timeout:continue
        connection.settimeout(1)
        try:
            action=connection.recv(32).decode().strip()
            if action not in ('status','cleanup','restart'):continue
            yield action,connection
        except (OSError,UnicodeError):pass
        finally:connection.close()
    yield 'cleanup',None


def main():
    if os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1':raise SystemExit('explicit opt-in required')
    def terminate(*_):raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM,terminate)
    with socket.socket() as check:check.bind(('127.0.0.1',PORT))
    with control_channel() as listener, tempfile.TemporaryDirectory(prefix='moonbox-chat-e2e-',dir='/private/tmp') as directory:
        root=Path(directory);password=secrets.token_urlsafe(24)+'9A!';worker=None;api=None
        try:
            for folder in ('runtime','workspaces'):(root/folder).mkdir(mode=0o700)
            with (Path.home()/'.codex/auth.json').open('rb') as reader,(root/'auth.json').open('xb') as writer:
                os.chmod(root/'auth.json',0o600);shutil.copyfileobj(reader,writer)
            executor=os.environ.get('MOONBOX_CHAT_TEST_EXECUTOR','native')
            if executor not in ('native','container'):raise ValueError('invalid test executor')
            config=dict(root=str(root),actor='alice',space='space',repository='repo',expires_at=time.time()+3600,executable=shutil.which('codex'),executor=executor)
            (root/'config.json').write_text(json.dumps(config));(root/'config.json').chmod(0o600)
            (root/'browser.json').write_text(json.dumps({'password':password,'url':f'http://127.0.0.1:{PORT}'}));(root/'browser.json').chmod(0o600)
            os.environ.update(APP_ENV='isolated-test',APP_SECRET_KEY=secrets.token_urlsafe(32),DATABASE_TYPE='sqlite',DATABASE_URL='sqlite:///'+str(root/'chat.db'),
                ADMIN_INITIAL_PASSWORD=secrets.token_urlsafe(24)+'9A!',MOONBOX_CHAT_LOCAL_CONFIG=str(root/'config.json'),
                MOONBOX_CHAT_RETENTION=json.dumps({'executor_delete_seconds':60,'backup_expiry_seconds':120}),
                MOONBOX_CHAT_LIMITS=json.dumps(LIMITS),MOONBOX_CHAT_REPOSITORIES=json.dumps([{'id':'repo','space_id':'space'}]),
                MOONBOX_CHAT_REPOSITORY_BINDINGS=json.dumps([{'id':'repo','space_id':'space','governance_root':str(root/'governance'),'workspace_root':str(root/'workspaces')}]))
            seed(root,password)
            from app.chat.backup import LocalBackupStore
            backups=root/'backups';backups.mkdir(mode=0o700)
            LocalBackupStore(backups,initialize=True).create(root/'chat.db')
            os.environ['MOONBOX_CHAT_BACKUP_ROOT']=str(backups)
            def start_worker():return subprocess.Popen([sys.executable,'-m','app.chat.local_worker'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            worker=start_worker()
            api=subprocess.Popen([sys.executable,__file__,'serve'],stdout=subprocess.DEVNULL,stderr=(root/'api.log').open('w'))
            deadline=time.time()+25
            while time.time()<deadline:
                try:
                    urllib.request.urlopen(f'http://127.0.0.1:{PORT}/health',timeout=1)
                    if (root/'worker-ready.json').exists():break
                except Exception:time.sleep(.25)
            else:raise RuntimeError('test service not ready')
            print(json.dumps({'ready':True,'root':str(root),'port':PORT}),flush=True)
            for action,connection in commands(listener,config['expires_at']):
                response={}
                if action=='restart':
                    worker.terminate();worker.wait(timeout=65);worker=start_worker()
                    time.sleep(1);response={'restarted':worker.poll() is None}
                elif action=='status':
                    from app.db.session import get_session_factory
                    from app.chat.accounting import pending
                    from app.chat.schema import turns,reservations,conversations
                    from sqlalchemy import select
                    with get_session_factory()() as db:
                        rows=[dict(r) for r in db.execute(select(turns.c.status,turns.c.error_code,reservations.c.status.label('reservation'),reservations.c.actual_tokens).join(reservations,reservations.c.turn_id==turns.c.id)).mappings()]
                        response={'running':True,'ready':worker.poll() is None and api.poll() is None,'root':str(root),
                            'url':f'http://127.0.0.1:{PORT}/chat','login_file':str(root/'browser.json'),'expires_at':config['expires_at'],
                            'worker_alive':worker.poll() is None,'turns':rows,'pending_count':len(pending(db))}
                elif action=='cleanup':response={'stopping':True}
                if connection:
                    try:connection.sendall(json.dumps(response).encode())
                    except OSError:pass
                else:print(json.dumps(response),flush=True)
                if action=='cleanup':break
        finally:
            for process in (worker,api):
                if process and process.poll() is None:
                    process.terminate()
                    try:process.wait(timeout=65)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
    print(json.dumps({'cleaned':not root.exists(),'processes_stopped':True}),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='serve':serve()
    else:main()
