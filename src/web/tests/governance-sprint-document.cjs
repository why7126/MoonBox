// Associated Sprint document: real repository aggregation and synthetic HTTP.
const {chromium,expect}=require('@playwright/test');const fs=require('node:fs');const path=require('node:path');
(async()=>{
const fixture=JSON.parse(fs.readFileSync(process.env.SPRINT_FIXTURE,'utf8')),data=fixture.context;
const out=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');const browser=await chromium.launch({headless:true});const samples=[];
try{for(const [theme,width,height] of [['dark',1440,1000],['light',1440,1000],['dark',390,844]]){
const page=await browser.newPage({viewport:{width,height}});const errors=[],reads=[];let missing=false;
page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test-token'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
await page.route('**/api/**',async route=>{const url=new URL(route.request().url());let result=data;
 if(url.pathname.endsWith('/projects'))result={...data,projects:[{space_id:'space',repository_id:'moonbox',status:'connected',readonly:false}]};
 else if(fixture.documents[url.pathname]){reads.push(url.pathname);if(missing)return route.fulfill({status:404,json:{detail:'文档不存在或已移动'}});result={content:fixture.documents[url.pathname],version:'a'.repeat(64)};}
 else if(!url.pathname.endsWith('/context'))throw Error('unexpected request '+url.pathname);
 await route.fulfill({json:{code:0,data:result}});
});
await page.goto('http://127.0.0.1:18122/tests/governance-board-preview.html');
for(const id of ['BUG-0014']){
 const card=page.locator(`[data-issue-id="${id}"]`);await expect(card).toHaveCount(1);
 await expect(card.getByRole('button',{name:'sprint.md',exact:true})).toHaveCount(1);
 await expect(card.locator('.rc-blocked')).toHaveCount(0);
 await expect(card.getByRole('button',{name:/Change 实施记录|需求追踪|缺陷追踪/})).toHaveCount(0);
 await card.getByRole('button',{name:'sprint.md',exact:true}).click();const dialog=page.getByRole('dialog');
 await expect(dialog.locator('.rc-drawer-crumb')).toHaveText(id+'·sprint.md');
 await expect(dialog.getByRole('button',{name:'编辑',exact:true})).toHaveCount(0);
 await expect(dialog.getByTestId('markdown-rendered-preview')).not.toBeEmpty();
 const style=await dialog.locator('.rc-drawer-crumb').evaluate(el=>{const s=getComputedStyle(el);return{fontSize:s.fontSize,width:s.width,overflowWrap:s.overflowWrap}});samples.push({id,theme,width,style});
 await page.screenshot({path:path.join(out,`sprint-document-${id}-${theme}-${width}.png`)});
 await dialog.getByRole('button',{name:'关闭右侧抽屉',exact:true}).click();
}
missing=true;await page.locator('[data-issue-id="BUG-0014"]').getByRole('button',{name:'sprint.md',exact:true}).click();
await expect(page.getByRole('dialog')).toContainText(/文档.*(不存在|移动|读取失败)/);
if(reads.some(url=>url.includes('/changes/')))throw Error('Incorrect Sprint source');
await page.screenshot({path:path.join(out,`sprint-document-missing-${theme}-${width}.png`)});
if(errors.length)throw Error(errors.join('\n'));await page.close();
 }const proto=await browser.newPage({viewport:{width:1440,height:1000}});await proto.goto('file://'+path.resolve('../../issues/requirements/review/REQ-0022-local-project-import-product-iteration/prototype/web/prototype.html'));await proto.locator('#sprint-doc').click();await expect(proto.locator('#trace-title')).toHaveText('sprint.md');await expect(proto.locator('#trace-source')).toContainText('关联 Sprint');await proto.screenshot({path:path.join(out,'sprint-document-prototype.png')});await proto.close();fs.writeFileSync(path.join(out,'sprint-document-styles.json'),JSON.stringify({mode:'repository-documents-synthetic-http',samples,missingCases:3},null,2));console.log(JSON.stringify({cases:6,errors:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
