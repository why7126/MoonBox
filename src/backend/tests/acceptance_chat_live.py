"""Local real Chat/model + real MoonBox acceptance; fresh identities and database.

Only transport scheduling/temporary-resource labels are supplied by this harness;
all admission, source capture, tool results, continuation and archive use product code.
"""
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import threading


def worker():
    from app.chat.container_server import ContainerAppServer, persistent_container_server
    root = Path(os.environ['MOONBOX_CHAT_TEST_ROOT'])
    labels = ['--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+os.environ['MOONBOX_TEMP_RUN'],
              '--label','moonbox.temp.expires='+os.environ['MOONBOX_TEMP_EXPIRES']]
    original_labels=ContainerAppServer.recovery_labels
    ContainerAppServer.recovery_labels = lambda self: original_labels(self)+labels
    from app.db.session import get_session_factory
    from app.chat import worker as chat_worker
    from app.chat.execution import run_claim
    from app.chat.schema import conversations
    from app.moonbox_core.sessions import execution_workspace
    from app.verification import acceptance_worker, acceptance_delivery, acceptance_archive
    from sqlalchemy import select
    factory = get_session_factory()
    # Optional observation barrier AFTER real transitions; never writes product
    # states or results. Heartbeats continue while the browser captures evidence.
    from app.verification.acceptance_state import AcceptanceState
    from app.verification.acceptance_runtime import DockerRuntime
    def observe(stage):
        if not (root/'observe-stages').exists():return
        marker=root/('observing-'+stage)
        marker.touch()
        deadline=time.monotonic()+90
        while marker.exists() and time.monotonic()<deadline and not (root/'stop').exists():time.sleep(.2)
        marker.unlink(missing_ok=True)
    original_prepare=DockerRuntime.prepare
    def prepare(runtime,token):
        observe('preparing')
        return original_prepare(runtime,token)
    DockerRuntime.prepare=prepare
    original_advance=AcceptanceState.advance
    def advance(state,token,status):
        result=original_advance(state,token,status)
        if status in {'ready','running'}:observe(status)
        return result
    AcceptanceState.advance=advance
    from app.chat.recovery_worker import RecoverySlot
    from app.chat.settings import recovery_policy
    def current_workspace(cid):
        with factory() as db:
            parent=db.execute(select(conversations).where(conversations.c.id==cid)).mappings().one()
            return None,execution_workspace(db,parent)[1]
    server=lambda path:persistent_container_server(path,root/'runtime',root/'auth.json')
    recovery=RecoverySlot(factory,current_workspace,server,recovery_policy(),docker=True)
    chat_job = acceptance_job = None
    deadline = time.time()+1800
    while time.time() < deadline and not (root/'stop').exists():
        stage=root/'worker-ready.tmp'
        stage.write_text(json.dumps({'time':time.time()}));stage.replace(root/'worker-ready.json')
        if chat_job is None or not chat_job.is_alive():
            if recovery.job is None or not recovery.job.is_alive():
                from app.moonbox_core.completion import reconcile as collect_terminal
                collect_terminal(factory)
                from app.chat.accounting import pending,reconcile_usage
                with factory() as db:
                    for item in pending(db):reconcile_usage(db,item['id'])
            with factory() as db:
                token=chat_worker.claim(db,'isolated-product-worker')
                if token:
                    parent=db.execute(select(conversations).where(conversations.c.id==token['conversation_id'])).mappings().one()
                    workspace=execution_workspace(db,parent)[1]
            if token:
                def execute(token=token,workspace=workspace):
                    run_claim(factory,token,workspace,
                        lambda path:persistent_container_server(path,root/'runtime',root/'auth.json'),max_seconds=900)
                chat_job=threading.Thread(target=execute);chat_job.start()
        if acceptance_job is None or not acceptance_job.is_alive():
            oid=acceptance_worker.next_queued(factory)
            if oid:
                acceptance_job=threading.Thread(target=acceptance_worker.run_one,args=(factory,oid,'isolated-acceptance-worker'))
                acceptance_job.start()
            else:
                pause=root/'pause-reconcile'
                if not pause.exists() or time.time()-pause.stat().st_mtime>90:
                    acceptance_worker.reconcile(factory)
                acceptance_archive.tick(factory)
                acceptance_delivery.tick(factory)
        recovery.tick()
        time.sleep(.5)
    for job in (chat_job,acceptance_job):
        if job:job.join(timeout=30)
    recovery.close()
    (root/'worker-ready.json').unlink(missing_ok=True)


def main():
    if os.environ.get('MOONBOX_PRODUCT_ACCEPTANCE_LIVE')!='1':raise SystemExit('explicit opt-in required')
    product=Path(os.environ['MOONBOX_PRODUCT_PREPARED'])
    space=os.environ.get('MOONBOX_PRODUCT_SPACE','space')
    if space not in {'space','space-2'}:raise ValueError('isolated_space_required')
    keep={'MOONBOX_TEMP_RUN','MOONBOX_TEMP_EXPIRES','MOONBOX_ACCEPTANCE_SUBNET','MOONBOX_PRODUCT_ACCEPTANCE_LIVE','MOONBOX_PRODUCT_PREPARED'}
    for name in list(os.environ):
        if name.startswith(('MOONBOX_','DATABASE_','MYSQL_','SQLITE_','OBJECT_STORAGE_','ADMIN_','APP_')) and name not in keep:
            del os.environ[name]
    template=json.loads((product/'template.json').read_text())
    root=Path(tempfile.mkdtemp(prefix='moonbox-chat-e2e-',dir='/private/tmp'));root.chmod(0o700)
    source=root/'source';shutil.copytree(product/'source',source,ignore=shutil.ignore_patterns('.git'))
    for name in ('runtime','workspaces','private','environments'):(root/name).mkdir(mode=0o700)
    oid='REQ-9001-local-moonbox-acceptance';change='local-moonbox-acceptance';sprint='sprint-999'
    issue=source/'issues/requirements/review'/oid;issue.mkdir(parents=True)
    metadata={'requirement_id':oid,'status':'in_sprint','iteration':sprint,'openspec_changes':[{'change_id':change,'status':'in_progress'}]}
    def front(meta,body):return '---\n'+json.dumps(meta,ensure_ascii=False)+'\n---\n'+body
    for name in ('requirement.md','trace.md','acceptance.md'):(issue/name).write_text(front(metadata,'# 本机真实 MoonBox 隔离验收\n仅验证本机独立数据和临时账号。\n'))
    entry=dict(id=oid,title='本机真实 MoonBox 隔离验收',path=issue.relative_to(source).as_posix(),status='in_sprint',related_change=change,iteration=sprint)
    (source/'issues/requirements/_registry.yaml').write_text(json.dumps({'entries':[entry]}))
    (source/'issues/bugs').mkdir(parents=True);(source/'issues/bugs/_registry.yaml').write_text('entries: []\n')
    change_root=source/'openspec/changes'/change;change_root.mkdir(parents=True)
    (change_root/'trace.md').write_text(front({'status':'in_progress','requirement_id':oid,'sprint':sprint},'# 本机验收\n'))
    (change_root/'proposal.md').write_text('# 本机真实 MoonBox 验收\n')
    (change_root/'acceptance-plan.json').write_text(json.dumps({'change_id':change,'checks':[{'id':ac,'inputs':['src/backend/pyproject.toml','src/backend/tests/acceptance_product_adapter.py']} for ac in template['checks']]}))
    sprint_root=source/'iterations/change'/sprint;sprint_root.mkdir(parents=True)
    (sprint_root/'sprint.yaml').write_text(json.dumps({'sprint_id':sprint,'status':'active','changes':[change],'requirements':[oid],'bugs':[]}))
    (source/'AGENTS.md').write_text('This is an isolated MoonBox acceptance copy. Do not read credentials or contact production services. Use moonbox_acceptance when requested; wait for its real result. Do not modify source unless explicitly requested.\n')
    subprocess.run(['git','init','-q',str(source)],check=True)
    subprocess.run(['git','-C',str(source),'add','.'],check=True)
    subprocess.run(['git','-C',str(source),'-c','user.name=Local Acceptance','-c','user.email=acceptance@example.invalid','commit','-qm','Isolated product acceptance'],check=True)
    auth=Path.home()/'.codex/auth.json'
    if auth.is_symlink() or auth.stat().st_uid!=os.getuid():raise RuntimeError('invalid_auth_source')
    template_path=root/'template.json';template_path.write_text(json.dumps(template));template_path.chmod(0o600)
    candidate=root/'candidate-template.json';candidate.write_text(json.dumps(template['base']));candidate.chmod(0o600)
    password=secrets.token_urlsafe(24)+'9A!'
    from chat_isolated_harness import LIMITS,seed
    limits={**LIMITS,'user_monthly_tokens':2000000,'space_monthly_tokens':2000000,'turn_reserved_tokens':150000,
        'user_storage_bytes':512000000,'space_storage_bytes':512000000,'turn_reserved_bytes':32000000}
    binding=dict(id='repo',space_id=space,source_root=str(source),governance_root=str(source),workspace_root=str(root/'workspaces'),workspace_mode='copy')
    os.environ.update(APP_ENV='isolated-test',CHAT_LIVE_ISOLATED_PROBE='1',APP_SECRET_KEY=secrets.token_urlsafe(32),
        DATABASE_TYPE='sqlite',DATABASE_URL='sqlite:///'+str(root/'chat.db'),SQLITE_DATABASE_URL='sqlite:///'+str(root/'chat.db'),
        ADMIN_INITIAL_PASSWORD=secrets.token_urlsafe(32),ADMIN_SPACE_APPLICATION_DEMO_SEED='false',OBJECT_STORAGE_ENDPOINT='127.0.0.1:1',
        MOONBOX_CHAT_LIMITS=json.dumps(limits),MOONBOX_CHAT_LOCAL_CONFIG=str(root/'config.json'),
        MOONBOX_CHAT_REPOSITORIES=json.dumps([dict(id='repo',space_id=space)]),MOONBOX_CHAT_REPOSITORY_BINDINGS=json.dumps([binding]),
        MOONBOX_GOVERNANCE_STATE_ROOT=str(root/'private'),MOONBOX_ACCEPTANCE_TEMPLATE=str(template_path),MOONBOX_ACCEPTANCE_ROOT=str(root/'environments'),
        MOONBOX_CANDIDATE_TEMPLATE=str(candidate),MOONBOX_CANDIDATE_ROOT=str(root/'candidates'),MOONBOX_CHAT_TEST_ROOT=str(root),HOST_PORT_CHAT_TEST='39048')
    os.environ.pop('MOONBOX_CHAT_EXECUTION_MODE',None)
    (root/'config.json').write_text(json.dumps(dict(root=str(root),actor='alice',space=space,repository='repo',expires_at=time.time()+1800,executor='container')))
    (root/'config.json').chmod(0o600)
    seed(root,password)
    from app.db.session import get_session_factory
    from app.moonbox_core import service as workspaces
    from app.chat import relations,service
    from sqlalchemy import text
    with get_session_factory()() as db:
        if space!='space':
            db.execute(text("""INSERT INTO admin_spaces(id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at)
                SELECT :space,name,:space,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at FROM admin_spaces WHERE id='space'"""),{'space':space})
            db.execute(text("""INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at)
                SELECT 'bob-member-2',:space,user_id,role,created_at,updated_at FROM admin_space_members WHERE id='bob-member'"""),{'space':space})
        db.execute(text("INSERT INTO admin_space_products(id,space_id,product_id,product_name,immutable_binding,created_at,updated_at) VALUES('product',:space,'repo','本机隔离 MoonBox',1,'2026-10-30','2026-10-30')"),{'space':space});db.commit()
        ws=workspaces.create_development(db,'alice',space,'repo',change)
        chat=workspaces.new_session(db,'alice',space,'repo',ws['id'],'local-acceptance-chat')
        relations.set_relations(db,'alice',chat['id'],oid,[])
    (root/'browser.json').write_text(json.dumps({'username':'alice','password':password,'url':'http://127.0.0.1:39048/chat','conversation_id':chat['id'],'space_id':space}));(root/'browser.json').chmod(0o600)
    children=[]
    try:
        shutil.copyfile(auth,root/'auth.json');(root/'auth.json').chmod(0o600)
        for mode in ('worker','serve'):
            children.append(subprocess.Popen([sys.executable,__file__,mode],stdout=(root/(mode+'.log')).open('w'),stderr=subprocess.STDOUT))
        deadline=time.time()+30
        while not (root/'worker-ready.json').exists():
            if time.time()>deadline:raise RuntimeError('worker_not_ready')
            time.sleep(.2)
        with get_session_factory()() as db:
            turn=service.request_turn(db,'alice',chat['id'],'local-acceptance-turn',
                '这是本机隔离 MoonBox 的产品验收。立即调用 moonbox_acceptance 工具一次，不要运行 shell，不要修改任何文件。等待真实工具结果后，用中文简述检查结果和资源回收结果，然后结束。')
        (root/'ids.json').write_text(json.dumps(dict(conversation_id=chat['id'],turn_id=turn['id'],workspace_id=ws['id'])))
        print(json.dumps({'root':str(root),'url':'http://127.0.0.1:39048/chat?conversation_id='+chat['id'],'turn':turn['id']}),flush=True)
        for line in sys.stdin:
            if line.strip()=='cleanup':break
            if line.strip()=='pause':
                children[0].terminate();children[0].wait(timeout=30)
                print(json.dumps({'worker_paused':True}),flush=True)
            if line.strip()=='restart':
                children[0].terminate();children[0].wait(timeout=30)
                children[0]=subprocess.Popen([sys.executable,__file__,'worker'],stdout=(root/'worker-restart.log').open('w'),stderr=subprocess.STDOUT)
                print(json.dumps({'worker_restarted':True}),flush=True)
    finally:
        (root/'stop').touch()
        for child in reversed(children):
            child.terminate()
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        (root/'auth.json').unlink(missing_ok=True)


if __name__=='__main__':
    mode=sys.argv[1] if len(sys.argv)>1 else 'main'
    if mode=='worker':worker()
    elif mode=='serve':
        from app.main import app
        from fastapi.responses import FileResponse
        project=Path(__file__).resolve().parents[3]
        for route in ('/login','/requirements'):
            app.add_api_route(route,lambda:FileResponse(project/'src/web/dist/index.html'),include_in_schema=False)
        from chat_isolated_harness import serve
        serve()
    else:main()
