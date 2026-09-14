// Explicit synthetic HTTP with real repository tasks plus targeted edge fixtures.
const {chromium,expect}=require('@playwright/test');const fs=require('node:fs');const path=require('node:path');
(async()=>{
const data=JSON.parse(fs.readFileSync(process.env.TASKS_FIXTURE,'utf8')).context;
const real=fs.readFileSync('../../openspec/changes/add-local-project-governance-loop/tasks.md','utf8');
const out=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');const browser=await chromium.launch({headless:true});const samples=[];let cases=0;
try{for(const [theme,width,height] of [['dark',1440,1000],['light',1440,1000],['dark',390,844]]){
const page=await browser.newPage({viewport:{width,height}});const errors=[],reads=[];let mode='real';page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test-token'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
await page.route('**/api/**',async route=>{const url=new URL(route.request().url());let result=data;
if(url.pathname.endsWith('/projects'))result={...data,projects:[{space_id:'space',repository_id:'moonbox',status:'connected',readonly:false}]};
else if(url.pathname.endsWith('/documents/tasks.md')){reads.push(url.pathname);await new Promise(r=>setTimeout(r,150));if(mode==='404')return route.fulfill({status:404,json:{detail:'missing'}});
let content=real;if(mode==='headings')content='# Tasks\n\n- [ ] 实现前置\n\n## 研发任务\n- [ ] 实现界面\n\n## 自动化测试\n- [ ] 回归验证\n\n## 人工验收\n- [ ] 人工签收';if(mode==='fallback')content='# Tasks\n\n- [ ] 人工验收当前任务\n\n## 验收返修记录\n## 人工验收旧章节';result={content,version:'a'.repeat(64)};}
else if(!url.pathname.endsWith('/context'))throw Error('unexpected request');await route.fulfill({json:{code:0,data:result}});
});
await page.goto('http://127.0.0.1:18122/tests/governance-board-preview.html');const card=page.locator('[data-issue-id="REQ-0022"]');await expect(card).toHaveCount(1);
for(const [m,label,found] of [['real','研发',true],['real','测试',true],['real','人工验收',false],['headings','研发',true],['headings','测试',true],['headings','人工验收',true],['fallback','人工验收',true],['404','测试',false]]){
mode=m;await card.getByRole('button',{name:new RegExp('^'+label+' ')}).click();const dialog=page.getByRole('dialog');await expect(dialog).toContainText('Markdown 加载中');await expect(page.getByTestId('tasks-drawer')).toHaveCount(0);
if(m==='404'){await expect(dialog).toContainText('tasks.md 不存在或已移动');await expect(dialog.getByTestId('markdown-rendered-preview')).toHaveCount(0);}
else if(!found){await expect(dialog.locator('[data-task-navigation]')).toContainText('未找到人工验收');await expect(dialog.getByTestId('markdown-rendered-preview')).toContainText('6.6');}
else{const target=dialog.locator('.rc-task-navigation-target');await expect(target).toHaveCount(1);await expect(target).toBeFocused();const sample=await target.evaluate(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return{text:el.textContent,top:r.top,bottom:r.bottom,outline:s.outline,fontSize:s.fontSize}});if(sample.bottom<0||sample.top>=height)throw Error('target outside viewport');samples.push({m,label,theme,width,...sample});if(m==='headings')await expect(target).toHaveAttribute('data-task-heading','true');if(m==='fallback')await expect(target).toHaveAttribute('data-task-item','true');}
await page.screenshot({path:path.join(out,`tasks-navigation-${m}-${label}-${theme}-${width}.png`)});cases++;await dialog.getByRole('button',{name:'关闭右侧抽屉',exact:true}).click();
}
await card.getByRole('button',{name:'tasks.md',exact:true}).click();await expect(page.getByRole('dialog').locator('[data-task-navigation]')).toHaveCount(0);
if(reads.some(url=>!url.includes('/changes/add-local-project-governance-loop/')))throw Error('incorrect source');if(errors.length)throw Error(errors.join('\n'));await page.close();
}
const prototype=await browser.newPage({viewport:{width:1440,height:1000}});
await prototype.goto('file://'+path.resolve('../../issues/requirements/review/REQ-0022-local-project-import-product-iteration/prototype/web/prototype.html'));
for(const focus of ['development','test','manual','missing']){await prototype.locator(`[data-task-focus="${focus}"]`).click();await expect(prototype.locator('#tasks-dialog')).toBeVisible();await expect(prototype.locator('#tasks-status')).toContainText(focus==='missing'?'未找到':'已定位');await prototype.screenshot({path:path.join(out,`tasks-navigation-prototype-${focus}.png`)});await prototype.getByRole('button',{name:'关闭任务文档'}).click();}await prototype.close();
fs.writeFileSync(path.join(out,'tasks-navigation-styles.json'),JSON.stringify({mode:'repository-and-synthetic-documents-synthetic-http',cases,samples},null,2));console.log(JSON.stringify({cases,errors:0}));}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
