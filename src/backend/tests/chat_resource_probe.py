"""Disposable CPU/OOM guard probe with real isolated API+SQLite read samples."""
import json
import queue
import shutil
from types import SimpleNamespace
import subprocess
import time
import urllib.request


def main():
    name='moonbox-req0053-resource-probe'
    created=int(time.time())
    command="import time; end=time.monotonic()+100\nwhile time.monotonic()<end: sum(range(20000))\na=bytearray(1400*1024*1024); time.sleep(10)"
    subprocess.run(['docker','run','-d','--name',name,'--network','none','--cpus','1','--memory','1g','--memory-swap','1g',
        '--pids-limit','128','--read-only','--tmpfs','/tmp:rw,nosuid,size=64m','--entrypoint','python',
        'moonbox-backend:local','-c',command],check=True,capture_output=True)
    samples=[]
    try:
        for _ in range(105):
            started=time.monotonic();ok=False
            try:
                with urllib.request.urlopen('http://127.0.0.1:39057/api/v1/chat/conversations/ui-running/turns',timeout=2) as response:
                    data=json.load(response);ok=response.status==200 and data['data']['items'][0]['id']=='turn-running'
            except Exception:pass
            elapsed=time.monotonic()-started;samples.append({'ok':ok,'seconds':round(elapsed,4)})
            time.sleep(max(0,1-elapsed))
        state=json.loads(subprocess.run(['docker','inspect','--format','{{json .State}}',name],check=True,capture_output=True,text=True).stdout)
        from app.chat.container_server import ContainerAppServer
        from app.chat.app_server import ExecutorError
        adapter=ContainerAppServer.__new__(ContainerAppServer)
        adapter.incoming=queue.Queue();adapter.failure='executor_disconnected'
        adapter.created_epoch=created;adapter.container_name=name;adapter.docker=shutil.which('docker')
        adapter.process=SimpleNamespace(poll=lambda:state['ExitCode'])
        try:adapter._next(time.monotonic()+1)
        except ExecutorError as error:diagnostic=error.code
        good=sum(s['ok'] and s['seconds']<=2 for s in samples)
        report={'synthetic_identity':True,'api':'isolated production API route with SQLite',
            'cpu':1,'memory_gib':1,'swap_gib':0,'pids_limit':128,'tmpfs_mib':64,'sample_period_seconds':1,
            'sample_count':len(samples),'healthy_fraction':good/len(samples),'oom_killed':state['OOMKilled'],
            'container_exit_code':state['ExitCode'],'diagnostic':diagnostic,'max_read_seconds':max(s['seconds'] for s in samples)}
        print(json.dumps(report),flush=True)
        assert report['healthy_fraction']>=.99 and report['oom_killed'] and state['ExitCode']==137 and diagnostic=='container_memory_exhausted'
    finally:
        subprocess.run(['docker','rm','-f',name],check=True,capture_output=True)


if __name__=='__main__':main()
