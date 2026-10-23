const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
const out=path.resolve(__dirname,'../../../openspec/changes/fix-requirement-center-card-width-sprint-tag-wrap/evidence/acceptance/layout');
const base={sprint_option_details:[{id:'sprint-005',status:'planning',lifecycle_stage:'change'}],current_user:{name:'验收账号'},workspaces:[{workspace_id:'space',name:'验证项目'}],selected_workspace_id:'space',snapshot_revision:'stable',stats:{total:4,requirements:0,bugs:0,standalone_changes:4,blocked:0},issues:['capture','planning','review-ready','approved','sprint-planning','ready-dev','development','acceptance','done'].map((stage,index)=>({id:stage==='capture'?'REQ-8101':stage==='done'?'x'.repeat(80):'sample-'+stage+'-long-change-identifier-for-sprint-tag',type:['requirement','bug','change'][index%3],title:'卡片宽度与迭代标签布局样本',stage,sprint_id:'sprint-005',owner:'产品',priority:'',documents:['tasks.md','proposal.md','spec.md','design.md','trace.md'],document_entries:[{name:'tasks.md',type:'markdown',open_mode:'drawer',url:'/api/v1/requirement-center/changes/sample-'+stage+'/documents/tasks.md',capability:{readable:true,human_editable:false,task_toggle_only:false}}]}))};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const evidence=[];try{
for(const theme of ['dark'])for(const width of [1440,768]){
 const page=await browser.newPage({viewport:{width,height:900}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/v1/**',route=>{const u=new URL(route.request().url());return route.fulfill({json:{code:0,data:u.pathname.endsWith('/projects')?{...base,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]}:u.pathname.endsWith('/context')?base:u.pathname.endsWith('/tasks.md')?{content:'# 当前变更进度\n- [ ] 待完成',version:'test'}:{ready:false}}});});
 await page.goto('http://127.0.0.1:39035/tests/governance-board-preview.html');
 if(process.env.LAYOUT_BASELINE==='1')await page.addStyleTag({content:'.rc-board {grid-template-columns: repeat(9,320px)} .rc-sprint-tag {white-space:normal;flex-shrink:1}'});
 const stages=['capture','planning','review-ready','approved','sprint-planning','ready-dev','development','acceptance','done'];
 await expect(page.locator('.rc-card')).toHaveCount(9);
 const styles=[];
 for(const stage of stages){
 const col=page.locator(`[data-stage="${stage}"]`);await col.scrollIntoViewIfNeeded();
 const m=await col.evaluate(e=>{const c=e.querySelector('.rc-card'),id=e.querySelector('.rc-card-top strong'),tag=e.querySelector('.rc-sprint-tag');const r=x=>{const b=x.getBoundingClientRect();return {left:b.left,right:b.right,width:b.width}};let lines=0;if(tag){const range=document.createRange();range.selectNodeContents(tag);lines=new Set([...range.getClientRects()].map(x=>x.top)).size;}return {column:r(e),card:r(c),id:r(id),tag:tag?{...r(tag),lines,whiteSpace:getComputedStyle(tag).whiteSpace,shrink:getComputedStyle(tag).flexShrink}:null};});
 expect(m.column.width).toBeCloseTo(380,0);expect(m.id.right).toBeLessThanOrEqual(m.card.right);
 if(m.tag){expect(m.tag.lines).toBe(1);expect(m.tag.shrink).toBe('0');expect(m.id.right).toBeLessThanOrEqual(m.tag.left+1);expect(m.tag.right).toBeLessThanOrEqual(m.card.right);}
 styles.push({stage,...m});await page.screenshot({path:path.join(out,`${stage}-${width}.png`)});
 }
 const col=page.locator('[data-stage="capture"]');await col.scrollIntoViewIfNeeded();await col.getByRole('button',{name:'tasks.md',exact:true}).click();await expect(page.locator('.rc-drawer')).toBeVisible();await page.screenshot({path:path.join(out,`document-${width}.png`)});await page.keyboard.press('Escape');await expect(page.locator('.rc-drawer')).toHaveCount(0);
 const progress=page.locator('[data-stage="development"]');await progress.scrollIntoViewIfNeeded();await progress.getByRole('button',{name:'查看进度 →'}).click();await expect(page.locator('.rc-drawer')).toBeVisible();await page.screenshot({path:path.join(out,`progress-${width}.png`)});await page.keyboard.press('Escape');await expect(page.locator('.rc-drawer')).toHaveCount(0);
 await page.route('**/api/v1/requirement-center/context?**',r=>r.fulfill({json:{code:0,data:{...base,issues:[]}}}));await page.reload();await expect(page.locator('.rc-column-body.empty')).toHaveCount(9);await page.screenshot({path:path.join(out,`empty-${width}.png`)});
 if(errors.length)throw Error(errors.join('\n'));evidence.push({theme,viewport:width,styles,pageErrors:errors});await page.close();
}fs.writeFileSync(path.join(out,'styles.json'),JSON.stringify({boundary:'真实浏览器组件，合成 API 响应复现仓库样本解析结果；非部署观察',evidence},null,2));console.log('18 stage/viewport cases passed');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
