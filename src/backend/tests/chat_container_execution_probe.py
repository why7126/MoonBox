"""先合成隔离、后临时本地凭证的真实容器探针；无现有业务DB挂载。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from app.chat.container_server import ContainerAppServer, write_profiles


from app.chat.container_server import SANDBOX_CHECK as CHECK


def terminal(server, thread, turn):
    deadline=time.monotonic()+180
    while time.monotonic()<deadline:
        event=server.event(timeout=1)
        if not event:continue
        params=event.get('params',{})
        if event.get('method')=='turn/completed' and params.get('threadId')==thread and params.get('turn',{}).get('id')==turn:
            return params['turn']['status']
    raise RuntimeError('container terminal not confirmed')


def main():
    if os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1':raise SystemExit('explicit opt-in required')
    report={'real_model_in_container':False}
    with tempfile.TemporaryDirectory(prefix='moonbox-container-live-',dir='/private/tmp') as folder:
        root=Path(folder);work=root/'work';work.mkdir(mode=0o700)
        runtime=root/'runtime';runtime.mkdir(mode=0o700)
        subprocess.run(['git','init','-q',str(work)],check=True)
        (work/'counter.txt').write_text('0\n')
        write_profiles(runtime)
        auth=runtime/'auth.json';auth.write_text('{"OPENAI_API_KEY":"synthetic-invalid-key"}');auth.chmod(0o600)
        with ContainerAppServer(work,runtime) as server:
            result=subprocess.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-write','-C','/work','/usr/local/bin/python','-c',CHECK],capture_output=True,text=True,timeout=30)
            if result.returncode:
                # At this point only synthetic credentials exist; retain short diagnostic.
                Path('/tmp/moonbox-container-sandbox-error.log').write_text(result.stderr[-3000:])
                raise RuntimeError('synthetic container sandbox failed; real credentials not copied')
            report['isolation']=json.loads(result.stdout)
        source=Path.home()/'.codex/auth.json'
        if source.is_symlink() or not source.is_file() or source.stat().st_uid!=os.getuid():raise RuntimeError('local auth source invalid')
        with source.open('rb') as reader, auth.open('wb') as writer:shutil.copyfileobj(reader,writer)
        thread=None
        for value in ('1','2'):
            with ContainerAppServer(work,runtime) as server:
                resumed=server.connect(thread)
                if thread is not None:assert resumed==thread
                thread=resumed
                turn=server.start_turn(thread,f'Controlled integration test: set counter.txt to exactly {value} followed by newline. Modify no other files. Do not commit. Reply done.')
                assert terminal(server,thread,turn)=='completed'
                assert (work/'counter.txt').read_text()==value+'\n'
        report.update(real_model_in_container=True,two_file_changes=True,thread_resumed_after_container_recreation=True)
        print(json.dumps(report),flush=True)
        with ContainerAppServer(work,runtime) as server:
            server.connect(thread)
            turn=server.start_turn(thread,'Run sleep 45 then reply done. Do not modify files.')
            deadline=time.monotonic()+60;tool_started=False;types=[]
            while time.monotonic()<deadline:
                event=server.event(timeout=1)
                if not event:continue
                params=event.get('params',{})
                if event.get('method')=='item/started' and params.get('turnId')==turn:
                    kind=params.get('item',{}).get('type');types.append(kind)
                    if kind in ('commandExecution','mcpToolCall','dynamicToolCall'):
                        tool_started=True;break
            assert tool_started, 'no running tool to interrupt: '+repr(types)
            server.interrupt(thread,turn)
            stopped=terminal(server,thread,turn)
            assert stopped=='interrupted','stop result='+stopped
            report['stop_confirmed']=True
        assert (work/'counter.txt').read_text()=='2\n'
    report['temporary_credentials_and_workspaces_removed']=not root.exists()
    Path('/tmp/moonbox-container-execution.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
