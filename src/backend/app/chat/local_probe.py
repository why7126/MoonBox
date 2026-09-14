"""显式本机验证用认证目录；不是生产多用户执行配置。"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile

from app.chat.app_server import AppServer, ExecutorError
from app.chat.workspace import trusted_directory


@contextmanager
def local_executor(workspaces, *, executable, auth_source):
    """Only trusted test code calls this helper. Never accept paths from an API caller."""
    if os.environ.get('CHAT_LIVE_ISOLATED_PROBE') != '1':
        raise ExecutorError('local_probe_not_enabled')
    workspaces = [trusted_directory(path) for path in workspaces]
    if not workspaces: raise ExecutorError('local_probe_workspace_missing')
    # Authenticate outside all model-readable roots; keep local config/history/plugins out of the probe.
    source = Path(auth_source)
    info = source.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
        raise ExecutorError('local_auth_source_invalid')
    with tempfile.TemporaryDirectory(prefix='moonbox-local-auth-', dir='/private/tmp') as temporary:
        home = Path(temporary); config = home/'codex'; config.mkdir(mode=0o700)
        target = config/'auth.json'
        with source.open('rb') as reader, target.open('xb') as writer:
            os.chmod(target, 0o600); shutil.copyfileobj(reader, writer)
        # Each workspace gets its own permissions profiles and Codex history directory.
        homes = {}
        for index, workspace in enumerate(workspaces):
            codex_home = home/f'worker-{index}'; codex_home.mkdir(mode=0o700)
            shutil.copyfile(target, codex_home/'auth.json'); (codex_home/'auth.json').chmod(0o600)
            filesystem = {'/':'read','/Users':'deny','/private':'deny','/Volumes':'deny',str(Path.home()):'deny',str(home):'deny'}
            text = 'model_reasoning_effort = "low"\ncli_auth_credentials_store = "file"\nweb_search = "disabled"\n[features]\napps = false\nmulti_agent = false\n[analytics]\nenabled = false\n'
            for mode in ('read','write'):
                rules = {**filesystem, str(workspace): mode, str(workspace/'.git'): 'read'}
                text += f'\n[permissions.moonbox-{mode}.filesystem]\n'
                text += ''.join(json.dumps(k)+' = '+json.dumps(v)+'\n' for k,v in rules.items())
                text += f'\n[permissions.moonbox-{mode}.network]\nenabled = false\n'
            (codex_home/'config.toml').write_text(text)
            homes[workspace] = codex_home
        def factory(workspace):
            workspace = trusted_directory(workspace)
            if workspace not in homes: raise ExecutorError('local_probe_workspace_unbound')
            return AppServer(executable, workspace, homes[workspace], home=home, write=True,
                             permission_profile='moonbox-write', timeout=30, effort='low')
        yield factory, home


def persistent_local_server(workspace, runtime_home, auth_source, executable):
    """由隔离启动器拥有整个生命周期；worker重启不删除原线程历史。"""
    workspace=trusted_directory(workspace);home=trusted_directory(runtime_home)
    import hashlib
    codex_home=home/hashlib.sha256(str(workspace).encode()).hexdigest()
    codex_home.mkdir(mode=0o700,exist_ok=True);trusted_directory(codex_home)
    target=codex_home/'auth.json'
    if not target.exists():
        with Path(auth_source).open('rb') as reader,target.open('xb') as writer:
            os.chmod(target,0o600);shutil.copyfileobj(reader,writer)
    rules={'/':'read','/Users':'deny','/private':'deny','/Volumes':'deny',str(Path.home()):'deny',str(home):'deny'}
    config='model_reasoning_effort = "low"\ncli_auth_credentials_store = "file"\nweb_search = "disabled"\n[features]\napps = false\nmulti_agent = false\n[analytics]\nenabled = false\n'
    for mode in ('read','write'):
        config+=f'\n[permissions.moonbox-{mode}.filesystem]\n'
        config+=''.join(json.dumps(k)+' = '+json.dumps(v)+'\n' for k,v in {**rules,str(workspace):mode,str(workspace/'.git'):'read'}.items())
        config+=f'\n[permissions.moonbox-{mode}.network]\nenabled = false\n'
    (codex_home/'config.toml').write_text(config)
    return AppServer(executable,workspace,codex_home,home=home,write=True,permission_profile='moonbox-write',effort='low')
