"""Read-only Codex execution; no formal repository or writer credentials are mounted."""
import os
from pathlib import Path
import shutil
import tempfile
import time
import threading
import hashlib
import subprocess
from uuid import UUID
from app.chat.app_server import ExecutorError
from app.chat.container_server import ContainerAppServer, write_profiles
from app.chat.workspace import trusted_directory

STOP=threading.Event()


def runtime_label():
    return hashlib.sha256(os.environ.get('MOONBOX_CHAT_RUNTIME_ROOT','').encode()).hexdigest()


def recover_copies():
    """Called under the exclusive worker lock before accepting new tasks."""
    root=trusted_directory(os.environ['MOONBOX_CHAT_RUNTIME_ROOT'])
    docker=shutil.which('docker')
    if not docker:raise ExecutorError('container_runtime_unavailable')
    result=subprocess.run([docker,'ps','-aq','--filter','label=moonbox.capture.runtime='+runtime_label()],
        check=True,capture_output=True,text=True,timeout=20)
    containers=result.stdout.split()
    if containers:subprocess.run([docker,'rm','-f',*containers],check=True,capture_output=True,timeout=20)
    for child in root.glob('capture-*'):
        if child.is_symlink() or not child.is_dir() or child.stat().st_uid!=os.getuid():continue
        marker=child/'.capture-owned'
        if marker.is_file() and not marker.is_symlink() and marker.read_text()=='1':shutil.rmtree(child)
    STOP.clear()


class CaptureServer(ContainerAppServer):
    def __init__(self, workspace, runtime):
        super().__init__(workspace,runtime,write=False)

    def options(self):
        return [v+',readonly' if v.startswith('type=bind,src=') and v.endswith('dst=/work') else v
                for v in super().options()]+['--label','moonbox.capture.runtime='+runtime_label()]

    def launch_command(self, executable):
        command=super().launch_command(executable)
        for key in ('shell_tool','unified_exec','multi_agent','apps','image_generation'):
            command+=['-c',f'features.{key}=false']
        return command+['-c','web_search="disabled"']

    def organize(self,prompt,image_names):
        if STOP.is_set():raise ExecutorError('capture_worker_stopping')
        thread=self.connect()
        inputs=[{'type':'text','text':prompt}]+[{'type':'localImage','path':'/work/'+name} for name in image_names]
        response=self.rpc('turn/start',{'threadId':thread,'input':inputs,'cwd':str(self.workspace),
            'approvalPolicy':'never','permissions':'moonbox-read'})
        tid=response.get('turn',{}).get('id')
        if not tid:raise ExecutorError('executor_missing_turn')
        deadline=time.monotonic()+300;messages=[]
        while time.monotonic()<deadline:
            if STOP.is_set():
                self.interrupt(thread,tid);raise ExecutorError('capture_worker_stopping')
            event=self.event(1)
            if not event:continue
            params=event.get('params',{})
            if params.get('turnId') not in (None,tid):continue
            if event.get('method')=='item/completed':
                item=params.get('item',{})
                if item.get('type')=='agentMessage':messages.append(item.get('text',''))
                elif item.get('type') in ('commandExecution','fileChange','mcpToolCall'):
                    self.interrupt(thread,tid);raise ExecutorError('organizer_tool_boundary')
            if event.get('method')=='turn/completed':
                turn=params.get('turn',{})
                if turn.get('id')!=tid:continue
                if turn.get('status')!='completed' or not messages:raise ExecutorError('organizer_failed')
                value=messages[-1].strip()
                return '\n'.join(value.splitlines()[1:-1]) if value.startswith('```') else value
        self.interrupt(thread,tid);raise ExecutorError('organizer_timeout')


def execute(prompt,images):
    configured_root=os.environ.get('MOONBOX_CHAT_RUNTIME_ROOT')
    configured_auth=os.environ.get('MOONBOX_CHAT_AUTH_FILE')
    if not configured_root or not configured_auth:raise ExecutorError('capture_executor_unconfigured')
    runtime=trusted_directory(configured_root);auth=Path(configured_auth)
    if not auth.is_file() or auth.is_symlink() or auth.stat().st_uid!=os.getuid():raise ExecutorError('capture_executor_auth_unavailable')
    with tempfile.TemporaryDirectory(prefix='capture-',dir=runtime) as folder:
        root=Path(folder);(root/'.capture-owned').write_text('1');work=root/'work';home=root/'runtime'
        work.mkdir(mode=0o700);home.mkdir(mode=0o700);(work/'.git').mkdir()
        names=[]
        for media_id,image in images:
            name=str(UUID(media_id))+'.'+{'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}[image.content_type]
            (work/name).write_bytes(image.data);names.append(name)
        write_profiles(home)
        shutil.copyfile(auth,home/'auth.json');(home/'auth.json').chmod(0o600)
        server=None
        try:
            server=CaptureServer(work,home)
            return server.organize(prompt,names)
        finally:
            if server:server.close()
