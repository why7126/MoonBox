"""Disposable real API/UI for BUG-0028; no production data or credentials."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time


def main():
    if os.environ.get('OWNER_DISPLAY_LIVE_TEST') != '1':
        raise SystemExit('explicit opt-in required')
    root = Path(tempfile.mkdtemp(prefix='moonbox-owner-')).resolve()
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
        for uid, name in [('user_owner_test', '合成负责人长名称用于省略与完整提示验收'), ('user_owner_peer', '同名验收')]:
            db.execute(text("""INSERT INTO admin_users
                (id,username,nickname,role,status,password_hash,created_at,updated_at)
                VALUES(:id,:id,:name,'前台用户','正常',:password,:now,:now)"""),
                {'id': uid, 'name': name, 'password': hash_password('Owner-test-only-2026!'), 'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_spaces
            (id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at)
            VALUES('space_owner_test','负责人隔离验收','owner-test','user_owner_test','ACTIVE','后台创建',2,5,1,1000,'long_term',:now,:now)"""), {'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at)
            VALUES('owner-member','space_owner_test','user_owner_peer','编辑者',:now,:now)"""), {'now': '2026-10-19'})
        db.execute(text("""INSERT INTO admin_space_products(id,space_id,product_id,product_name,immutable_binding,created_at,updated_at)
            VALUES('owner-product','space_owner_test','owner-test','负责人隔离验收',1,:now,:now)"""), {'now': '2026-10-19'})
        db.commit()
        scope = authorize(db, 'user_owner_test', 'space_owner_test', 'owner-test', write=True)
    permit = private / 'maintenance.json'
    permit.write_text(json.dumps({'scope_key': scope.key, 'binding_revision': scope.binding_revision,
        'registered_writers': ['governance-controller'], 'external_writers_paused': True, 'expires_at': time.time() + 3500}))
    permit.chmod(0o600)
    children = []
    try:
        for args, name in [(['-m', 'app.governance.controller'], 'controller'), ([__file__, 'serve'], 'api')]:
            children.append(subprocess.Popen([sys.executable, *args], stdout=(root / (name + '.log')).open('w'), stderr=subprocess.STDOUT))
        print(json.dumps({'root': str(root), 'url': 'http://127.0.0.1:39029'}), flush=True)
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
    dist = Path(os.environ['OWNER_DISPLAY_WEB_DIST'])
    @app.get('/requirements', include_in_schema=False)
    @app.get('/login', include_in_schema=False)
    @app.get('/', include_in_schema=False)
    def index():
        return FileResponse(dist / 'index.html')
    app.mount('/assets', StaticFiles(directory=dist / 'assets'))
    app.mount('/brand', StaticFiles(directory=dist / 'brand'))
    uvicorn.run(app, host='127.0.0.1', port=39029, access_log=False, log_level='error')


if __name__ == '__main__':
    serve() if len(sys.argv) > 1 and sys.argv[1] == 'serve' else main()
