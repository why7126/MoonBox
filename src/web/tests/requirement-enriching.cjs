const {chromium, expect} = require('@playwright/test');
const fs = require('node:fs'), path = require('node:path');
const out = path.resolve('../../logs/requirement-enriching-no-label');
const documents = ['capture.md','bug.md','trace.md','root-cause.md','workaround.md','acceptance.md'];
const longOwner = 'user_0123456789abcdef0123456789abcdef0123456789abcdef';
const base = {current_user:{name:'验收账号'}, workspaces:[{workspace_id:'space',name:'验证项目'}],selected_workspace_id:'space',snapshot_revision:'stable',stats:{total:2,requirements:0,bugs:2,standalone_changes:0,blocked:0},issues:['enriching','draft'].map((status,i)=>({id:'BUG-009'+i,type:'bug',title:'登录失效刷新未跳转登录页',owner:'产品团队',severity:'medium',source:'plan',stage:'planning',status,completion_hint:status==='enriching'?'根因尚未确认，请按根因分析文档补充可复核证据。':null,documents,updated_at:'26/09/30 15:20',action:{command:'/bug-complete BUG-009'+i+'-example',label:'完善 Bug',requires_choice:'completion'}}))};
(async()=>{
 base.issues.forEach(issue=>issue.owner=longOwner);
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch();const evidence=[];
 try {
  for(const width of [1440,390]){
   const page=await browser.newPage({viewport:{width,height:1000}});const requests=[],errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic'})));
   await page.route('**/api/**',route=>{
    const endpoint=new URL(route.request().url()).pathname;requests.push({endpoint,method:route.request().method(),body:route.request().postDataJSON()});
    if(endpoint.endsWith('/object-sessions'))return route.fulfill({json:{code:0,data:{conversation_id:'continued',object_id:'BUG-0090-example',action:'bug-complete'}}});
    if(endpoint.endsWith('/spaces'))return route.fulfill({json:{code:0,data:[{id:'space',name:'验证项目'}]}});
    if(endpoint.endsWith('/capabilities'))return route.fulfill({json:{code:0,data:{execution_ready:true,repositories:[{id:'repo',space_id:'space'}]}}});
    if(endpoint.endsWith('/conversations/continued'))return route.fulfill({json:{code:0,data:{id:'continued',space_id:'space',repository_id:'repo',title:'继续完善'}}});
    if(endpoint.includes('/chat/')&&!endpoint.endsWith('/projects'))return route.fulfill({json:{code:0,data:{items:[],primary:null,references:[]}}});
    const data=endpoint.endsWith('/projects')?{...base,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]}:endpoint.endsWith('/context')?base:endpoint.includes('/documents/')?{content:'# 登录失效根因分析\n\n待补充运行时证据。',version:'test'}:{};
    return route.fulfill({json:{code:0,data}});
   });
   await page.goto(`${process.env.REQUIREMENT_CENTER_BASE_URL || 'http://localhost:39002'}/requirements`);
   const card=page.locator('[data-issue-id="BUG-0090"]');await expect(card).toBeVisible();await card.scrollIntoViewIfNeeded();
   await expect(card.getByText('完善中',{exact:true})).toHaveCount(0);
   const owner=card.locator('.rc-owner-tag');
   await expect(owner).toHaveAttribute('title',longOwner);
   const ownerStyle=await owner.evaluate(el=>({right:el.getBoundingClientRect().right,parentRight:el.parentElement.getBoundingClientRect().right,whiteSpace:getComputedStyle(el).whiteSpace,textOverflow:getComputedStyle(el).textOverflow,overflow:getComputedStyle(el).overflow}));
   expect(ownerStyle.right).toBeLessThanOrEqual(ownerStyle.parentRight+1);
   expect(ownerStyle.whiteSpace).toBe('nowrap');expect(ownerStyle.textOverflow).toBe('ellipsis');expect(ownerStyle.overflow).toBe('hidden');
   await expect(card.getByRole('button',{name:'继续完善 →'})).toBeEnabled();
   const draftCard=page.locator('[data-issue-id="BUG-0091"]');
   await expect(draftCard.getByText('草稿',{exact:true})).toHaveCount(0);
   await expect(draftCard.locator('.rc-owner-tag')).toHaveText(longOwner);
   await expect(draftCard.locator('.rc-card-tags .rc-tag.medium')).toBeVisible();
   for(const name of ['root-cause.md','workaround.md','acceptance.md'])await expect(card.getByRole('button',{name,exact:true})).toBeVisible();
   const style=await card.getByTestId('issue-completion-hint').evaluate(el=>({width:el.clientWidth,scrollWidth:el.scrollWidth,fontSize:getComputedStyle(el).fontSize,lineHeight:getComputedStyle(el).lineHeight,color:getComputedStyle(el).color}));
   expect(style.scrollWidth).toBeLessThanOrEqual(style.width+1);
   await page.screenshot({path:path.join(out,`card-${width}.png`)});
   await card.getByRole('button',{name:'root-cause.md',exact:true}).click();
   await expect(page.getByRole('heading',{name:'登录失效根因分析',exact:true})).toBeVisible();
   expect(requests.some(r=>r.endpoint.includes('root-cause.md'))).toBe(true);
   expect(requests.filter(r=>r.method==='POST')).toHaveLength(0);
   await page.keyboard.press('Escape');
   await expect(page.locator('.rc-drawer')).toHaveCount(0);
   await card.getByRole('button',{name:'继续完善 →'}).click();
   await expect(page).toHaveURL(/conversation_id=continued/);
   expect(requests.find(r=>r.endpoint.endsWith('/object-sessions')).body.action).toBe('bug-complete');
   expect(errors).toHaveLength(0);evidence.push({width,style,ownerStyle,requests,errors});await page.close();
  }
  fs.writeFileSync(path.join(out,'evidence.json'),JSON.stringify({mode:'deployed-components-synthetic-api',evidence},null,2));
  console.log('Desktop/mobile enriching card, document access and no-write assertions passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
