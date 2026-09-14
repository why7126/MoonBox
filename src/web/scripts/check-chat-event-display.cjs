const {chromium}=require(process.cwd()+'/node_modules/@playwright/test');
const fs=require('node:fs');
const dir='../../openspec/changes/add-chat-workbench-codex/evidence/event-display';
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'视觉测试',access_token:'synthetic-test-token'})));
 await page.route('**/api/v1/requirement-center/context',route=>route.fulfill({json:{code:0,data:{currentUser:{name:'视觉测试',avatarInitial:'测试',canAccessAdmin:false,permissions:[]},workspaces:[{workspaceId:'space',name:'验收空间',role:'成员',memberCount:1}],selectedWorkspaceId:'space'}}}));
 const row={id:'synthetic',space_id:'space',repository_id:'sandbox',title:'事件与表格验收',archived:false,pinned:false,active_turn_id:null,created_at:'2026-09-10T00:00:00Z',updated_at:'2026-09-10T00:00:00Z'};
 const events=[{type:'execution.state',payload:{status:'running'}},...['我','先','查看','需求','台账','和','归档','状态。'].map(text=>({type:'execution.output',payload:{text,item_id:'a'}})),{type:'execution.tool',payload:{type:'commandExecution',phase:'completed'}},{type:'execution.output',payload:{text:'检查完成。',item_id:'b'}},{type:'execution.state',payload:{status:'completed'}}].map((e,i)=>({...e,sequence:i+1}));
 await page.route('**/api/v1/chat/**',async route=>{
  const url=new URL(route.request().url());let data;
  if(url.pathname.endsWith('/spaces'))data=[{id:'space',name:'验收空间'}];
  else if(url.pathname.endsWith('/capabilities'))data={execution_ready:true,reason:'执行服务已就绪',repositories:[{id:'sandbox',space_id:'space'}]};
  else if(url.pathname.endsWith('/relations'))data={primary:null,references:[]};
  else if(url.pathname.endsWith('/events')) {const after=Number(url.searchParams.get('after')||0);await route.fulfill({contentType:'text/event-stream',body:events.filter(e=>e.sequence>after).map(e=>`id: ${e.sequence}\nevent: ${e.type}\ndata: ${JSON.stringify(e.payload)}\n\n`).join('')});return;}
  else if(url.pathname.endsWith('/diff'))data={available:true,files:[],cumulative_files:[]};
  else if(url.pathname.endsWith('/context'))data=[];
  else if(url.pathname.endsWith('/turns'))data={items:[{id:'turn',conversation_id:'synthetic',status:'completed',created_at:row.created_at}]};
  else if(url.pathname.endsWith('/messages'))data={items:[{id:'message',role:'assistant',content:'已核对需求记录。\n\n| 需求编号 | 名称 | 状态 |\n| --- | --- | --- |\n| REQ-9001 | **事件展示** | 已完成 |\n| REQ-9002 | 表格渲染 | 已完成 |\n\n表格下方正文。',created_at:row.created_at}]};
  else if(url.pathname.endsWith('/synthetic'))data=row;
  else data={items:[row],total:1,page:1,page_size:20};
  await route.fulfill({json:{code:0,data}});
 });
 fs.mkdirSync(dir,{recursive:true});await page.goto((process.argv[2]||'http://localhost:18102')+'/chat?conversation_id=synthetic&space_id=space');
 await page.getByRole('table').waitFor();if(!await page.getByTestId('chat-execution-panel').isVisible())await page.getByTestId('chat-panel-toggle').click();await page.locator('.chat-event-group').first().waitFor();console.log((await page.getByTestId('chat-execution-events').innerText()).slice(0,700));await page.getByText('我先查看需求台账和归档状态。',{exact:true}).waitFor();
 if(await page.locator('.chat-event-group').count()!==5)throw Error('group count');
 if(await page.getByTestId('chat-turn-status').innerText()!=='所选轮次当前状态：已完成')throw Error('current status');
 if(await page.getByTestId('chat-raw-events').getAttribute('open')!==null)throw Error('raw default');
 await page.getByTestId('chat-raw-events').locator('summary').click();if(await page.getByTestId('chat-raw-events').locator('pre').count()!==12)throw Error('raw count');await page.getByTestId('chat-raw-events').locator('summary').click();
 await page.getByTestId('chat-status').waitFor({state:'hidden'});const styles=[];
 for(const theme of ['dark','light'])for(const width of [1440,390]){
  await page.setViewportSize({width,height:900});
  if(await page.getByTestId('chat-shell').getAttribute('data-theme')!==theme)await page.getByTestId('chat-theme-toggle').click();
  await page.screenshot({path:`${dir}/events-${theme}-${width}.png`});
  styles.push({theme,width,values:await page.locator('.chat-event-group pre').first().evaluate(e=>{const s=getComputedStyle(e);return {fontSize:s.fontSize,lineHeight:s.lineHeight,color:s.color,whiteSpace:s.whiteSpace}})});
  await page.getByLabel('关闭执行详情').click();await page.getByRole('table').scrollIntoViewIfNeeded();
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('page overflow');
  styles.push({theme,width,table:await page.locator('th').first().evaluate(e=>{const s=getComputedStyle(e);return {padding:s.padding,border:s.border,background:s.backgroundColor,color:s.color}})});
  await page.screenshot({path:`${dir}/table-${theme}-${width}.png`});await page.getByTestId('chat-panel-toggle').click();
 }
 if(errors.length)throw Error(errors.join(','));fs.writeFileSync(dir+'/verification.json',JSON.stringify({mock:'synthetic API and events; real production Web bundle',screenshots:8,groups:5,rawEvents:12,pageErrors:errors,styles},null,2));console.log('PASS: groups, raw toggle, status, tables, 8 screenshots and computed styles');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
