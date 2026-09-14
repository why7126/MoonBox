const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs'),path=require('node:path');
const out=path.resolve('../../logs/req0026-modify');fs.mkdirSync(out,{recursive:true});
const base={current_user:{name:'验收账号'},workspaces:[{workspace_id:'space',name:'验证项目'}],selected_workspace_id:'space',snapshot_revision:'stable',stats:{total:4,requirements:1,bugs:1,standalone_changes:2,blocked:0},issues:[
{id:'REQ-0099',type:'requirement',title:'需求卡片',stage:'capture',owner:'产品',priority:'P2',documents:[]},
{id:'BUG-0099',type:'bug',title:'缺陷卡片',stage:'capture',owner:'产品',priority:'P2',documents:[]},
{id:'standalone-change',type:'change',title:'独立变更',stage:'capture',owner:'产品',priority:'P2',documents:[]},
{id:'duplicate-archive-change',type:'change',title:'重复归档',stage:'unknown',owner:'未分配',priority:'',documents:[]}]};
(async()=>{const browser=await chromium.launch({headless:true});const evidence=[];try{
for(const theme of ['dark','light'])for(const width of [1440,390]){
 const page=await browser.newPage({viewport:{width,height:1000}});const errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error(e.message);});
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/**',route=>{const u=new URL(route.request().url());const data=u.pathname.endsWith('/projects')?{...base,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]}:u.pathname.endsWith('/context')?base:{ready:false};return route.fulfill({json:{code:0,data}});});
 await page.goto('http://127.0.0.1:18135/tests/governance-board-preview.html');await expect(page.locator('.rc-card')).toHaveCount(3).catch(async e=>{console.error((await page.locator('body').innerText()).slice(0,1500));throw e;});
 await expect(page.locator('.rc-column')).toHaveCount(9);await expect(page.locator('.rc-unknown-changes')).toHaveCount(0);
 await expect(page.getByLabel('需求中心统计')).toContainText('全部对象3');
 const header=await page.locator('.rc-page-header').boundingBox(),stats=await page.locator('.rc-stats').boundingBox();if(header.y+header.height>stats.y+1)throw Error('header overlaps stats');
 const styles=await page.locator('.rc-card,.rc-board,.rc-board-wrap,.rc-data-diagnostics').evaluateAll(es=>es.map(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {selector:e.className,borderLeft:s.borderLeftColor,padding:s.padding,overflowX:s.overflowX,grid:s.gridTemplateColumns,width:r.width,left:r.left,right:r.right};}));
 const colors=styles.filter(s=>s.selector.startsWith('rc-card ')).map(s=>s.borderLeft);if(new Set(colors).size!==3)throw Error('type colors collide');
 await expect(page.locator('.rc-data-diagnostics')).not.toHaveAttribute('open','');await page.screenshot({path:path.join(out,`layout-${theme}-${width}.png`)});
 await page.locator('.rc-data-diagnostics summary').focus();await page.keyboard.press('Enter');await expect(page.locator('.rc-data-diagnostics')).toHaveAttribute('open','');await expect(page.getByText('duplicate-archive-change',{exact:true})).toBeVisible();
 await page.screenshot({path:path.join(out,`diagnostics-${theme}-${width}.png`)});await page.keyboard.press('Enter');await expect(page.locator('.rc-data-diagnostics')).not.toHaveAttribute('open','');
 await page.getByLabel('搜索治理对象',{exact:true}).fill('duplicate-archive-change');await expect(page.locator('.rc-card')).toHaveCount(0);await expect(page.getByLabel('需求中心统计')).toContainText('全部对象0');await expect(page.locator('.rc-data-diagnostics')).toBeVisible();
 await page.getByLabel('搜索治理对象',{exact:true}).fill('REQ-0099');await expect(page.locator('.rc-card')).toHaveCount(1);await expect(page.locator('.rc-data-diagnostics')).toHaveCount(0);
 if(errors.length)throw Error(errors.join('\n'));evidence.push({theme,width,styles,pageErrors:errors});await page.close();
}fs.writeFileSync(path.join(out,'styles.json'),JSON.stringify({boundary:'真实浏览器和组件，合成API夹具；非部署观察',evidence},null,2));console.log('4 viewport/theme cases passed');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
