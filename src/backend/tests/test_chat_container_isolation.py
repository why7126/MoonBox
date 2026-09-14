"""Explicit disposable Docker probe; no real repository, database, or authentication is mounted."""
import json
import os
from pathlib import Path
import subprocess
import pytest

@pytest.mark.skipif(os.environ.get('CHAT_CONTAINER_PROBE')!='1',reason='Explicit isolated Docker probe only')
def test_two_sandboxes_cannot_write_or_read_peer_and_host(tmp_path):
    probe='''import json,os,socket
from pathlib import Path
checks={}
p=Path('/work/counter');p.write_text('own sandbox');checks['own_workspace_writable']=p.read_text()=='own sandbox'
for key,path in [('root_readonly','/escape'),('git_readonly','/work/.git/escape')]:
 try:Path(path).write_text('blocked');checks[key]=False
 except OSError:checks[key]=True
checks['no_peer_mount']=not Path('/peer').exists()
checks['no_database_mount']=not Path('/app/data/sqlite/moonbox.db').exists()
checks['no_docker_socket']=not Path('/var/run/docker.sock').exists()
checks['no_platform_credentials']=not any(k in os.environ for k in ('OPENAI_API_KEY','CODEX_AUTH_JSON','DATABASE_URL'))
checks['non_root']=os.getuid()!=0
sock=socket.socket();sock.settimeout(1)
try:sock.connect(('1.1.1.1',443));checks['network_denied']=False
except OSError:checks['network_denied']=True
finally:sock.close()
assert all(checks.values()),checks
print(json.dumps(checks))'''
    results=[]
    for index in range(2):
        work=(tmp_path/f'sandbox-{index}').resolve();work.mkdir();work.chmod(0o777)
        (work/'.git').mkdir();(work/'.git').chmod(0o555)
        result=subprocess.run(['docker','run','--rm','--network','none','--read-only','--user','10001:10001',
            '--cap-drop','ALL','--security-opt','no-new-privileges:true','--pids-limit','32','--memory','128m','--cpus','0.5',
            '--tmpfs','/tmp:rw,noexec,nosuid,size=16m','--mount',f'type=bind,src={work},dst=/work',
            '--mount',f'type=bind,src={work/".git"},dst=/work/.git,readonly',
            'moonbox-backend:local','python','-c',probe],capture_output=True,text=True,timeout=30)
        assert result.returncode==0,result.stderr[-500:]
        results.append(json.loads(result.stdout))
    assert (tmp_path/'sandbox-0/counter').read_text()=='own sandbox'
    Path('/tmp/moonbox-chat-container-probe.json').write_text(json.dumps({'sandboxes':results,'boundary':'synthetic filesystem/network container checks only; not platform Codex credential execution'},indent=2))
