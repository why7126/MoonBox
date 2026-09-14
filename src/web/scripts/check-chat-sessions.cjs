const {chromium}=require(process.cwd()+'/node_modules/@playwright/test');
const fs=require('node:fs');
const origin=process.argv[2]||'http://localhost:18102';
const dir='../../openspec/changes/add-chat-workbench-codex/evidence/session-ui';
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'视觉测试',access_token:'synthetic-test-token'})));
 await page.route('**/api/v1/requirement-center/context',route=>route.fulfill({json:{code:0,data:{currentUser:{name:'视觉测试',avatarInitial:'测试',canAccessAdmin:false,permissions:[]},workspaces:[{workspaceId:'space',name:'隔离验收空间',role:'成员',memberCount:1}],selectedWorkspaceId:'space'}}}));
 let executionFixture=false;
 let row={id:'synthetic',space_id:'space',repository_id:'sandbox-repo',title:'Chat 工作台验收会话',archived:false,pinned:false,active_turn_id:null,created_at:'2026-09-08T00:00:00Z',updated_at:'2026-09-08T00:00:00Z'};
 await page.route('**/api/v1/chat/**',async route=>{
  const req=route.request(),url=new URL(req.url()); let data;
  if(req.headers()['authorization']!=='Bearer synthetic-test-token')throw Error('missing auth');
  if(url.pathname.endsWith('/spaces'))data=[{id:'space',name:'隔离验收空间'}];
  else if(url.pathname.endsWith('/capabilities'))data={execution_ready:false,reason:'执行服务尚未通过隔离与额度验收，暂不可发送',repositories:[{id:'sandbox-repo',space_id:'space'}]};
  else if(url.pathname.endsWith('/deletion-check'))data={allowed:true,reason:null,workspace_hash:null};
  else if(url.pathname.endsWith('/relations'))data={primary:null,references:[]};
  else if(url.pathname.endsWith('/objects'))data={items:[{id:'REQ-9001-synthetic',title:'关联动作族验收对象'},{id:'REQ-9002-synthetic',title:'引用快照验收对象'}],reason:null};
  else if(req.method()==='PATCH'){row={...row,...req.postDataJSON()};data=row;}
  else if(req.method()==='POST')data=row;
  else if(executionFixture && url.pathname.endsWith('/events')){await route.fulfill({contentType:'text/event-stream',body:'id: 1\nevent: execution.output\ndata: {"text":"合成执行事件，仅用于视觉验收"}\n\n'});return;}
  else if(executionFixture && url.pathname.endsWith('/diff'))data={available:true,files:[{path:'src/counter.txt',status:'modified',before_size:2,after_size:2,patch:'--- a/src/counter.txt\n+++ b/src/counter.txt\n-1\n+2\n'}],cumulative_files:[]};
  else if(executionFixture && url.pathname.endsWith('/context'))data=[{object_id:'REQ-9001-synthetic',title:'合成快照',content:'原始引用内容',version:'123456789abc',truncated:true}];
  else if(executionFixture && url.pathname.endsWith('/turns'))data={items:[{id:'synthetic-turn',conversation_id:'synthetic',status:'running',created_at:'2026-09-08T00:00:00Z'}]};
  else if((url.pathname.endsWith('/turns')||url.pathname.endsWith('/messages')))data={items:[]};
  else data={items:String(row.archived)===url.searchParams.get('archived')?[row]:[],total:1,page:1,page_size:20};
  await route.fulfill({json:{code:0,data,message:'成功'}});
 });
 fs.mkdirSync(dir,{recursive:true}); const evidence=[];
 await page.goto(origin+'/chat'); await page.getByTestId('chat-new-session').waitFor();
 for(const [theme,width,height] of [['dark',1440,900],['light',1440,900],['light',1024,600],['light',390,844]]){
  await page.setViewportSize({width,height});
  if(theme==='light'&&await page.getByTestId('chat-shell').getAttribute('data-theme')==='dark')await page.getByTestId('chat-theme-toggle').click();
  if(width<1281&&await page.getByTestId('chat-execution-panel').count())await page.getByRole('button',{name:'关闭执行详情'}).click();
  await page.getByTestId('chat-history-trigger').click();
  await page.getByTestId('chat-rename-trigger').waitFor();
  await page.screenshot({path:`${dir}/history-${theme}-${width}.png`,fullPage:true});
  const style=await page.getByTestId('chat-history-dialog').evaluate(e=>{const s=getComputedStyle(e);const r=e.getBoundingClientRect();return {width:r.width,height:r.height,x:r.x,y:r.y,borderRadius:s.borderRadius,backgroundColor:s.backgroundColor,fontFamily:s.fontFamily,overflow:s.overflow};});
  if(style.x<0||style.x+style.width>width||style.y<0||style.y+style.height>height)throw Error('dialog outside viewport');
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('horizontal overflow');
  evidence.push({theme,width,height,style});
  await page.getByTestId('chat-rename-trigger').click();
  await page.getByLabel('会话标题').fill('验收重命名');
  await page.screenshot({path:`${dir}/rename-${theme}-${width}.png`});
  await page.getByTestId('chat-modal-cancel').click();
  await page.getByTestId('chat-history-trigger').click();await page.getByTestId('chat-delete-trigger').click();
  await page.getByTestId('chat-delete-confirm').waitFor();
  await page.waitForFunction(()=>!document.querySelector('[data-testid=chat-modal-submit]')?.disabled);
  await page.screenshot({path:`${dir}/delete-${theme}-${width}.png`});
  await page.getByTestId('chat-modal-cancel').click();
 }
 await page.setViewportSize({width:1440,height:900});
 await page.getByTestId('chat-session-picker').click();await page.getByTestId('chat-session-popover').waitFor();
 await page.screenshot({path:`${dir}/picker-light-1440.png`});
 await page.keyboard.press('Escape');
 await page.getByTestId('chat-new-session').click();await page.getByTestId('chat-modal-submit').click();
 await page.getByTestId('chat-new-dialog').waitFor({state:'hidden'});
 if(!await page.getByTestId('chat-send').isDisabled())throw Error('execution gate');
 for(const [theme,width,height] of [['dark',1440,900],['light',1440,900],['light',1024,600],['light',390,844]]){
  await page.setViewportSize({width,height});
  if(await page.getByTestId('chat-shell').getAttribute('data-theme')!==theme)await page.getByTestId('chat-theme-toggle').click();
  await page.getByTestId('chat-relations-trigger').click();
  await page.getByLabel('引用 REQ-9002-synthetic',{exact:true}).waitFor();
  await page.getByLabel('主对象',{exact:true}).selectOption('REQ-9001-synthetic');
  await page.getByLabel('引用 REQ-9002-synthetic',{exact:true}).check();
  const style=await page.getByTestId('chat-relations-dialog').evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,borderRadius:s.borderRadius,backgroundColor:s.backgroundColor,padding:s.padding};});
  if(style.x<0||style.y<0||style.x+style.width>width||style.y+style.height>height)throw Error('relations dialog outside viewport');
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('relations horizontal overflow');
  await page.screenshot({path:`${dir}/relations-${theme}-${width}.png`});
  evidence.push({component:'relations',theme,width,height,style});
  await page.getByTestId('chat-modal-cancel').click();
  if(await page.getByTestId('chat-relations-bar').innerText().then(t=>!t.includes('未关联')))throw Error('cancel persisted relations');
 }
 executionFixture=true;
 await page.setViewportSize({width:1440,height:900});
 if(!await page.getByTestId('chat-execution-panel').count())await page.getByTestId('chat-panel-toggle').click();
 await page.getByTestId('chat-stop-current').waitFor();
 await page.getByTestId('chat-diff').locator('summary').filter({hasText:'src/counter.txt'}).click();
 await page.screenshot({path:dir+'/execution-light-1440.png'});
 await page.getByTestId('chat-stop-current').click();
 await page.getByTestId('chat-stop-confirm').waitFor();
 await page.screenshot({path:dir+'/stop-light-1440.png'});
 await page.getByTestId('chat-modal-cancel').click();
 for(const [width,height] of [[1024,600],[390,844]]){
  await page.setViewportSize({width,height});
  const button=await page.getByTestId('chat-stop-current').boundingBox();
  if(!button||button.x<0||button.y<0||button.x+button.width>width||button.y+button.height>height)throw Error('current stop outside viewport');
  await page.screenshot({path:`${dir}/execution-light-${width}.png`});
  await page.getByTestId('chat-stop-current').click();
  const modal=await page.getByTestId('chat-stop-confirm').boundingBox();
  if(!modal||modal.y<0||modal.y+modal.height>height)throw Error('stop confirmation clipped');
  await page.screenshot({path:`${dir}/stop-light-${width}.png`});
  await page.getByTestId('chat-modal-cancel').click();
  evidence.push({component:'execution-stop',width,height,button,modal});
 }
 const diffStyle=await page.getByLabel('Diff 比较范围').evaluate(element=>{
  const actual=getComputedStyle(element),reference=getComputedStyle(document.querySelector('[data-testid=chat-turn-select]'));
  return {backgroundColor:actual.backgroundColor,borderRadius:actual.borderRadius,padding:actual.padding,fontFamily:actual.fontFamily,referenceBackground:reference.backgroundColor,referenceRadius:reference.borderRadius};
 });
 if(diffStyle.backgroundColor!==diffStyle.referenceBackground||diffStyle.borderRadius!==diffStyle.referenceRadius)throw Error('diff select style mismatch');
 evidence.push({component:'diff-select',style:diffStyle});
 fs.writeFileSync(dir+'/computed.json',JSON.stringify({boundary:'Browser API mocks use synthetic data; this verifies UI, not real backend or model execution.',screenshots:23,evidence,create:'pass',escape:'pass',executionGate:'pass'},null,2));
 console.log(JSON.stringify({screenshots:23,viewports:'pass',create:'pass',boundary:'synthetic API responses'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exitCode=1});
