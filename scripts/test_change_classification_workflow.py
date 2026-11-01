"""Run real OpenSpec CLI in a disposable repository; no product chat is invoked."""
from pathlib import Path
import tempfile, subprocess, sys, shutil, yaml, json
root=Path(__file__).resolve().parents[1];results=[]
with tempfile.TemporaryDirectory(prefix='moonbox-req59-') as td:
 base=Path(td).resolve();shutil.copytree(root/'scripts',base/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
 (base/'src').mkdir();(base/'src/backend').symlink_to(root/'src/backend',target_is_directory=True)
 for cid,kind,field,grade,reason in [('fix-evaluation-sample','fix','severity','high','核心交付操作无法完成，存在人工替代路径；无数据丢失证据。'),('update-evaluation-sample','non_fix','priority','P2','改进常规交付信息准确性，无紧急期限或核心功能阻断。')]:
  run=subprocess.run(['openspec','new','change',cid],cwd=base,capture_output=True,text=True);assert run.returncode==0
  folder=base/'openspec/changes'/cid
  (folder/'proposal.md').write_text('---\ntitle: 独立分级隔离观察\n---\n# 独立分级隔离观察\n\n'+reason+'\n')
  meta={'title':'独立分级隔离观察追溯','status':'proposed','change_type':kind,field:grade,'execution':{'schema_version':1,'started_at':None,'completed_at':None,'last_event':'opsx.propose'},'classification':{'state':'assessed','dimension':field,'rationale':reason,'evidence_refs':['proposal.md'],'evaluated_at':'2026-11-01 00:48:00','evaluated_by':'codex'}}
  trace=folder/'trace.md';trace.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n# 独立分级隔离观察追溯\n')
  cmd=[sys.executable,str(base/'scripts/sync-workflow-status.py'),'--event','opsx.propose','--change',cid,'--sprint','none']
  first=subprocess.run(cmd,cwd=base,capture_output=True,text=True);assert first.returncode==0,first.stdout[-1500:]
  old=trace.read_bytes();second=subprocess.run(cmd,cwd=base,capture_output=True,text=True);assert second.returncode==0 and trace.read_bytes()==old
  meta['classification']['state']='pending';trace.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---\n# 独立分级隔离观察追溯\n')
  negative=subprocess.run(cmd,cwd=base,capture_output=True,text=True);assert negative.returncode!=0
  results.append({'sample':cid,'dimension':field,'grade':grade,'cli_creation':'passed','completion':'passed','retry_unchanged':True,'pending_rejected':True,'environment':'isolated real CLI; agent supplied assessment; no product conversation/model execution'})
print(json.dumps(results,ensure_ascii=False))
