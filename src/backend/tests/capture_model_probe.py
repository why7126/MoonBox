"""Opt-in real model comparison against capture classification rules, synthetic inputs only."""
import json
import sys
from pathlib import Path
import subprocess
import time

ROOT=Path(__file__).resolve().parents[3]
CASES=[
 ('mixed-1','已有保存按钮点击报500；希望新增CSV导出。',None),
 ('mixed-2','已支持筛选但状态筛选不生效；希望增加批量标签。',None),
 ('mixed-3','已有登录功能正确密码却被拒绝；新增扫码登录。',None),
 ('mixed-4','已有深色模式切换后文字消失；希望支持定时切换主题。',None),
 ('bug-1','保存接口本应成功，点击保存出现图中的错误。','ERROR: Save failed (HTTP 500)'),
 ('bug-2','已有项目列表，图中加载失败；期望显示我的项目。','Project list: Failed to load (HTTP 503)'),
 ('ambiguous-1','这个列表太难用了。',None),
 ('ambiguous-2','提交很慢，不清楚是不是网络问题。',None),
 ('image-1','', 'ERROR: Save failed (HTTP 500)'),
 ('image-2','', 'Feature request: Export projects to CSV'),
 ('lineage-1','希望增加草稿保存和恢复，这两项一起验收；另一个独立诉求是CSV导出。',None),
 ('lineage-2','保存失败原先说是BUG，但保存尚未开发，请作为新增需求；另需新增导出。',None),
]
REMOTE='''import json,sys,time
from io import BytesIO
from types import SimpleNamespace
from PIL import Image,ImageDraw
from app.governance.capture_executor import execute
from app.governance.capture_organizer import RULES,Organized,validate_result
case=json.loads(sys.stdin.readline()); images=[];mid='4f377906-12a4-425b-9406-9dac6a5c8491'
if case['image']:
 im=Image.new('RGB',(1100,300),'white');ImageDraw.Draw(im).text((30,100),case['image'],fill='black',font_size=32)
 out=BytesIO();im.save(out,format='PNG');images=[(mid,SimpleNamespace(data=out.getvalue(),content_type='image/png'))]
payload={'text':case['text'],'media_ids':[mid] if images else []}
rule=RULES if case['mode']=='adapter' else case['baseline']
prompt=rule+'\\n仅整理候选不落盘、不运行工具。type仅requirement或bug。输出JSON Schema：'+json.dumps(Organized.model_json_schema(),ensure_ascii=False)+'\\n材料JSON：'+json.dumps(payload,ensure_ascii=False)
start=time.monotonic()
try:
 raw=execute(prompt,images);value=validate_result(raw,payload)
 print(json.dumps({'valid':True,'result':value,'seconds':round(time.monotonic()-start,2)},ensure_ascii=False))
except Exception as exc:print(json.dumps({'valid':False,'error_type':type(exc).__name__,'reason':str(exc),'raw':locals().get('raw'),'seconds':round(time.monotonic()-start,2)}))
'''

def main():
 skill=(ROOT/'.agents/skills/capture/SKILL.md').read_text()
 baseline=skill.split('## 分类要点',1)[1].split('---',1)[0]
 for name,heading in [('req-capture','## Multi-REQ'),('bug-capture','## Multi-BUG')]:
  body=(ROOT/'.agents/skills'/name/'SKILL.md').read_text();baseline+='\n'+body.split(heading,1)[1].split('**规则**',1)[0]
 baseline+='\n每条需求必须建议priority P0/P1/P2/P3，每条缺陷必须建议severity blocker/critical/high/medium/low，不同时使用两个字段。不得虚构根因与事实。此处仅比较分类拆分内容：候选不得提供id，parents为空；不执行编号和目录落盘步骤。source_refs只允许字符串text（有文字时）或材料media_ids内的图片ID。'
 evidence=ROOT/'openspec/changes/add-capture-multimodal-candidate-review/evidence/model-comparison.json'
 records=[]
 if '--diagnostic' in sys.argv:evidence=evidence.with_name('model-diagnostic.json')
 if '--baseline-only' in sys.argv:
  previous=json.loads(evidence.read_text());evidence=evidence.with_name('model-comparison-verified.json')
  records=[r for r in previous if r['mode']=='adapter']
 for name,text,image in (CASES[:1] if '--diagnostic' in sys.argv else CASES):
  for mode in (('baseline',) if '--baseline-only' in sys.argv or '--only-baseline' in sys.argv else ('adapter','baseline')):
   case=dict(name=name,text=text,image=image,mode=mode,baseline=baseline)
   # Code and synthetic input are supplied as stdin, no credentials or private config are read here.
   program=REMOTE.replace('case=json.loads(sys.stdin.readline())', 'case=json.loads('+repr(json.dumps(case,ensure_ascii=False))+')')
   result=subprocess.run(['docker','exec','-i','moonbox-chat-worker','python','-c',program],capture_output=True,text=True,timeout=340)
   try:out=json.loads(result.stdout)
   except ValueError:out={'valid':False,'error_type':'worker_probe_failed'}
   records.append({'case':name,'mode':mode,**out});evidence.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
   print(name,mode,'pass' if out['valid'] else out.get('reason',out['error_type']),flush=True)
if __name__=='__main__':main()
