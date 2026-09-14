"""显式运行的可丢弃镜像部署探针；不访问既有服务数据或模型凭证。"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
import urllib.request


def docker(*args):
    return subprocess.check_output(['docker', *args], text=True).strip()


def main():
    image = os.environ.get('CHAT_TEST_IMAGE', 'moonbox-backend:chat-verification')
    port = int(os.environ.get('HOST_PORT_CHAT_DEPLOY_TEST', '18127'))
    if not 18101 <= port <= 18199:
        raise ValueError('test port outside project range')
    name = 'moonbox-chat-deploy-' + secrets.token_hex(4)
    volume = name + '-data'
    common = ['--read-only', '--user', '10001:10001', '--cap-drop', 'ALL',
              '--security-opt', 'no-new-privileges', '--tmpfs', '/tmp:rw,nosuid,size=64m',
              '-v', volume + ':/app/data']
    with tempfile.TemporaryDirectory(prefix='moonbox-deploy-', dir='/private/tmp') as folder:
        envfile = Path(folder) / 'test.env'
        envfile.write_text('APP_ENV=local\nSQLITE_DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db\nADMIN_INITIAL_PASSWORD=' + secrets.token_hex(24) + '\n')
        envfile.chmod(0o600)
        common += ['--env-file', str(envfile)]
        try:
            docker('volume', 'create', volume)
            docker('run', '--rm', '--network', 'none', '-v', volume + ':/app/data', image,
                   'python', '-c', 'import os; os.chown("/app/data",10001,10001)')
            docker('run', '-d', '--name', name, *common, '-p', f'127.0.0.1:{port}:8000', image)

            def healthy():
                for _ in range(60):
                    try:
                        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=1) as response:
                            if response.status == 200:
                                return
                    except (OSError, TimeoutError):
                        pass
                    time.sleep(1)
                raise RuntimeError('isolated API readiness timeout')

            healthy()
            # Synthetic rows belong only to this disposable deployment volume.
            docker('exec', name, 'python', '-c', '''
from sqlalchemy import text, insert
from app.db.session import get_session_factory
from app.chat import service
from app.chat.schema import conversations, turns
with get_session_factory()() as db:
    actor=db.scalar(text('SELECT id FROM admin_users LIMIT 1'))
    assert actor
    now=service.now()
    db.execute(text("INSERT INTO admin_spaces(id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at) VALUES('probe-space','部署测试','deploy-probe',:actor,'ACTIVE','后台创建',1,1,1,10000,'long_term',:now,:now)"),{'actor':actor,'now':now})
    db.execute(insert(conversations).values(id='probe-conversation',created_at=now,updated_at=now,owner_id=actor,space_id='probe-space',repository_id='probe-repo',title='部署测试',active_turn_id='probe-turn'))
    db.execute(insert(turns).values(id='probe-turn',created_at=now,updated_at=now,conversation_id='probe-conversation',client_request_id='probe-request',status='running',prompt='synthetic deployment probe',worker_id='expired-worker',heartbeat_at='2000-01-01T00:00:00+00:00'))
    db.commit()
''')
            docker('restart', name)
            healthy()
            # Run twice: unknown is retained and never reclaimed on restart.
            for _ in range(2):
                docker('run', '--rm', '--network', 'none', *common, image,
                       'python', '-m', 'app.chat.worker', '--once')
            docker('exec', name, 'python', '-c', '''
from sqlalchemy import select
from app.db.session import get_session_factory
from app.chat.schema import conversations,turns
from app.chat.worker import claim
with get_session_factory()() as db:
    assert db.scalar(select(turns.c.status).where(turns.c.id=='probe-turn'))=='unknown'
    assert db.scalar(select(conversations.c.active_turn_id).where(conversations.c.id=='probe-conversation'))=='probe-turn'
    assert claim(db,'new-worker') is None
''')
            state = json.loads(docker('inspect', name))[0]
            assert state['HostConfig']['ReadonlyRootfs']
            assert state['Config']['User'] == '10001:10001'
            assert all(m['Destination'] == '/app/data' for m in state['Mounts'])
            report = dict(image_id=state['Image'], health=True, restart_persistence=True,
                          stale_unknown=True, lock_retained=True, no_reclaim=True,
                          nonroot=True, readonly_root=True, recovery_network='none',
                          model_credentials_mounted=False, real_model_in_container=False)
        finally:
            subprocess.run(['docker', 'rm', '-f', name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['docker', 'volume', 'rm', volume], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        report['temporary_resources_removed'] = True
        Path('/tmp/moonbox-chat-deployment.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report))


if __name__ == '__main__':
    main()
