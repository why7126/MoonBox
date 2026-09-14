// End-to-end observed latency against actual files/API/browser; no response interception.
const {chromium}=require('@playwright/test'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const root=process.env.GOVERNANCE_LIVE_ROOT;if(!root)throw Error('explicit runtime required');
 const config=JSON.parse(fs.readFileSync(path.join(root,'browser.json'))),browser=await chromium.launch();
 try{
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),dir=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');
  await page.goto(config.url);await page.evaluate(async({password})=>{
   const response=await fetch('/api/v1/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({username:'alice',password,remember_me:false})});
   if(!response.ok)throw Error('login failed');localStorage.setItem('moonbox.session',JSON.stringify((await response.json()).data));
   history.pushState(null,'','/requirements?space_id=space&repository_id=moonbox-validation');dispatchEvent(new PopStateEvent('popstate'));
  },config);
  const card=page.locator('[data-issue-id="REQ-9098"]');await card.waitFor({timeout:20000});
  const file=path.join(root,'project/issues/requirements/plan',config.object_id,'requirement.md');
  if(!fs.existsSync(file))throw Error('real apply must complete first');
  // Application is terminal before these operator-controlled external-edit samples.
  const registry=path.join(root,'project/issues/requirements/_registry.yaml'),samples=[];
  const mutate=require('node:child_process').execFileSync;
  fs.unlinkSync(path.join(root,'private/maintenance.json')); // Real apply is terminal; external-edit observation starts after the maintenance window closes.
  await page.getByLabel('搜索治理对象').fill('REQ-9098');
  for(let i=1;i<=10;i++){
   const title=`本地项目刷新观察 ${String(i).padStart(2,'0')}`;
   const start=Date.now();
   const flushed=Number(mutate('python',['-c',"import sys,yaml,time;from pathlib import Path;p=Path(sys.argv[1]);d=yaml.safe_load(p.read_text());next(x for x in d['entries'] if x['id']==sys.argv[2])['title']=sys.argv[3];p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));print(int(time.time()*1000))",registry,config.object_id,title],{encoding:'utf8'}).trim());
   await card.getByText(title,{exact:true}).waitFor({timeout:5000});const shown=Date.now();
   samples.push({sequence:i,write_started_at:start,stable_written_at:flushed,presented_at:shown,latency_ms:shown-flushed});
  }
  await page.screenshot({path:path.join(dir,'live-refresh-10.png')});
  const report={source:'observed',real_api:true,stable_file_changes:10,all_under_5_seconds:samples.every(x=>x.latency_ms<=5000),filter_preserved:await page.getByLabel('搜索治理对象').inputValue()==='REQ-9098',samples};
  fs.writeFileSync(path.join(dir,'live-refresh.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exitCode=1});
