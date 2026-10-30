"""MoonBox product adapter, restricted to the acceptance container's fresh /state DB.

Uses real migrations, password hashing, sessions and space authorization. It never
substitutes API handlers or creates acceptance operation/status rows.
"""
import json
import os
from pathlib import Path
import re
import secrets
import sys
import time
import subprocess
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def configure():
    from sqlalchemy.engine import make_url
    url = make_url(os.environ.get('DATABASE_URL', ''))
    safe_sqlite = url.drivername == 'sqlite' and url.database == '/state/acceptance.db'
    safe_mysql = (url.drivername == 'mysql+pymysql' and url.username == 'candidate'
                  and url.database == 'candidate' and re.fullmatch(r'moonbox-candidate-[a-f0-9-]+-db', url.host or ''))
    if os.environ.get('APP_ENV') != 'test' or not (safe_sqlite or safe_mysql):
        raise RuntimeError('isolated_product_database_required')
    private = Path('/state/product-secret')
    if not private.exists():
        try:
            fd = os.open(private, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as stream:
                stream.write(secrets.token_urlsafe(32))
        except FileExistsError:
            pass
    os.environ.update(APP_SECRET_KEY=private.read_text(), ADMIN_INITIAL_PASSWORD=private.read_text(),
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES='15', ADMIN_SPACE_APPLICATION_DEMO_SEED='false',
        OBJECT_STORAGE_ENDPOINT='127.0.0.1:1', OBJECT_STORAGE_ACCESS_KEY='example',
        OBJECT_STORAGE_SECRET_KEY='example')
    source = Path(__file__).resolve().parents[3]
    binding = {'id': 'acceptance-product', 'space_id': 'acceptance-space', 'governance_root': str(source)}
    os.environ['MOONBOX_CHAT_REPOSITORIES'] = json.dumps([{'id': binding['id'], 'space_id': binding['space_id']}])
    os.environ['MOONBOX_CHAT_REPOSITORY_BINDINGS'] = json.dumps([binding])


def expire_identities():
    """The adapter adds a deadline to temporary accounts; real auth enforces freeze."""
    from sqlalchemy import text
    from app.db.session import get_session_factory
    from app.db.time_values import storage_time
    directory=Path('/state/identity-deadlines')
    if not directory.exists():return
    for path in directory.glob('a*.json'):
        if not re.fullmatch(r'a[a-f0-9]{31}\.json',path.name) or path.is_symlink():raise RuntimeError('invalid_identity_deadline')
        try:deadline=float(path.read_text())
        except FileNotFoundError:continue
        if deadline>time.time():continue
        with get_session_factory().begin() as db:
            now=storage_time(datetime.now(timezone.utc).isoformat())
            db.execute(text('UPDATE admin_sessions SET revoked_at=:now WHERE user_id=:id'),{'now':now,'id':path.stem})
            db.execute(text("UPDATE admin_users SET status='已冻结',status_before_freeze='正常' WHERE id=:id"),{'id':path.stem})
        path.unlink(missing_ok=True)


def main(action):
    configure()
    from sqlalchemy import text
    from app.db.session import init_database, get_session_factory
    from app.repositories.admin_auth import hash_password
    if action == 'migrate':
        init_database()
        return
    now = datetime.now(timezone.utc).isoformat()
    with get_session_factory().begin() as db:
        if action == 'seed':
            db.execute(text("""INSERT INTO admin_users
                (id,username,nickname,role,status,password_hash,created_at,updated_at)
                VALUES('acceptance-owner','acceptance-owner','隔离验收所有者','前台用户','正常',:password,:now,:now)"""),
                {'password': hash_password(secrets.token_urlsafe(32)), 'now': now})
            db.execute(text("""INSERT INTO admin_spaces
                (id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at)
                VALUES('acceptance-space','本机隔离验收','acceptance-product','acceptance-owner','ACTIVE','后台创建',1,10,1,100000,'long_term',:now,:now)"""), {'now': now})
            db.execute(text("""INSERT INTO admin_space_products
                (id,space_id,product_id,product_name,immutable_binding,created_at,updated_at)
                VALUES('acceptance-product','acceptance-space','acceptance-product','MoonBox 隔离验收',1,:now,:now)"""), {'now': now})
            return
        payload = json.load(sys.stdin)
        username = payload.get('username', '')
        if not re.fullmatch(r'a[a-f0-9]{31}', username):
            raise RuntimeError('isolated_identity_required')
        if action == 'issue':
            if payload['expires_at'] <= time.time() or payload['role'] not in {'member', 'reader'}:
                raise RuntimeError('identity_invalid')
            db.execute(text("""INSERT INTO admin_users
                (id,username,nickname,role,status,password_hash,created_at,updated_at)
                VALUES(:id,:id,:name,'前台用户','正常',:password,:now,:now)"""),
                {'id': username, 'name': '隔离验收 ' + payload['role'],
                 'password': hash_password(payload['password']), 'now': now})
            db.execute(text("""INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at)
                VALUES(:id,'acceptance-space',:id,:role,:now,:now)"""),
                {'id': username, 'role': '编辑者' if payload['role'] == 'member' else '查看者', 'now': now})
            directory=Path('/state/identity-deadlines');directory.mkdir(mode=0o700,exist_ok=True)
            with os.fdopen(os.open(directory/(username+'.json'),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600),'w') as stream:
                stream.write(str(payload['expires_at']))
        elif action == 'revoke':
            db.execute(text('UPDATE admin_sessions SET revoked_at=:now WHERE user_id=:id'), {'id': username, 'now': now})
            db.execute(text("UPDATE admin_users SET status='已冻结',status_before_freeze='正常' WHERE id=:id"), {'id': username})
            (Path('/state/identity-deadlines')/(username+'.json')).unlink(missing_ok=True)
        elif action == 'check':
            from app.governance.scope import authorize
            from app.chat.service import ChatError
            scope = authorize(db, username, 'acceptance-space', 'acceptance-product')
            assert scope.readonly == (payload['role'] == 'reader')
            backend=db.get_bind().dialect.name
            assert int(db.scalar(text("SELECT JSON_EXTRACT(:document, '$.n')"),{'document':'{"n":2}'}))==2
            db.execute(text('CREATE TEMPORARY TABLE acceptance_compat_probe (name VARCHAR(16), marker INTEGER)'))
            db.execute(text("INSERT INTO acceptance_compat_probe VALUES ('c',3),('a',1),('b',2)"))
            assert db.scalar(text('SELECT name FROM acceptance_compat_probe ORDER BY name LIMIT 1 OFFSET 1'))=='b'
            nested=db.begin_nested()
            db.execute(text("INSERT INTO acceptance_compat_probe VALUES ('rollback',4)"));nested.rollback()
            assert db.scalar(text("SELECT COUNT(*) FROM acceptance_compat_probe WHERE name='rollback'"))==0
            if backend=='mysql':
                assert db.scalar(text('SELECT @@character_set_database'))=='utf8mb4'
                assert db.scalar(text('SELECT @@collation_database'))=='utf8mb4_0900_ai_ci'
                assert db.scalar(text('SELECT TIMESTAMPDIFF(SECOND,UTC_TIMESTAMP(),NOW())'))==0
                assert str(db.scalar(text('SELECT CAST(:value AS DATETIME)'),{'value':'2026-10-30 02:00:00'}))=='2026-10-30 02:00:00'
            db.execute(text('DROP TABLE acceptance_compat_probe'))
            try:
                authorize(db, username, 'acceptance-space', 'acceptance-product',write=True)
            except ChatError as error:
                assert payload['role']=='reader' and error.status==403
            else:
                assert payload['role']=='member'
            try:
                authorize(db, username, 'another-task-space', 'acceptance-product')
            except ChatError as error:
                assert error.status==403
            else:raise AssertionError('cross_space_access_allowed')
            # Release SQLite's probe transaction before HTTP authentication writes
            # a session through a different process/connection.
            db.commit()
            request = Request('http://127.0.0.1:8000/api/v1/auth/login',
                data=json.dumps({'username': username, 'password': payload['password']}).encode(),
                headers={'Content-Type': 'application/json'})
            with urlopen(request, timeout=10) as response:
                session = json.load(response)['data']
            assert session['user']['id'] == username and session['access_token']
            def authenticated_status(path):
                request=Request('http://127.0.0.1:8000'+path,headers={'Authorization':'Bearer '+session['access_token']})
                try:
                    with urlopen(request,timeout=10) as response:return response.status
                except HTTPError as error:return error.code
            assert authenticated_status('/api/v1/auth/me')==200
            assert authenticated_status('/api/v1/admin/users')==403
            # Controlled expiry in this fresh DB, then a real HTTP rejection.
            from app.repositories.admin_auth import token_hash
            from app.db.time_values import storage_time
            with get_session_factory().begin() as expiry_db:
                expiry_db.execute(text('UPDATE admin_sessions SET expires_at=:expired WHERE token_hash=:hash'),
                                  {'expired':storage_time('2000-01-01T00:00:00Z'),'hash':token_hash(session['access_token'])})
            assert authenticated_status('/api/v1/auth/me')==401
            # A separate two-second credential proves that re-login also expires,
            # not merely the first session. The primary browser identity stays live.
            probe=dict(username='a'+secrets.token_hex(16)[:31],password=secrets.token_urlsafe(32),role=payload['role'],expires_at=time.time()+2)
            subprocess.run([sys.executable,__file__,'issue'],input=json.dumps(probe),text=True,capture_output=True,check=True)
            time.sleep(max(0,probe['expires_at']-time.time())+.1)
            request=Request('http://127.0.0.1:8000/api/v1/auth/login',data=json.dumps({'username':probe['username'],'password':probe['password']}).encode(),headers={'Content-Type':'application/json'})
            try:
                with urlopen(request,timeout=10):pass
            except HTTPError as error:assert error.code==401
            else:raise AssertionError('expired_identity_logged_in')
            print(json.dumps({'role':payload['role'],'database':backend,'json_sort_page_transaction':'passed',
                              'login':200,'admin_access':403,'expired_session':401,'expired_identity':401,'cross_space':'denied'}))
        else:
            raise RuntimeError('unknown_action')


def application():
    configure()
    from app.main import app
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    @app.middleware('http')
    async def enforce_temporary_identity_deadline(request,call_next):
        expire_identities()
        return await call_next(request)
    # Build output is intentionally excluded from Chat source checkpoints.
    # The approved immutable application image owns the matching web bundle.
    dist = Path('/opt/moonbox-product-web')
    for route in ('/', '/chat', '/login', '/requirements'):
        app.add_api_route(route, lambda: FileResponse(dist / 'index.html'), include_in_schema=False)
    app.mount('/assets', StaticFiles(directory=dist / 'assets'))
    app.mount('/brand', StaticFiles(directory=dist / 'brand'))
    return app


if __name__ == '__main__':
    main(sys.argv[1])
else:
    # Imported only by the dedicated ASGI module below, not pytest collection.
    pass
