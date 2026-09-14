const {chromium}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const root=process.env.GOVERNANCE_LIVE_ROOT;if(!root)throw Error('explicit private runtime required');
 const config=JSON.parse(fs.readFileSync(path.join(root,'browser.json')));
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const dir=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');
  await page.goto(config.url);
  await page.evaluate(async ({password})=>{
   const response=await fetch('/api/v1/auth/login',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({username:'alice',password,remember_me:false})});
   if(!response.ok)throw Error('real login failed');localStorage.setItem('moonbox.session',JSON.stringify((await response.json()).data));
   history.pushState(null,'','/requirements?space_id=space&repository_id=moonbox-validation');dispatchEvent(new PopStateEvent('popstate'));
  },config);
  const card=page.locator('[data-issue-id="REQ-9098"]');await card.waitFor({timeout:20000});
  await page.screenshot({path:path.join(dir,'live-board-before.png')});
  const source=path.join(root,'project/issues/requirements/plan',config.object_id,'requirement.md');
  if(fs.existsSync(source))throw Error('object already generated');
  const resume=process.env.GOVERNANCE_LIVE_RESUME==='1';
  if(resume){
    const prior=JSON.parse(fs.readFileSync(path.join(root,'live-conversation.json')));
    await page.evaluate(cid=>{history.pushState(null,'',`/chat?space_id=space&conversation_id=${cid}`);dispatchEvent(new PopStateEvent('popstate'))},prior.cid);
  } else {
  await card.locator('button.primary').click();await page.getByTestId('chat-prompt').waitFor();
  await page.waitForFunction(()=>document.querySelector('[data-testid=chat-prompt]')?.value?.includes('REQ-9098'));
  const cid=new URL(page.url()).searchParams.get('conversation_id');
  const count=await page.evaluate(async cid=>{const token=JSON.parse(localStorage.getItem('moonbox.session')).access_token;return (await(await fetch(`/api/v1/chat/conversations/${cid}/turns`,{headers:{authorization:`Bearer ${token}`}})).json()).data.items.length},cid);
  if(count!==0)throw Error('entry sent a turn');fs.writeFileSync(path.join(root,'live-conversation.json'),JSON.stringify({cid}));
  await page.screenshot({path:path.join(dir,'live-chat-before-send.png')});await page.getByTestId('chat-send').click();
  console.log(JSON.stringify({prepared:true,no_auto_send:true,sent:true}));
  }
  await page.waitForFunction(()=>{const el=document.querySelector('[data-testid=governance-result-preview]');return el&&!el.disabled},undefined,{timeout:600000});
  if(fs.existsSync(source))throw Error('source changed before confirmation');
  await page.getByTestId('governance-result-preview').click();await page.screenshot({path:path.join(dir,'live-candidate-preview.png')});
  await page.getByTestId('governance-maintenance-confirm').check();await page.getByTestId('governance-apply-confirm').click();
  await page.getByTestId('governance-application-state').filter({hasText:'已应用'}).waitFor({timeout:30000});
  await page.screenshot({path:path.join(dir,'live-applied.png')});
  await page.getByTestId('governance-apply-close').click();
  await page.evaluate(()=>{history.pushState(null,'','/requirements?space_id=space&repository_id=moonbox-validation');dispatchEvent(new PopStateEvent('popstate'))});
  await card.waitFor({timeout:20000});await page.screenshot({path:path.join(dir,'live-board-after.png')});
  const report={real_api:true,real_login:true,real_platform_worker:true,no_auto_send:true,source_unchanged_until_confirm:true,applied:true,errors};
  fs.writeFileSync(path.join(dir,'live-result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exitCode=1});
