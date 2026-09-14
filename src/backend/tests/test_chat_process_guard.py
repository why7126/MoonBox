import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import pytest

@pytest.mark.parametrize('failure',['worker_killed','executor_crashed'])
def test_owned_descendants_reaped_on_parent_loss(tmp_path,failure):
    root=tmp_path.resolve();ids=root/'ids.json';guard=Path(__file__).parents[1]/'app/chat/process_guard.py'
    executor=root/'executor.py'
    executor.write_text("import subprocess,sys,os,json,time\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)'])\nPath(sys.argv[1]).write_text(json.dumps({'executor':os.getpid(),'tool':p.pid}))\ntime.sleep(60)\n")
    owner=root/'owner.py'
    owner.write_text("import subprocess,sys,time\np=subprocess.Popen(sys.argv[1:])\ntime.sleep(60)\n")
    process=subprocess.Popen([sys.executable,str(owner),sys.executable,str(guard),sys.executable,str(executor),str(ids)])
    def live(pid):
        result=subprocess.run(['ps','-o','stat=','-p',str(pid)],capture_output=True,text=True)
        return result.returncode==0 and result.stdout.strip() and not result.stdout.strip().startswith('Z')
    targets={}
    try:
        deadline=time.monotonic()+5
        while not ids.exists() and time.monotonic()<deadline:time.sleep(.05)
        assert ids.exists();targets=json.loads(ids.read_text())
        assert all(live(pid) for pid in targets.values())
        if failure=='worker_killed':process.kill();process.wait()
        else:os.kill(targets['executor'],signal.SIGKILL)
        deadline=time.monotonic()+8
        while any(live(pid) for pid in targets.values()) and time.monotonic()<deadline:time.sleep(.1)
        assert not any(live(pid) for pid in targets.values())
    finally:
        if process.poll() is None:process.kill();process.wait()
        for pid in targets.values():
            if live(pid):
                try:os.kill(pid,signal.SIGKILL)
                except ProcessLookupError:pass
