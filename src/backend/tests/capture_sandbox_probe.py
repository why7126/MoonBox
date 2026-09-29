"""Actual nested-container boundary probe with synthetic credentials only."""
import json,subprocess
from pathlib import Path
PROGRAM='''import tempfile,os,json,subprocess
from pathlib import Path
from app.governance.capture_executor import CaptureServer
from app.chat.container_server import write_profiles,READONLY_CHECK
with tempfile.TemporaryDirectory(prefix='capture-probe-',dir=os.environ['MOONBOX_CHAT_RUNTIME_ROOT']) as folder:
 root=Path(folder);work=root/'work';home=root/'runtime';work.mkdir(mode=0o700);home.mkdir(mode=0o700);(work/'.git').mkdir()
 write_profiles(home);(home/'auth.json').write_text('{"OPENAI_API_KEY":"synthetic-invalid-key"}');(home/'auth.json').chmod(0o600)
 with CaptureServer(work,home) as server:
  checks={}
  for name,code in {
   'workspace_readonly':READONLY_CHECK,
   'credential_denied':"import os;\\ntry: os.open('/runtime/auth.json',os.O_RDONLY)\\nexcept PermissionError: print('denied')\\nelse: raise RuntimeError('credential readable')",
   'no_formal_mount':"from pathlib import Path; assert not Path('/app/governance').exists() and not Path('/var/run/docker.sock').exists(); print('absent')"
  }.items():
   p=subprocess.run([server.docker,'exec',server.container_name,'codex','sandbox','-P','moonbox-read','-C','/work','/usr/local/bin/python','-c',code],capture_output=True,text=True,timeout=30)
   checks[name]=p.returncode==0
  print(json.dumps(checks))
'''
if __name__=='__main__':
 result=subprocess.run(['docker','exec','-i','moonbox-chat-worker','python','-c',PROGRAM],capture_output=True,text=True,timeout=100)
 checks=json.loads(result.stdout)
 Path('openspec/changes/add-capture-multimodal-candidate-review/evidence/container-boundary.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 1)
