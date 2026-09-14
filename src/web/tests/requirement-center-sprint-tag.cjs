const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
const out=path.resolve('../../openspec/changes/add-requirement-center-change-visibility/evidence/sprint-tag');
const base={current_user:{name:'验收账号'},workspaces:[{workspace_id:'space',name:'验证项目'}],selected_workspace_id:'space',snapshot_revision:'stable',stats:{total:1,requirements:0,bugs:0,standalone_changes:1,blocked:0},issues:[{id:'build-api-standard',type:'change',title:'建立接口标准',stage:'done',sprint_id:'sprint-000',owner:'产品',priority:'',documents:[]}]};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true});const evidence=[];try{
for(const theme of ['dark','light']){
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/**',route=>{const u=new URL(route.request().url());return route.fulfill({json:{code:0,data:u.pathname.endsWith('/projects')?{...base,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]}:u.pathname.endsWith('/context')?base:{ready:false}}});});
 await page.goto('http://127.0.0.1:18135/tests/governance-board-preview.html');
 const card=page.locator('[data-issue-id="build-api-standard"]');await expect(card).toBeVisible();await card.scrollIntoViewIfNeeded();
 await expect(card.locator('.rc-sprint-tag')).toHaveText('sprint-000');
 const styles=await card.locator('.rc-sprint-tag').evaluate(e=>{const s=getComputedStyle(e);return {text:e.textContent,fontSize:s.fontSize,color:s.color,background:s.backgroundColor,display:s.display};});
 await page.screenshot({path:path.join(out,`done-${theme}-1440.png`)});
 if(errors.length)throw Error(errors.join('\n'));evidence.push({theme,viewport:1440,styles,pageErrors:errors});await page.close();
}fs.writeFileSync(path.join(out,'styles.json'),JSON.stringify({boundary:'真实浏览器组件，合成 API 响应复现仓库样本解析结果；非部署观察',evidence},null,2));console.log('2 theme cases passed');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
