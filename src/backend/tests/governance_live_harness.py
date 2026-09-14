"""显式独立 MoonBox 副本验收：真实登录、平台容器 worker 和可信写入进程。"""
import json, os, secrets, shutil, subprocess, sys, tempfile, time
from pathlib import Path
import yaml
from chat_isolated_harness import PROJECT, seed, LIMITS, serve

OID='REQ-9098-governance-live-validation'

def main():
    if os.environ.get('GOVERNANCE_LIVE_PROBE') != '1': raise SystemExit('explicit opt-in required')
    root=Path(tempfile.mkdtemp(prefix='moonbox-governance-live-',dir='/private/tmp'));root.chmod(0o700)
    children=[]
    try:
        source=root/'project'
        subprocess.run(['git','clone','--quiet','--no-hardlinks',str(PROJECT),str(source)],check=True,capture_output=True)
        subprocess.run(['git','-C',str(source),'switch','-c','codex/req0022-local-validation'],check=True,capture_output=True)
        for name in ('issues','iterations','openspec','docs','rules','.agents','scripts'):
            shutil.rmtree(source/name,ignore_errors=True);shutil.copytree(PROJECT/name,source/name)
        shutil.copyfile(PROJECT/'AGENTS.md',source/'AGENTS.md')
        for name in ('workspaces','state','runtime','private','backups'):(root/name).mkdir(mode=0o700)
        password=secrets.token_urlsafe(24)+'9A!'
        LIMITS.update(user_monthly_tokens=3000000,space_monthly_tokens=3000000,turn_reserved_tokens=1000000,turn_reserved_bytes=16000000,user_storage_bytes=128000000,space_storage_bytes=128000000)
        binding={'id':'moonbox-validation','space_id':'space','source_root':str(source),'governance_root':str(source),'workspace_root':str(root/'workspaces')}
        os.environ.update(APP_ENV='isolated-test',APP_SECRET_KEY=secrets.token_urlsafe(32),DATABASE_TYPE='sqlite',DATABASE_URL='sqlite:///'+str(root/'moonbox.db'),SQLITE_DATABASE_URL='sqlite:///'+str(root/'moonbox.db'),ADMIN_INITIAL_PASSWORD=secrets.token_urlsafe(24)+'9A!',
          MOONBOX_CHAT_EXECUTION_MODE='local-codex',MOONBOX_CHAT_STATE_ROOT=str(root/'state'),MOONBOX_CHAT_RUNTIME_ROOT=str(root/'runtime'),MOONBOX_CHAT_AUTH_FILE=str(Path.home()/'.codex/auth.json'),
          MOONBOX_CHAT_LIMITS=json.dumps(LIMITS),MOONBOX_CHAT_RETENTION=json.dumps({'executor_delete_seconds':86400,'backup_expiry_seconds':86400}),MOONBOX_CHAT_BACKUP_ROOT=str(root/'backups'),
          MOONBOX_CHAT_REPOSITORIES=json.dumps([{'id':binding['id'],'space_id':'space'}]),MOONBOX_CHAT_REPOSITORY_BINDINGS=json.dumps([binding]),MOONBOX_GOVERNANCE_STATE_ROOT=str(root/'private'))
        seed(root,password)
        import sqlite3
        with sqlite3.connect(root/'moonbox.db') as db:
            db.execute("INSERT INTO admin_space_products(id,space_id,product_id,product_name,immutable_binding,created_at,updated_at) VALUES('validation-product','space','moonbox-validation','MoonBox 本地验证',1,'2026-09-11','2026-09-11')");db.commit()
        shutil.rmtree(root/'seed');shutil.rmtree(root/'governance')
        folder=source/f'issues/requirements/plan/{OID}';folder.mkdir(parents=True)
        meta={'requirement_id':OID,'status':'captured','iteration':None,'openspec_changes':[],'lifecycle':{'captured':'2026-09-11'},'updated_at':'2026-09-11','created_at':'2026-09-11 08:00:00','lifecycle_stage':'plan','priority':'P2'}
        def front(meta,body):return '---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n\n'+body
        (folder/'trace.md').write_text(front(meta,'# 验证需求追踪\n'))
        (folder/'capture.md').write_text(front({'requirement_id':OID,'status':'captured','title':'本地项目治理连接状态说明','priority':'P2'},'# 采集说明\n\n为 MoonBox 本地验证项目补齐项目连接状态说明：需求中心和 Chat 展示相同项目标识，未连接时解释原因并可刷新。此对象仅用于独立副本验证 req-generate 文档闭环。范围是生成需求文档，不开发产品代码。验收包括项目标识一致、状态说明清楚、动作不自动发送。\n'))
        registry=source/'issues/requirements/_registry.yaml';data=yaml.safe_load(registry.read_text());data['entries'].append({'id':OID,'title':'本地项目治理连接状态说明','status':'captured','priority':'P2','path':f'issues/requirements/plan/{OID}/','lifecycle_stage':'plan','iteration':None});registry.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
        index=source/'issues/requirements/CHANGELOG.md';index.write_text(index.read_text()+f'\n| {OID} | 本地项目治理连接状态说明 | captured | issues/requirements/plan/{OID} |\n')
        from app.chat.backup import LocalBackupStore
        from app.governance.backup import create
        from app.governance.scope import authorize
        from app.db.session import get_session_factory
        LocalBackupStore(root/'backups',initialize=True)
        # Private coordinated offline bundle; no user account/database copied.
        create(get_session_factory(),root/'before-backup')
        with get_session_factory()() as db:scope=authorize(db,'alice','space',binding['id'])
        permit={'scope_key':scope.key,'binding_revision':scope.binding_revision,'registered_writers':['governance-controller'],'external_writers_paused':True,'expires_at':time.time()+3500}
        path=root/'private/maintenance.json';path.write_text(json.dumps(permit));path.chmod(0o600)
        (root/'browser.json').write_text(json.dumps({'password':password,'url':'http://127.0.0.1:18128','object_id':OID}));(root/'browser.json').chmod(0o600)
        # Environment retained privately only for operator recovery in this disposable deployment.
        (root/'environment.json').write_text(json.dumps({k:v for k,v in os.environ.items() if k.startswith(('MOONBOX_','DATABASE','SQLITE','APP_','ADMIN_INITIAL'))}));(root/'environment.json').chmod(0o600)
        for module in ('app.chat.platform_worker','app.governance.controller'):
            children.append(subprocess.Popen([sys.executable,'-m',module],stdout=(root/(module+'.log')).open('w'),stderr=subprocess.STDOUT))
        children.append(subprocess.Popen([sys.executable,__file__,'serve'],stdout=(root/'api.log').open('w'),stderr=subprocess.STDOUT))
        print(json.dumps({'root':str(root),'url':'http://127.0.0.1:18128','object_id':OID}),flush=True)
        for line in sys.stdin:
            if line.strip()=='cleanup':break
            if line.strip()=='status':print(json.dumps({'alive':[p.poll() is None for p in children],'ready':(root/'state/worker-ready.json').exists()}),flush=True)
    finally:
        for p in reversed(children):
            if p.poll() is None:
                p.terminate()
                try:p.wait(timeout=60)
                except subprocess.TimeoutExpired:p.kill();p.wait()
        print(json.dumps({'stopped':True,'private_evidence_retained':str(root)}),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='serve':serve()
    else:main()
