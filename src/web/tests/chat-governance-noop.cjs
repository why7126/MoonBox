const { chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const browser=await chromium.launch();
 const out=path.resolve('../../logs/chat-governance-noop');fs.mkdirSync(out,{recursive:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}});
  const requests=[];
  const conversation={id:'noop',space_id:'space',repository_id:'repo',title:'重复完善验证',active_turn_id:null,archived:false};
  const latest={id:'latest',object_id:'BUG-0099-example',state:'unchanged',files:[],revision:1,manifest_hash:'a'.repeat(64)};
  await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'synthetic',access_token:'synthetic'})));
  await page.route('**/api/**',async route=>{
   const endpoint=new URL(route.request().url()).pathname;requests.push({endpoint,method:route.request().method()});
   let data={};
   if(endpoint.endsWith('/events'))return route.fulfill({contentType:'text/event-stream',body:''});
   if(endpoint.endsWith('/spaces'))data=[{id:'space',name:'验证空间'}];
   else if(endpoint.endsWith('/capabilities'))data={execution_ready:true,reason:'',repositories:[{id:'repo',space_id:'space'}]};
   else if(endpoint.endsWith('/conversations'))data={items:[conversation],total:1};
   else if(endpoint.endsWith('/conversations/noop'))data=conversation;
   else if(endpoint.endsWith('/messages'))data={items:[{id:'a',role:'assistant',turn_id:'turn',content:'已有草稿保持不变，无需更新。',materials:[],created_at:'2026-09-30T07:26:34Z'}]};
   else if(endpoint.endsWith('/turns/turn'))data={id:'turn',status:'completed'};
   else if(endpoint.endsWith('/relations'))data={primary:null,references:[]};
   else if(endpoint.endsWith('/projects'))data={projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]};
   else if(endpoint.endsWith('/governance-candidates'))data={items:[latest,{...latest,id:'old',state:'rejected',error_code:'governance_validation_failed'}]};
   else data={items:[]};
   await route.fulfill({json:{code:0,data}});
  });
  await page.goto('http://localhost:39002/chat?space_id=space&conversation_id=noop');
  const evidence=[];
  for(const phase of ['open','history']){
   if(phase==='history')await page.reload();
   const notice=page.getByText('已核验，事实源一致，无需更新。',{exact:true});
   await expect(notice).toBeVisible();
   await expect(page.getByText('治理结果未通过校验，未写入事实源。',{exact:true})).toHaveCount(0);
   await expect(page.getByTestId('governance-result-preview')).toHaveCount(0);
   evidence.push(await notice.evaluate(el=>({text:el.textContent,width:el.getBoundingClientRect().width,fontSize:getComputedStyle(el).fontSize})));
   await page.screenshot({path:path.join(out,phase+'.png')});
  }
  expect(requests.filter(r=>r.method==='POST'||r.endpoint.includes('governance-applications'))).toHaveLength(0);
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({mode:'real-components-synthetic-api',requests,evidence},null,2));
  console.log('No-op open/history DOM and no-write Network assertions passed');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
