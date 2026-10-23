"""Disposable real API/UI with synthetic execution states for BUG-0044; no model runs."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time


def main():
    if os.environ.get('GOVERNANCE_EXECUTION_UI_TEST') != '1':
        raise SystemExit('explicit opt-in required')
    root = Path(tempfile.mkdtemp(prefix='moonbox-execution-')).resolve()
    root.chmod(0o700)
    project = root / 'project'
    private = root / 'private'
    private.mkdir(mode=0o700)
    for kind in ('requirements', 'bugs'):
        folder = project / 'issues' / kind
        folder.mkdir(parents=True)
        (folder / '_registry.yaml').write_text('next_id: 1\nentries: []\n')
    binding = {'id': 'owner-test', 'space_id': 'space_owner_test', 'governance_root': str(project)}
    os.environ.update(APP_ENV='isolated-test', DATABASE_TYPE='sqlite',
        DATABASE_URL='sqlite:///' + str(root / 'test.db'), SQLITE_DATABASE_URL='sqlite:///' + str(root / 'test.db'),
        APP_SECRET_KEY=secrets.token_urlsafe(32), ADMIN_INITIAL_PASSWORD=secrets.token_urlsafe(32),
        MOONBOX_GOVERNANCE_STATE_ROOT=str(private),
        MOONBOX_CHAT_REPOSITORIES=json.dumps([{'id': binding['id'], 'space_id': binding['space_id']}]),
        MOONBOX_CHAT_REPOSITORY_BINDINGS=json.dumps([binding]))
    from app.db.session import init_database, get_session_factory
    from app.repositories.admin_auth import hash_password
    from app.governance.scope import authorize
    from sqlalchemy import text
    init_database()
    with get_session_factory()() as db:
        for uid, name in [('user_owner_test', '验收用户'), ('user_owner_peer', '同名验收')]:
            db.execute(text("""INSERT INTO admin_users
                (id,username,nickname,role,status,password_hash,created_at,updated_at)
                VALUES(:id,:id,:name,'前台用户','正常',:password,:now,:now)"""),
                {'id': uid, 'name': name, 'password': hash_password('Owner-test-only-2026!'), 'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_spaces
            (id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at)
            VALUES('space_owner_test','执行状态隔离验收','owner-test','user_owner_test','ACTIVE','后台创建',2,5,1,1000,'long_term',:now,:now)"""), {'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at)
            VALUES('owner-member','space_owner_test','user_owner_peer','编辑者',:now,:now)"""), {'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_space_products(id,space_id,product_id,product_name,immutable_binding,created_at,updated_at)
            VALUES('owner-product','space_owner_test','owner-test','执行状态隔离验收',1,:now,:now)"""), {'now': '2026-10-19'})
        db.commit()
        scope = authorize(db, 'user_owner_test', 'space_owner_test', 'owner-test', write=True)
        from app.chat import service
        from app.chat.schema import relations
        from app.governance import execution_guard as guard
        from sqlalchemy import insert
        import yaml
        entries=[]
        for number,state in enumerate(['running','needs_review','validated'],start=1):
            oid=f'BUG-990{number}-execution-sample';base=f'issues/bugs/review/{oid}'
            folder=project/base;folder.mkdir(parents=True)
            metadata={'bug_id':oid,'title':'隔离执行状态样本 '+state,'status':'approved','severity':'medium'}
            def doc(meta):return '---\n'+yaml.safe_dump(meta,allow_unicode=True)+'---\n# 隔离执行状态验收\n'
            for filename in ['bug.md','trace.md','review.md','capture.md','root-cause.md','workaround.md','acceptance.md']:
                (folder/filename).write_text(doc(metadata))
            entries.append(dict(id=oid,path=base,title=metadata['title'],status='approved',severity='medium'))
            parent=service.create_conversation(db,'user_owner_test','space_owner_test','owner-test',metadata['title'])
            db.execute(insert(relations).values(conversation_id=parent['id'],object_id=oid,role='primary',title=metadata['title']))
            row=guard.acquire(db,scope_key=scope.key,object_id=oid,operation_id='synthetic-'+state,conversation_id=parent['id'],owner_id='user_owner_test',action='sprint-propose',confirmed_stage='approved',baseline_revision='synthetic')
            if state != 'running':
                guard.terminal(db,'synthetic-'+state,'failed' if state=='needs_review' else 'completed')
            if state == 'validated':
                guard.confirm(db,scope_key=scope.key,object_id=oid,operation_id='synthetic-'+state,version=row['version'],result_revision='synthetic',current_revision='synthetic',stage='approved',business_valid=True,sync_valid=True,execution_ended=True)
            db.commit()
        (project/'issues/bugs/_registry.yaml').write_text(yaml.safe_dump({'entries':entries},allow_unicode=True))
    permit = private / 'maintenance.json'
    permit.write_text(json.dumps({'scope_key': scope.key, 'binding_revision': scope.binding_revision,
        'registered_writers': ['governance-controller'], 'external_writers_paused': True, 'expires_at': time.time() + 3500}))
    permit.chmod(0o600)
    children = []
    try:
        for args, name in [(['-m', 'app.governance.controller'], 'controller'), ([__file__, 'serve'], 'api')]:
            children.append(subprocess.Popen([sys.executable, *args], stdout=(root / (name + '.log')).open('w'), stderr=subprocess.STDOUT))
        print(json.dumps({'root': str(root), 'url': 'http://127.0.0.1:39145'}), flush=True)
        for line in sys.stdin:
            if line.strip() == 'cleanup':
                break
    finally:
        for child in children:
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def serve():
    from app.main import app
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    dist = Path(os.environ['GOVERNANCE_EXECUTION_WEB_DIST'])
    @app.get('/chat', include_in_schema=False)
    @app.get('/requirements', include_in_schema=False)
    @app.get('/login', include_in_schema=False)
    @app.get('/', include_in_schema=False)
    def index():
        return FileResponse(dist / 'index.html')
    from fastapi.responses import HTMLResponse
    @app.get('/evidence-1440', include_in_schema=False)
    def evidence_view():
        return HTMLResponse('<!doctype html><title>1440px 隔离产品视口</title><style>body{margin:0}iframe{display:block;width:1440px;height:900px;border:0}</style><iframe title="隔离需求中心" src="/requirements"></iframe><details><summary>查看验收样式采样</summary><pre id="measurements"></pre></details><script>setInterval(()=>{const f=document.querySelector("iframe"),d=f.contentDocument;if(!d)return;const samples=[...d.querySelectorAll("article[data-issue-id]")].map(e=>{const s=f.contentWindow.getComputedStyle(e);return {id:e.dataset.issueId,width:s.width,padding:s.padding,borderWidth:s.borderWidth,borderColor:s.borderColor,minHeight:s.minHeight,status:[...e.querySelectorAll("[role=status]")].map(x=>({text:x.textContent,color:f.contentWindow.getComputedStyle(x).color,lineHeight:f.contentWindow.getComputedStyle(x).lineHeight})),buttons:[...e.querySelectorAll("footer button")].map(x=>({text:x.textContent,disabled:x.disabled,cursor:f.contentWindow.getComputedStyle(x).cursor}))}});document.querySelector("#measurements").textContent=JSON.stringify({viewport:{width:f.contentWindow.innerWidth,height:f.contentWindow.innerHeight},samples},null,2)},1000)</script>')
    app.mount('/assets', StaticFiles(directory=dist / 'assets'))
    app.mount('/brand', StaticFiles(directory=dist / 'brand'))
    uvicorn.run(app, host='127.0.0.1', port=39145, access_log=False, log_level='error')


if __name__ == '__main__':
    serve() if len(sys.argv) > 1 and sys.argv[1] == 'serve' else main()
