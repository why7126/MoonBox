const { chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const browser = await chromium.launch();
 const out = path.resolve('../../logs/chat-preparation-failure');
 fs.mkdirSync(out,{recursive:true});
 try {
  const page = await browser.newPage({viewport:{width:1440,height:1000}});
  const network=[];
  const conversation={id:'prepare',space_id:'space',repository_id:'repo',title:'准备失败验证',active_turn_id:null,archived:false};
  await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'synthetic',access_token:'synthetic'})));
  await page.route('**/api/**',async route=>{
   const endpoint=new URL(route.request().url()).pathname;
   let data={};
   if(endpoint.endsWith('/events'))return route.fulfill({contentType:'text/event-stream',body:''});
   if(endpoint.endsWith('/spaces'))data=[{id:'space',name:'验证空间'}];
   else if(endpoint.endsWith('/capabilities'))data={execution_ready:true,reason:'',repositories:[{id:'repo',space_id:'space'}]};
   else if(endpoint.endsWith('/conversations'))data={items:[conversation],total:1};
   else if(endpoint.endsWith('/conversations/prepare'))data=conversation;
   else if(endpoint.endsWith('/messages'))data={items:[{id:'u',role:'user',turn_id:'turn',content:'/req-complete REQ-0027-example',materials:[],created_at:'2026-09-30T06:08:19Z'}]};
   else if(endpoint.endsWith('/turns/turn')){data={id:'turn',status:'failed',error_code:'workspace_unapplied_changes'};network.push({endpoint,...data});}
   else if(endpoint.endsWith('/relations'))data={primary:null,references:[]};
   else if(endpoint.endsWith('/projects'))data={current_user:{name:'synthetic'},workspaces:[],projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]};
   else data={items:[]};
   await route.fulfill({json:{code:0,data}});
  });
  await page.goto('http://localhost:39002/chat?space_id=space&conversation_id=prepare');
  const evidence=[];
  for(const phase of ['open','history']){
   if(phase==='history')await page.reload();
   await expect(page.locator('.chat-tool-summary')).toContainText('执行前阻断');
   await expect(page.locator('.chat-turn-activity [role="alert"]')).toContainText('尚未应用的成果');
   await expect(page.locator('.chat-turn-activity [role="status"]')).toHaveCount(0);
   await expect(page.getByText('正在等待执行结果…',{exact:true})).toHaveCount(0);
   evidence.push(await page.locator('.chat-turn-activity').evaluate(el=>({text:el.textContent,width:el.getBoundingClientRect().width,display:getComputedStyle(el).display})));
   await page.screenshot({path:path.join(out,phase+'.png')});
  }
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({mode:'real-components-synthetic-api',network,evidence},null,2));
  console.log('Preparation failure open/history DOM and Network assertions passed');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
