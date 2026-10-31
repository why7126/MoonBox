"""受信任worker的独立容器适配；浏览器不可提供镜像、挂载或Docker命令。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import hashlib
import threading

from app.chat import recovery_runtime

_PREFLIGHT_CACHE = {}
_PREFLIGHT_LOCK = threading.Lock()

from app.chat.app_server import AppServer, ExecutorError
from app.chat.workspace import trusted_directory

TOOL_PATH = '/usr/local/bin:/usr/bin:/bin'


def write_profiles(runtime):
    runtime = trusted_directory(runtime)
    config = 'model_reasoning_effort="low"\ncli_auth_credentials_store="file"\nweb_search="disabled"\n[features]\napps=false\nmulti_agent=false\n[analytics]\nenabled=false\n'
    # Tool caches must never use the private credential HOME of app-server.
    config += '\n[shell_environment_policy.set]\nHOME="/tmp"\nXDG_CONFIG_HOME="/tmp/config"\nXDG_CACHE_HOME="/tmp/cache"\nOPENSPEC_TELEMETRY="0"\nDO_NOT_TRACK="1"\nPATH="' + TOOL_PATH + '"\n'
    config += 'MOONBOX_CHAT_TOOL_SANDBOX="1"\n'
    profiles = {
        'read': {'/':'read','/runtime':'deny','/proc':'deny','/work':'read','/work/.git':'read'},
        'write': {'/':'read','/runtime':'deny','/proc':'deny','/work':'write','/work/.git':'read'},
        'governance': {'/':'read','/runtime':'deny','/proc':'deny','/work':'read',
            '/work/issues':'write','/work/openspec/changes':'write','/work/iterations':'write','/work/docs/spec-logs':'write','/work/.git':'read'},
        'archive': {'/':'read','/runtime':'deny','/proc':'deny','/work':'read',
            '/work/issues':'write','/work/openspec/changes':'write','/work/openspec/specs':'write',
            '/work/openspec/archive':'write','/work/iterations':'write','/work/docs/spec-logs':'write','/work/.git':'read'},
    }
    from app.moonbox_exec_server.context import DELIVERY
    delivery = DELIVERY.get()
    if delivery:
        from app.moonbox_core.delivery_policy import writable_roots
        roots = writable_roots(delivery['change_id'])
        for mode in ('write', 'governance', 'archive'):
            profiles[mode] = {'/':'read','/runtime':'deny','/proc':'deny','/work':'read','/work/.git':'read'}
        for relative in roots:
            profiles['write']['/work/' + relative] = 'write'
        profiles['write']['/work/docs/spec-logs'] = 'read'
    for mode, paths in profiles.items():
        from app.moonbox_exec_server.scope import EXCLUDED
        for relative in EXCLUDED:
            if relative != '.git':
                # Codex creates an empty protected .codex directory inside its
                # sandbox. A deny-file overlay conflicts with that directory.
                # Host preflight rejects nonempty repository tool directories.
                paths['/work/' + relative] = 'read' if relative == '.codex' else 'deny'
        paths['/tmp'] = 'write'
        config += f'\n[permissions.moonbox-{mode}.filesystem]\n'
        for path, access in paths.items():
            config += json.dumps(path) + '=' + json.dumps(access) + '\n'
        config += f'\n[permissions.moonbox-{mode}.network]\nenabled=false\n'
    (runtime / 'config.toml').write_text(config)
    (runtime / 'config.toml').chmod(0o600)


class ContainerAppServer(AppServer):
    IMAGE = 'moonbox-chat-executor:0.153.4-test'

    def __init__(self, workspace, runtime, *, write=True, timeout=180, write_scope=None):
        self.docker = shutil.which('docker')
        if not self.docker:raise ExecutorError('container_runtime_unavailable')
        if os.getuid()==0:raise ExecutorError('nonroot_controller_required')
        workspace=trusted_directory(workspace);runtime=trusted_directory(runtime)
        if runtime.stat().st_mode & 0o077 or (runtime/'auth.json').is_symlink():
            raise ExecutorError('container_credential_directory_invalid')
        if workspace == runtime or workspace in runtime.parents or runtime in workspace.parents:
            raise ExecutorError('container_mount_overlap')
        from app.moonbox_exec_server.git_view import prepare as prepare_git_view
        git_view = prepare_git_view(workspace, runtime) if (workspace / '.git').is_file() else None
        if git_view is None:
            trusted_directory(workspace / '.git')
        self.container_name = 'moonbox-chat-session-' + uuid.uuid4().hex
        self.created_epoch = int(time.time())
        self.recovery_context = recovery_runtime.CURRENT.get()
        if self.recovery_context and getattr(self.recovery_context, 'image', None):
            self.IMAGE = self.recovery_context.image
        from app.moonbox_exec_server.context import IMAGE
        selected_image = IMAGE.get() or self.IMAGE
        inspected = recovery_runtime.run([self.docker, 'image', 'inspect', '--format', '{{.Id}}', selected_image],
                                         capture_output=True, text=True, timeout=10)
        import re
        if inspected.returncode or not re.fullmatch(r'sha256:[0-9a-f]{64}', inspected.stdout.strip()):
            raise ExecutorError('container_runtime_unavailable')
        self.IMAGE = inspected.stdout.strip()
        from app.governance.archive_tools import selected
        try:
            self.archive_package = selected()
        except ValueError as error:
            raise ExecutorError(str(error)) from None
        self.mounts = ['--mount', f'type=bind,src={workspace},dst=/work',
                       '--mount', f'type=bind,src={runtime},dst=/runtime']
        if self.archive_package:
            from app.governance.archive_tools import MOUNT
            package = self.archive_package
            configuration = runtime / 'archive-tools.json'
            configuration.write_text(json.dumps({'schema_version': 1, 'root': MOUNT,
                'host_root': MOUNT, 'digest': package.digest}))
            configuration.chmod(0o444)
            self.mounts += ['--mount', f'type=bind,src={package.host_root},dst={MOUNT},readonly',
                '--mount', f'type=bind,src={configuration},dst=/etc/moonbox/archive-tools.json,readonly']
        if git_view:
            self.mounts += ['--mount', f'type=bind,src={git_view[0]},dst=/git,readonly',
                           '--mount', f'type=bind,src={git_view[1]},dst=/work/.git,readonly']
        else:
            self.mounts += ['--mount', f'type=bind,src={workspace / ".git"},dst=/work/.git,readonly']
        # A test-owned runtime is prepared by the controller; never load personal config.
        scope = write_scope or ('implementation_write' if write else 'read_only')
        super().__init__(self.docker, workspace, runtime, home=runtime, write=write,
                         timeout=timeout, permission_profile=None, effort='low', write_scope=scope)

    def transport_environment(self):
        # Docker context belongs to the trusted controller, not the isolated CODEX_HOME.
        endpoint = os.environ.get('DOCKER_HOST')
        if not endpoint:
            result = recovery_runtime.run([self.docker, 'context', 'inspect', '--format', '{{.Endpoints.docker.Host}}'],
                                          capture_output=True, text=True, timeout=5)
            if result.returncode: raise ExecutorError('container_runtime_unavailable')
            endpoint = result.stdout.strip()
        if not endpoint.startswith('unix://'): raise ExecutorError('container_runtime_endpoint_unsupported')
        return {'DOCKER_HOST': endpoint}

    def options(self):
        return ['--read-only','--log-driver','none','--user',f'{os.getuid()}:{os.getgid()}','--cap-drop','ALL',
                '--security-opt','no-new-privileges:true',
                '--security-opt','seccomp='+str(Path(__file__).parents[2]/'container/seccomp-codex.json'),'--pids-limit','128',
                '--memory','1g','--memory-swap','1g','--cpus','1','--tmpfs','/tmp:rw,nosuid,size=64m',
                '--workdir','/work','--env','HOME=/runtime','--env','CODEX_HOME=/runtime', *self.mounts]

    def version_command(self, executable):
        return [self.docker,'run','--rm', *self.recovery_labels(), '--network','none','--read-only',self.IMAGE,'codex','--version']

    def version_timeout(self):
        # A cold Docker start can exceed the local CLI's 30-second limit.
        return recovery_runtime.timeout(180)

    def archive_launch(self):
        if not getattr(self, 'archive_package', None):
            return ['codex', 'app-server', '--stdio', '-c', 'shell_environment_policy.inherit="none"', '-c', 'features.default_mode_request_user_input=true']
        from app.governance.archive_tools import MOUNT, selected
        if selected() != self.archive_package:
            raise ExecutorError('archive_tool_changed')
        # Validation executes inside the actual app-server container before Codex.
        probe = ('import sys,os;sys.path.insert(0,' + repr(MOUNT + '/src/backend') + ');'
                 'from app.governance.archive_tools import selected;'
                 'p=selected();assert p is not None and p.digest==' + repr(self.archive_package.digest) + ';'
                 'os.execvp("codex",["codex","app-server","--stdio","-c",'
                 '\'shell_environment_policy.inherit="none"\',"-c","features.default_mode_request_user_input=true"])')
        return ['python', '-B', '-c', probe]

    def launch_command(self, executable):
        return [self.docker,'run','--rm','--init','--interactive','--name',self.container_name,
                *self.recovery_labels(), '--label','moonbox.chat.platform=true' if os.environ.get('MOONBOX_CHAT_EXECUTION_MODE')=='local-codex' else 'moonbox.chat.test=true',*self.options(), self.IMAGE,
                *self.archive_launch()]

    def recovery_labels(self):
        return self.recovery_context.labels() if self.recovery_context else []

    def rpc(self, method, params):
        if self.recovery_context:
            self.timeout = self.recovery_context.remaining(self.timeout)
        if 'cwd' in params:
            if params['cwd'] != str(self.workspace):raise ExecutorError('container_workspace_mismatch')
            params={**params,'cwd':'/work'}
        return super().rpc(method, params)

    def _next(self, deadline):
        if self.recovery_context: deadline = min(deadline, self.recovery_context.deadline)
        try: return super()._next(deadline)
        except ExecutorError as error:
            if error.code != 'executor_disconnected': raise
            # --rm stays enabled. Docker's bounded event history can still prove
            # an OOM after removal; absence is not proof of a different cause.
            try:
                evidence = subprocess.run([self.docker, 'events', '--since', str(self.created_epoch),
                    '--until', str(int(time.time())+1), '--filter', 'container='+self.container_name,
                    '--filter', 'event=oom', '--format', '{{.Action}}'],
                    capture_output=True, text=True, timeout=3)
                if evidence.returncode == 0 and 'oom' in evidence.stdout.splitlines():
                    raise ExecutorError('container_memory_exhausted') from None
            except (OSError, subprocess.TimeoutExpired): pass
            if self.process.poll() == 137: raise ExecutorError('container_terminated') from None
            raise

    def _verify_thread(self, thread, expected):
        if thread.get('cwd') != '/work':raise ExecutorError('executor_workspace_mismatch')
        super()._verify_thread({**thread,'cwd':str(self.workspace)},expected)

    def close(self):
        try:super().close()
        finally:
            subprocess.run([self.docker,'rm','--force',self.container_name],capture_output=True,timeout=10)
            checked = subprocess.run([self.docker, 'ps', '-a', '--filter', 'name=^/' + self.container_name + '$',
                '--format', '{{.Names}}'], capture_output=True, text=True, timeout=10)
            if checked.returncode or checked.stdout.strip():
                raise ExecutorError('executor_shutdown_unconfirmed')


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
with tempfile.TemporaryFile() as file:
 import fcntl
 file.write(b'lock');fcntl.flock(file,fcntl.LOCK_EX|fcntl.LOCK_NB)
 checks['temporary_lock_write']=True
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
    from app.moonbox_exec_server.context import IMAGE
    if IMAGE.get() is None:
        result = recovery_runtime.run(['docker','image','inspect','--format','{{.Id}}',ContainerAppServer.IMAGE],
            capture_output=True,text=True,timeout=10)
        import re
        if result.returncode or not re.fullmatch(r'sha256:[0-9a-f]{64}', result.stdout.strip()):
            raise ExecutorError('container_runtime_unavailable')
        IMAGE.set(result.stdout.strip())
    runtime=runtime_root/hashlib.sha256(str(workspace).encode()).hexdigest()
    runtime.mkdir(mode=0o700,exist_ok=True);trusted_directory(runtime)
    write_profiles(runtime)
    auth=runtime/'auth.json';synthetic=not auth.exists()
    if auth.is_symlink():raise ExecutorError('container_auth_path_invalid')
    if synthetic:
        with auth.open('x') as file:
            auth.chmod(0o600);file.write('{"OPENAI_API_KEY":"synthetic-invalid-key"}')
    try:
        cache_key = preflight_key(workspace, runtime, auth_source) if recovery_runtime.CURRENT.get() else None
        cached = cache_key is not None and time.monotonic() < _PREFLIGHT_CACHE.get(cache_key, 0)
        if recovery_runtime.CURRENT.get(): recovery_runtime.CURRENT.get().metrics["cache_hit"] = cached
        if not cached:
            verify_preflight(workspace, runtime)
            if cache_key is not None:
                with _PREFLIGHT_LOCK:
                    _PREFLIGHT_CACHE.clear()
                    _PREFLIGHT_CACHE[cache_key] = time.monotonic() + 300
    finally:
        if synthetic:auth.unlink(missing_ok=True)
    if synthetic or recovery_runtime.CURRENT.get() or os.environ.get('MOONBOX_CHAT_EXECUTION_MODE')=='local-codex':
        refresh_auth(auth_source, runtime, auth)
    return ContainerAppServer(workspace,runtime,write=not bool(recovery_runtime.CURRENT.get()))


def verify_preflight(workspace, runtime):
    with ContainerAppServer(workspace,runtime) as server:
        verify_toolchain(server)
        from app.moonbox_exec_server.context import DELIVERY
        check = SANDBOX_CHECK
        if DELIVERY.get():
            from app.moonbox_core.delivery_policy import writable_roots
            writable = next((p for p in writable_roots(DELIVERY.get()['change_id']) if (workspace/p).is_dir()), None)
            if writable is None: raise ExecutorError('container_sandbox_preflight_failed')
            check = check.replace("dir='.'", 'dir=' + repr(writable))
        result=recovery_runtime.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-write','-C','/work','/usr/local/bin/python','-c',check],capture_output=True,text=True,timeout=30)
        try:checks=json.loads(result.stdout)
        except ValueError:checks={}
        if result.returncode or not checks or not all(value is True for value in checks.values()):
            raise ExecutorError('container_sandbox_preflight_failed')
        readonly=recovery_runtime.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-read','-C','/work','/usr/local/bin/python','-c',READONLY_CHECK],capture_output=True,text=True,timeout=30)
        if readonly.returncode or readonly.stdout.strip()!='readonly-denied':
            raise ExecutorError('container_readonly_preflight_failed')
        governance=recovery_runtime.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-governance','-C','/work','/usr/local/bin/python','-c',"import tempfile,fcntl; f=tempfile.TemporaryFile(); f.write(b'lock'); fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB); print('governance-lock-ready')"],capture_output=True,text=True,timeout=30)
        if governance.returncode or governance.stdout.strip()!='governance-lock-ready':
            raise ExecutorError('container_governance_lock_unavailable')

def refresh_auth(auth_source, runtime, auth):
    source=Path(auth_source)
    if source.is_symlink() or not source.is_file() or source.stat().st_uid!=os.getuid():
        raise ExecutorError('container_auth_source_invalid')
    stage=runtime/('auth-'+uuid.uuid4().hex+'.tmp')
    try:
        with source.open('rb') as reader,stage.open('xb') as writer:
            stage.chmod(0o600);shutil.copyfileobj(reader,writer)
        stage.replace(auth)
    finally: stage.unlink(missing_ok=True)


def preflight_key(workspace, runtime, auth_source):
    """No raw identity or credential bytes leave this in-memory digest."""
    from app.governance.archive_tools import selected
    package = selected()
    source = Path(auth_source)
    if source.is_symlink() or not source.is_file() or source.stat().st_uid != os.getuid():
        raise ExecutorError('container_auth_source_invalid')
    result = recovery_runtime.run(['docker', 'image', 'inspect', '--format', '{{.Id}}', ContainerAppServer.IMAGE],
                                 capture_output=True, text=True, timeout=5)
    if result.returncode or not result.stdout.strip(): return None
    if recovery_runtime.CURRENT.get(): recovery_runtime.CURRENT.get().image = result.stdout.strip()
    stats = [(str(path), path.stat().st_dev, path.stat().st_ino, path.stat().st_mode)
             for path in (workspace, workspace/'.git', runtime)]
    policy = Path(__file__).read_bytes() + (Path(__file__).parents[2]/'container/seccomp-codex.json').read_bytes()
    return hashlib.sha256(result.stdout.encode() + repr(stats).encode() + policy + (package.digest.encode() if package else b'legacy') +
                          (runtime/'config.toml').read_bytes() + source.read_bytes()).hexdigest()


def verify_toolchain(server):
    try:
        result = recovery_runtime.run([server.docker, 'exec', server.container_name,
            'codex', 'sandbox', '-P', 'moonbox-read', '-C', '/work',
            '/usr/bin/env', '-i', f'PATH={TOOL_PATH}', 'HOME=/tmp',
            'XDG_CONFIG_HOME=/tmp/config', 'XDG_CACHE_HOME=/tmp/cache',
            'OPENSPEC_TELEMETRY=0', 'DO_NOT_TRACK=1',
            '/usr/local/bin/python', '/app/container/check_toolchain.py'],
            capture_output=True, text=True, timeout=180)
        report = json.loads(result.stdout)
        if result.returncode or report != {'ready': True, 'unavailable': []}:
            allowed = {'python','git','bash','rg','node','npm','pnpm','openspec','uv','curl','jq','patch','unzip','zip'}
            missing = report.get('unavailable', []) if isinstance(report, dict) else []
            tools = sorted(set(missing) & allowed) if isinstance(missing, list) and all(isinstance(value, str) for value in missing) else []
            print(json.dumps({'event': 'chat.toolchain_preflight_failed', 'tools': tools}), flush=True)
            raise ExecutorError('container_toolchain_unavailable')
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        raise ExecutorError('container_toolchain_unavailable') from error
