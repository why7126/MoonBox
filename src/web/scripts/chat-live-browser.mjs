// Real HTTP/browser verification. Never route or mock business responses.
import { chromium, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
const root=process.argv[2],mode=process.argv[3]||'first';
const cfg=JSON.parse(fs.readFileSync(path.join(root,'browser.json'),'utf8'));
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:1440,height:900}});
const page=await context.newPage();
let errors=[];page.on('pageerror',e=>errors.push(e.name));
try {
 const login=await context.request.post(cfg.url+'/api/v1/auth/login',{data:{username:'alice',password:cfg.password,remember_me:false}});
 if(login.status()!==200)throw Error('real login failed');
 const session=(await login.json()).data;
 await page.addInitScript(s=>localStorage.setItem('moonbox.session',JSON.stringify(s)),session);
 const saved=mode!=='first'&&fs.existsSync(path.join(root,'conversation.json'))?JSON.parse(fs.readFileSync(path.join(root,'conversation.json'),'utf8')).cid:null;
 await page.goto(cfg.url+'/chat'+(saved?'?space_id=space&conversation_id='+saved:''));await page.waitForLoadState('networkidle');
 fs.writeFileSync(path.join(root,'dom.txt'),await page.locator('body').innerText());
 await page.screenshot({path:path.join(root,'initial.png')});
 const headers={Authorization:'Bearer '+session.access_token};
 const req=async(method,url,data)=>{const r=await context.request.fetch(cfg.url+'/api/v1/chat'+url,{method,headers,data});if(!r.ok())throw Error('API '+r.status()+' '+url);return (await r.json()).data;};
 if(mode==='inspect'){
  const styles=await page.locator('[data-testid=chat-shell], [data-testid=chat-prompt], [data-testid=chat-send]').evaluateAll(nodes=>nodes.map(node=>{const css=getComputedStyle(node);return {selector:node.getAttribute('data-testid'),width:css.width,height:css.height,color:css.color,fontSize:css.fontSize};}));
  fs.writeFileSync(path.join(root,'computed.json'),JSON.stringify(styles,null,2));
  await page.getByLabel('Diff 比较范围').selectOption('cumulative');
  await page.getByTestId('chat-diff').scrollIntoViewIfNeeded();
  await page.getByTestId('chat-diff').locator('summary').filter({hasText:'counter.txt'}).click();
  await expect(page.getByTestId('chat-diff')).toContainText('+2');
  await page.screenshot({path:path.join(root,'cumulative-diff.png')});
  console.log('rendered');
 }
 else {
  let cid;
  if(mode==='first'){
   await page.getByTestId('chat-new-session').click();
   const created=page.waitForResponse(r=>r.url().endsWith('/api/v1/chat/conversations')&&r.request().method()==='POST');
   await page.getByTestId('chat-modal-submit').click();cid=(await (await created).json()).data.id;
   fs.writeFileSync(path.join(root,'conversation.json'),JSON.stringify({cid}));
   await req('PUT',`/conversations/${cid}/relations`,{primary:'REQ-9001-synthetic'});
   await page.reload();await page.waitForLoadState('networkidle');
  } else cid=JSON.parse(fs.readFileSync(path.join(root,'conversation.json'),'utf8')).cid;
  const value=mode==='first'?'1':'2';
  if(mode==='stop'||mode==='restart-active'){
   let turn;
   const parent=await req('GET',`/conversations/${cid}`);
   if(parent.active_turn_id)turn=await req('GET',`/turns/${parent.active_turn_id}`);
   else {
    await page.getByTestId('chat-prompt').fill('受控中止测试：首先执行 /bin/sleep 45，不要修改任何文件，结束后简短回复。');
    const started=page.waitForResponse(r=>r.url().endsWith(`/conversations/${cid}/turns`)&&r.request().method()==='POST');
    await page.getByTestId('chat-send').click();turn=(await (await started).json()).data;
   }
   if(!turn?.id)throw Error('stop turn not admitted');
   await expect.poll(async()=>{const r=await context.request.get(cfg.url+`/api/v1/chat/turns/${turn.id}/events`,{headers});return (await r.text()).includes('execution.tool');},{timeout:180000,intervals:[500]}).toBe(true);
   await page.getByTestId('chat-turn-select').selectOption(turn.id);
   if(mode==='restart-active'){
    await page.screenshot({path:path.join(root,'worker-running.png')});
    fs.writeFileSync(path.join(root,'restart-ready.json'),JSON.stringify({ready:true}));
   } else {
    await page.getByTestId('chat-stop-current').click();
    await page.screenshot({path:path.join(root,'stop-confirm.png')});
    await page.getByTestId('chat-modal-submit').click();
   }
   await expect.poll(async()=>(await req('GET',`/turns/${turn.id}`)).status,{timeout:60000,intervals:[500]}).toBe('stopped');
   await page.reload();await page.waitForLoadState('networkidle');
   await expect(page.getByTestId('chat-turn-select')).toContainText('已停止',{timeout:15000});
   if(fs.readFileSync(path.join(root,'workspaces',cid,'counter.txt'),'utf8')!=='2\n')throw Error('stop changed file');
   await page.screenshot({path:path.join(root,mode==='stop'?'stopped.png':'worker-restarted.png'),fullPage:true});
   fs.writeFileSync(path.join(root,mode+'-result.json'),JSON.stringify({real_stop:true,terminal_confirmed:true,refresh_restored:true,actual_file_preserved:true,pageerrors:errors}));
   console.log(mode+' confirmed stopped');
  } else {
  await page.getByTestId('chat-prompt').fill(`受控测试：先执行 /bin/sleep 8，然后将 counter.txt 修改为数字 ${value} 加换行。不要修改其他文件，不要提交。完成后简短回复。`);
  const sent=page.waitForResponse(r=>r.url().endsWith(`/conversations/${cid}/turns`)&&r.request().method()==='POST');
  await page.getByTestId('chat-send').click();const turn=(await (await sent).json()).data;
  if(!turn?.id)throw Error('send not admitted');
  await page.reload();await page.waitForLoadState('networkidle');
  await expect.poll(async()=>(await req('GET',`/turns/${turn.id}`)).status,{timeout:180000,intervals:[1000]}).toBe('completed');
  await expect(page.getByTestId('chat-turn-select')).toContainText('已完成',{timeout:15000});
  const diff=await req('GET',`/turns/${turn.id}/diff`);
  if(!diff.available||!diff.files.some(f=>f.patch.includes('+'+value))||(mode==='second'&&!diff.cumulative_files.some(f=>f.patch.includes('-0\n+2'))))throw Error('diff mismatch');
  if(fs.readFileSync(path.join(root,'workspaces',cid,'counter.txt'),'utf8')!==value+'\n')throw Error('actual file mismatch');
  const bob=await context.request.post(cfg.url+'/api/v1/auth/login',{data:{username:'bob',password:cfg.password}});
  const other=(await bob.json()).data;
  const denied=await context.request.get(cfg.url+`/api/v1/chat/conversations/${cid}`,{headers:{Authorization:'Bearer '+other.access_token}});
  if(denied.status()!==404)throw Error('owner boundary failed');
  const cap=await context.request.get(cfg.url+'/api/v1/chat/capabilities?space_id=space',{headers:{Authorization:'Bearer '+other.access_token}});
  if((await cap.json()).data.execution_ready)throw Error('actor allowlist failed');
  await page.screenshot({path:path.join(root,mode+'.png'),fullPage:true});
  fs.writeFileSync(path.join(root,mode+'-result.json'),JSON.stringify({real_login:true,real_send:true,page_reload:true,completed:true,actual_file:true,diff:true,other_actor_denied:true,pageerrors:errors},null,2));
  console.log(JSON.stringify({phase:mode,completed:true,pageerrors:errors.length}));
  }
 }
} finally {await context.close();await browser.close();}
