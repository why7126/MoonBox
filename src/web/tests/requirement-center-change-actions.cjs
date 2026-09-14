const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
const out=path.resolve('../../openspec/changes/add-requirement-center-change-visibility/evidence/actions');
const base={current_user:{name:'验收账号'},workspaces:[{workspace_id:'space',name:'验证项目'}],selected_workspace_id:'space',snapshot_revision:'stable',stats:{total:4,requirements:0,bugs:0,standalone_changes:4,blocked:0},issues:['ready-dev','development','acceptance','done'].map(stage=>({id:'sample-'+stage,type:'change',title:'独立变更阶段按钮',stage,sprint_id:'sprint-005',owner:'产品',priority:'',documents:['tasks.md'],document_entries:[{name:'tasks.md',type:'markdown',open_mode:'drawer',url:'/api/v1/requirement-center/changes/sample-'+stage+'/documents/tasks.md',capability:{readable:true,human_editable:false,task_toggle_only:false}}]}))};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const evidence=[];try{
for(const theme of ['dark','light'])for(const width of [1440,390]){
 const page=await browser.newPage({viewport:{width,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/**',route=>{const u=new URL(route.request().url());return route.fulfill({json:{code:0,data:u.pathname.endsWith('/projects')?{...base,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]}:u.pathname.endsWith('/context')?base:u.pathname.endsWith('/tasks.md')?{content:'# 当前变更进度\n- [ ] 待完成',version:'test'}:{ready:false}}});});
 await page.goto('http://127.0.0.1:18135/tests/governance-board-preview.html');
 const card=page.locator('[data-issue-id="sample-ready-dev"]');await expect(card).toBeVisible();await card.scrollIntoViewIfNeeded();
 await expect(card.getByRole('button',{name:'开始开发 →'})).toBeDisabled();
 await expect(page.locator('[data-issue-id="sample-acceptance"]').getByRole('button',{name:'完成 / 归档 →'})).toBeDisabled();
 await expect(page.locator('[data-issue-id="sample-done"] footer button')).toHaveCount(0);
 const styles=await card.locator('footer .primary').evaluate(e=>{const s=getComputedStyle(e);return {fontSize:s.fontSize,color:s.color,padding:s.padding,disabled:e.disabled};});
 await page.screenshot({path:path.join(out,`final-${theme}-${width}.png`)});
 const progress=page.locator('[data-issue-id="sample-development"]');await progress.scrollIntoViewIfNeeded();await progress.getByRole('button',{name:'查看进度 →'}).click();
 await expect(page.getByRole('heading',{name:'当前变更进度'})).toBeVisible();await expect(page.getByRole('button',{name:'编辑',exact:true})).toHaveCount(0);
 await page.screenshot({path:path.join(out,`progress-${theme}-${width}.png`)});
 await page.keyboard.press('Escape');await expect(page.locator('.rc-drawer')).toHaveCount(0);
 if(errors.length)throw Error(errors.join('\n'));evidence.push({theme,viewport:width,styles,pageErrors:errors});await page.close();
}fs.writeFileSync(path.join(out,'styles.json'),JSON.stringify({boundary:'真实浏览器组件，合成 API 响应复现仓库样本解析结果；非部署观察',evidence},null,2));console.log('4 viewport/theme cases passed');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
