"""从指定临时测试环境导出脱敏验证事实，不导出登录或原始执行记录。"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

root=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
config=json.loads((root/'config.json').read_text());cid=json.loads((root/'conversation.json').read_text())['cid']
workspace=root/'workspaces'/cid;runtime=root/'runtime'/hashlib.sha256(str(workspace).encode()).hexdigest()
targets={'credential_denied':str(runtime/'auth.json'),'database_denied':str(root/'chat.db'),'peer_denied':str(root/'seed/counter.txt')}
code='''import os,json,socket
from pathlib import Path
checks={}
for key,path in TARGETS.items():
 try:fd=os.open(path,os.O_RDONLY);os.close(fd);checks[key]=False
 except PermissionError:checks[key]=True
checks['workspace_read']=Path('counter.txt').read_text()=='2\\n'
try:Path('.git/forbidden').write_text('bad');checks['git_write_denied']=False
except PermissionError:checks['git_write_denied']=True
s=socket.socket();s.settimeout(1)
try:s.connect(('1.1.1.1',443));checks['network_denied']=False
except OSError:checks['network_denied']=True
finally:s.close()
assert all(checks.values())
print(json.dumps(checks))
'''
env={'PATH':'/usr/bin:/bin','HOME':str(root/'runtime'),'CODEX_HOME':str(runtime)}
probe=subprocess.run([config['executable'],'sandbox','-P','moonbox-write','-C',str(workspace),'/usr/bin/python3','-c','TARGETS='+repr(targets)+'\n'+code],env=env,capture_output=True,text=True,timeout=30)
assert probe.returncode==0,'native isolation failed; output withheld'
readonly=subprocess.run([config['executable'],'sandbox','-P','moonbox-read','-C',str(workspace),'/usr/bin/python3','-c',"from pathlib import Path\ntry:Path('forbidden').write_text('bad')\nexcept PermissionError:print('denied')\nelse:raise AssertionError()"],env=env,capture_output=True,text=True,timeout=30)
assert readonly.returncode==0 and readonly.stdout.strip()=='denied'
report={'runtime':'codex-cli 0.153.4','deployment':'loopback native API + built Web + independent worker','business_responses_mocked':False,'native_isolation':json.loads(probe.stdout),'readonly_write_denied':True,'cleanup_pending':True}
with sqlite3.connect(root/'chat.db') as db:
 db.row_factory=sqlite3.Row
 thread=db.execute('select thread_id from chat_conversations where id=?',(cid,)).fetchone()[0]
 report['same_thread_after_worker_restart']=hashlib.sha256(thread.encode()).hexdigest()==json.loads((root/'thread-before.json').read_text())['hash']
 report['turns']=[dict(r) for r in db.execute('select t.status,t.error_code,r.status reservation,r.actual_tokens from chat_turns t join chat_usage_reservations r on r.turn_id=t.id order by t.created_at')]
 names=[r[0] for r in db.execute('select name from sqlite_master where type="table"')]
 # Table names and counts are safe; relation checks avoid copying actor tokens or message bodies.
 for name in ('chat_request_logs','usage_events','task_traces','task_trace_spans'):
  if name in names:report[name+'_count']=db.execute('select count(*) from '+name).fetchone()[0]
 report['trace_request_linked']=db.execute('select count(*) from task_traces t join chat_request_logs r on r.request_id=t.parent_request_id').fetchone()[0]==len(report['turns'])
 report['unique_events']=not db.execute('select turn_id,source_id,count(*) n from chat_events group by turn_id,source_id having n>1').fetchall()
 diff=json.loads(db.execute('select payload from chat_diff_snapshots d join chat_turns t on t.id=d.turn_id where t.status="completed" order by t.created_at desc limit 1').fetchone()[0])
 report['cumulative_diff_correct']=any('-0\n+2' in f.get('patch','') for f in diff['cumulative_files'])
for phase in ('first','second','stop','restart-active'):
 report[phase]=json.loads((root/(phase+'-result.json')).read_text())
for name in ('first.png','second.png','stop-confirm.png','stopped.png','worker-running.png','worker-restarted.png'):
 shutil.copyfile(root/name,out/name)
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'exported':True,'native_isolation':True}))
