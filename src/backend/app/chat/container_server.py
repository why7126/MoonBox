"""受信任worker的独立容器适配；浏览器不可提供镜像、挂载或Docker命令。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

from app.chat.app_server import AppServer, ExecutorError
from app.chat.workspace import trusted_directory


def write_profiles(runtime):
    runtime = trusted_directory(runtime)
    config = 'model_reasoning_effort="low"\ncli_auth_credentials_store="file"\nweb_search="disabled"\n[features]\napps=false\nmulti_agent=false\n[analytics]\nenabled=false\n'
    for mode in ('read', 'write'):
        config += f'\n[permissions.moonbox-{mode}.filesystem]\n'
        for path, access in {'/':'read','/runtime':'deny','/proc':'deny','/work':mode,'/work/.git':'read'}.items():
            config += json.dumps(path) + '=' + json.dumps(access) + '\n'
        config += f'\n[permissions.moonbox-{mode}.network]\nenabled=false\n'
    (runtime / 'config.toml').write_text(config)
    (runtime / 'config.toml').chmod(0o600)


class ContainerAppServer(AppServer):
    IMAGE = 'moonbox-chat-executor:0.153.4-test'

    def __init__(self, workspace, runtime, *, write=True, timeout=30):
        self.docker = shutil.which('docker')
        if not self.docker:raise ExecutorError('container_runtime_unavailable')
        if os.getuid()==0:raise ExecutorError('nonroot_controller_required')
        workspace=trusted_directory(workspace);runtime=trusted_directory(runtime)
        if runtime.stat().st_mode & 0o077 or (runtime/'auth.json').is_symlink():
            raise ExecutorError('container_credential_directory_invalid')
        if workspace == runtime or workspace in runtime.parents or runtime in workspace.parents:
            raise ExecutorError('container_mount_overlap')
        trusted_directory(workspace / '.git')
        self.container_name = 'moonbox-chat-session-' + uuid.uuid4().hex
        self.mounts = ['--mount', f'type=bind,src={workspace},dst=/work',
                       '--mount', f'type=bind,src={workspace / ".git"},dst=/work/.git,readonly',
                       '--mount', f'type=bind,src={runtime},dst=/runtime']
        # A test-owned runtime is prepared by the controller; never load personal config.
        super().__init__(self.docker, workspace, runtime, home=runtime, write=write,
                         timeout=timeout, permission_profile='moonbox-write' if write else 'moonbox-read', effort='low')

    def options(self):
        return ['--read-only','--log-driver','none','--user',f'{os.getuid()}:{os.getgid()}','--cap-drop','ALL',
                '--security-opt','no-new-privileges:true',
                '--security-opt','seccomp='+str(Path(__file__).parents[2]/'container/seccomp-codex.json'),'--pids-limit','128',
                '--memory','1g','--cpus','1','--tmpfs','/tmp:rw,nosuid,size=64m',
                '--workdir','/work','--env','HOME=/runtime','--env','CODEX_HOME=/runtime', *self.mounts]

    def version_command(self, executable):
        return [self.docker,'run','--rm','--network','none','--read-only',self.IMAGE,'codex','--version']

    def launch_command(self, executable):
        return [self.docker,'run','--rm','--init','--interactive','--name',self.container_name,
                '--label','moonbox.chat.platform=true' if os.environ.get('MOONBOX_CHAT_EXECUTION_MODE')=='local-codex' else 'moonbox.chat.test=true',*self.options(), self.IMAGE,
                'codex','app-server','--stdio','-c','shell_environment_policy.inherit="none"']

    def rpc(self, method, params):
        if 'cwd' in params:
            if params['cwd'] != str(self.workspace):raise ExecutorError('container_workspace_mismatch')
            params={**params,'cwd':'/work'}
        return super().rpc(method, params)

    def _verify_thread(self, thread, expected):
        if thread.get('cwd') != '/work':raise ExecutorError('executor_workspace_mismatch')
        super()._verify_thread({**thread,'cwd':str(self.workspace)},expected)

    def close(self):
        try:super().close()
        finally:
            subprocess.run([self.docker,'rm','--force',self.container_name],capture_output=True,timeout=20)


SANDBOX_CHECK = """import json,os,socket,tempfile,uuid
from pathlib import Path
checks={}
try:fd=os.open('/runtime/auth.json',os.O_RDONLY);os.close(fd);checks['credential_denied']=False
except OSError:checks['credential_denied']=True
checks['no_peer_mount']=not Path('/peer').exists()
checks['no_database_mount']=not Path('/app/data/sqlite/moonbox.db').exists()
checks['no_docker_socket']=not Path('/var/run/docker.sock').exists()
try:fd=os.open('/proc/1/environ',os.O_RDONLY);os.close(fd);checks['process_environment_denied']=False
except OSError:checks['process_environment_denied']=True
probe=Path('.git')/('.moonbox-preflight-'+uuid.uuid4().hex)
try:
 with probe.open('x') as file:file.write('bad')
 probe.unlink();checks['git_readonly']=False
except OSError:checks['git_readonly']=True
with tempfile.TemporaryFile(dir='.') as file:file.write(b'own')
checks['own_write']=True
s=None
try:s=socket.socket();s.settimeout(1);s.connect(('1.1.1.1',443));checks['tool_network_denied']=False
except OSError:checks['tool_network_denied']=True
finally:
 if s is not None:s.close()
assert all(checks.values()),checks
print(json.dumps(checks))
"""

READONLY_CHECK = """import tempfile,errno
try:
 with tempfile.TemporaryFile(dir='.') as file:file.write(b'forbidden')
except OSError as error:
 if error.errno not in (errno.EPERM,errno.EACCES,errno.EROFS):raise
 print('readonly-denied')
else:raise RuntimeError('readonly workspace writable')
"""


def persistent_container_server(workspace, runtime_root, auth_source):
    """隔离worker入口：每个工作区独立运行目录；先验证沙箱，再复制认证。"""
    import hashlib
    workspace=trusted_directory(workspace);runtime_root=trusted_directory(runtime_root)
    runtime=runtime_root/hashlib.sha256(str(workspace).encode()).hexdigest()
    runtime.mkdir(mode=0o700,exist_ok=True);trusted_directory(runtime)
    write_profiles(runtime)
    auth=runtime/'auth.json';synthetic=not auth.exists()
    if auth.is_symlink():raise ExecutorError('container_auth_path_invalid')
    if synthetic:
        with auth.open('x') as file:
            auth.chmod(0o600);file.write('{"OPENAI_API_KEY":"synthetic-invalid-key"}')
    try:
        with ContainerAppServer(workspace,runtime) as server:
            result=subprocess.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-write','-C','/work','/usr/local/bin/python','-c',SANDBOX_CHECK],capture_output=True,text=True,timeout=30)
            try:checks=json.loads(result.stdout)
            except ValueError:checks={}
            if result.returncode or not checks or not all(value is True for value in checks.values()):
                raise ExecutorError('container_sandbox_preflight_failed')
            readonly=subprocess.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-read','-C','/work','/usr/local/bin/python','-c',READONLY_CHECK],capture_output=True,text=True,timeout=30)
            if readonly.returncode or readonly.stdout.strip()!='readonly-denied':
                raise ExecutorError('container_readonly_preflight_failed')
    finally:
        if synthetic:auth.unlink(missing_ok=True)
    if synthetic or os.environ.get('MOONBOX_CHAT_EXECUTION_MODE')=='local-codex':
        source=Path(auth_source)
        if source.is_symlink() or not source.is_file() or source.stat().st_uid!=os.getuid():
            raise ExecutorError('container_auth_source_invalid')
        # New claims refresh only the credential file; personal config is never imported.
        stage=runtime/('auth-'+uuid.uuid4().hex+'.tmp')
        try:
            with source.open('rb') as reader,stage.open('xb') as writer:
                stage.chmod(0o600);shutil.copyfileobj(reader,writer)
            stage.replace(auth)
        finally: stage.unlink(missing_ok=True)
    return ContainerAppServer(workspace,runtime)
