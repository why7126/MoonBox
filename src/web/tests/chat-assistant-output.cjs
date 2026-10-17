// Real browser / real components with synthetic API. Backend behavior is tested separately.
const { firefox, chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const type = process.env.CHAT_TEST_BROWSER === 'chromium' ? chromium : firefox;
 const browser = await type.launch();
 const browserName = process.env.CHAT_TEST_BROWSER === 'chromium' ? 'chromium' : 'firefox';
 const out = path.resolve(__dirname, '../../../logs/BUG-0030-chat-assistant-output-missing-from-conversation/visual', browserName);
 fs.mkdirSync(out, {recursive:true});
 const evidence=[];
 try {
  const page=await browser.newPage();
  let status='unknown';
  const conversation={id:'body',space_id:'space',repository_id:'repo',title:'助手正文合成验收',active_turn_id:'turn',archived:false};
  await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'synthetic',access_token:'synthetic'})));
  await page.route('**/api/**',async route=>{
   const endpoint=new URL(route.request().url()).pathname;
   let data={};
   if(endpoint.endsWith('/events'))return route.fulfill({contentType:'text/event-stream',body:'id: 1\nevent: execution.output\ndata: {"text":"合成正文已保存"}\n\n'});
   if(endpoint.endsWith('/spaces'))data=[{id:'space',name:'验证空间'}];
   else if(endpoint.endsWith('/capabilities'))data={execution_ready:true,reason:'',repositories:[{id:'repo',space_id:'space'}]};
   else if(endpoint.endsWith('/conversations'))data={items:[conversation],total:1};
   else if(endpoint.endsWith('/conversations/body'))data=conversation;
   else if(endpoint.endsWith('/messages'))data={items:[{id:'assistant-turn',turn_id:'turn',role:'assistant',content:'合成正文已保存',created_at:'2026-10-08T10:00:00Z',materials:[],output_partial:status!=='completed',output_truncated:status==='unknown',output_source:'events'}]};
   else if(endpoint.endsWith('/turns/turn'))data={id:'turn',status};
   else if(endpoint.endsWith('/relations'))data={primary:null,references:[]};
   else if(endpoint.endsWith('/projects'))data={current_user:{name:'synthetic'},workspaces:[],projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]};
   else data={items:[]};
   await route.fulfill({json:{code:0,data}});
  });
  for(const width of [1440,390]){
   await page.setViewportSize({width,height:1000});
   for(const next of ['unknown','stopped','failed','completed']){
    status=next;
    await page.goto((process.env.CHAT_TEST_URL||'http://localhost:39002')+'/chat?space_id=space&conversation_id=body');
    for(const phase of ['open','reload']){
     if(phase==='reload')await page.reload();
     await expect(page.locator('.chat-message-bubble')).toContainText('合成正文已保存');
     await expect(page.getByTestId('chat-partial-output')).toHaveCount(status==='completed'?0:1);
     if(status==='unknown')await expect(page.locator('.chat-turn-activity')).toContainText('不要重复发送命令');
     const box=await page.locator('.chat-assistant-col').evaluate(el=>({width:el.getBoundingClientRect().width,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,display:getComputedStyle(el).display,color:getComputedStyle(el).color}));
     expect(box.width).toBeGreaterThan(0);expect(box.scrollWidth).toBeLessThanOrEqual(box.clientWidth+1);
     evidence.push({viewport_width:width,status,phase,...box});
     await page.screenshot({path:path.join(out,`${width}-${status}-${phase}.png`)});
    }
    await page.locator('.chat-tool-summary').click();
    await expect(page.getByTestId('chat-conversation')).toBeHidden();
    await page.goto((process.env.CHAT_TEST_URL||'http://localhost:39002')+'/chat?space_id=space&conversation_id=body');
    await expect(page.locator('.chat-message-bubble')).toContainText('合成正文已保存');
   }
  }
  fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({mode:'browser-with-synthetic-api',evidence},null,2));
  console.log('PASS: browser states, reload/re-entry, trajectory switch and 1440/390 layout');
 } finally {await browser.close();}
})().catch(error=>{console.error(error.message);process.exitCode=1;});
