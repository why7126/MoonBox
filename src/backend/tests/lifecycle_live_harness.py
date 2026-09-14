"""一次性 Lifecycle 真实验收服务：独立账号/数据库/治理目录，无模型凭证。"""
import json, os, secrets, subprocess, sys, tempfile, time, shutil
from lifecycle_fixture import populate
from pathlib import Path
from chat_isolated_harness import PROJECT, seed


def main():
    if os.environ.get('LIFECYCLE_LIVE_PROBE') != '1': raise SystemExit('explicit opt-in required')
    root=Path(tempfile.mkdtemp(prefix='moonbox-lifecycle-',dir='/private/tmp')); root.chmod(0o700)
    children=[]
    try:
        source=root/'project';source.mkdir()
        private=root/'private';private.mkdir(mode=0o700)
        password=secrets.token_urlsafe(24)+'9A!'
        binding={'id':'lifecycle-probe','space_id':'space','governance_root':str(source),'source_root':str(source),'workspace_root':str(root/'workspaces')}
        os.environ.update(APP_ENV='isolated-test',APP_SECRET_KEY=secrets.token_urlsafe(32),DATABASE_TYPE='sqlite',DATABASE_URL='sqlite:///'+str(root/'moonbox.db'),SQLITE_DATABASE_URL='sqlite:///'+str(root/'moonbox.db'),ADMIN_INITIAL_PASSWORD=secrets.token_urlsafe(24)+'9A!',MOONBOX_CHAT_REPOSITORIES=json.dumps([{'id':binding['id'],'space_id':'space'}]),MOONBOX_CHAT_REPOSITORY_BINDINGS=json.dumps([binding]),MOONBOX_GOVERNANCE_STATE_ROOT=str(private))
        seed(root,password)
        for kind in ('requirements','bugs'):
            folder=source/'issues'/kind;folder.mkdir(parents=True)
            (folder/'_registry.yaml').write_text('next_id: 1\nentries: []\n')
        populate(source)
        shutil.copytree(PROJECT/'scripts', source/'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        module=source/'src/backend/app/governance';module.mkdir(parents=True)
        shutil.copyfile(PROJECT/'src/backend/app/governance/lifecycle.py',module/'lifecycle.py')
        from sqlalchemy import text
        from app.db.session import get_session_factory
        from app.governance.scope import authorize
        with get_session_factory()() as db:
            db.execute(text("INSERT INTO admin_space_products(id,space_id,product_id,product_name,immutable_binding,created_at,updated_at) VALUES('lifecycle-product','space','lifecycle-probe','Lifecycle 隔离验收',1,'2026-09-12','2026-09-12')"));db.commit()
            scope=authorize(db,'alice','space',binding['id'])
        permit=private/'maintenance.json';permit.write_text(json.dumps({'scope_key':scope.key,'binding_revision':scope.binding_revision,'registered_writers':['governance-controller'],'external_writers_paused':True,'expires_at':time.time()+3500}));permit.chmod(0o600)
        config=root/'browser.json';config.write_text(json.dumps({'password':password,'url':'http://127.0.0.1:18131'}));config.chmod(0o600)
        for args,name in (([__file__,'serve'],'api'),):
            children.append(subprocess.Popen([sys.executable,*args],stdout=(root/(name+'.log')).open('w'),stderr=subprocess.STDOUT))
        print(json.dumps({'root':str(root),'url':'http://127.0.0.1:18131'}),flush=True)
        for line in sys.stdin:
            if line.strip()=='cleanup':break
    finally:
        for child in children:
            child.terminate()
            try:child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        print('isolated services stopped',flush=True)


def serve():
    from app.main import app
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    dist=PROJECT/'src/web/dist'
    @app.get('/requirements',include_in_schema=False)
    @app.get('/',include_in_schema=False)
    def index(): return FileResponse(dist/'index.html')
    app.mount('/assets',StaticFiles(directory=dist/'assets'))
    app.mount('/brand',StaticFiles(directory=dist/'brand'))
    uvicorn.run(app,host='127.0.0.1',port=18131,access_log=False,log_level='error')

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='serve':serve()
    else:main()
