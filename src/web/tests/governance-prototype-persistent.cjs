// Associated Sprint documents remain visible across active and archived cards.
const {chromium,expect}=require('@playwright/test');const fs=require('node:fs');const path=require('node:path');
(async()=>{
const fixture=JSON.parse(fs.readFileSync(process.env.PERSISTENT_FIXTURE,'utf8')),data=fixture.context;
for(const issue of data.issues){if(issue.type==='requirement'){for(const part of ['admin','web']){const name=`prototype/${part}/prototype.html`;issue.documents.push(name);issue.document_entries.push({name,type:'html',label:`原型 · ${part}/prototype.html`,open_mode:'new-tab',url:`/api/v1/requirement-center/issues/${issue.id}/documents/${name}/preview`});}}}
for(const issue of data.issues){issue.updated_at=issue.id==='BUG-0001'?'更新时间未知':'26/09/12 07:03';}
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
for(const id of ['REQ-0022','BUG-0014','REQ-0001','BUG-0001']){
 const name='sprint.md';
 const card=page.locator(`[data-issue-id="${id}"]`);await expect(card).toHaveCount(1);
 await expect(card.locator('.rc-updated')).toHaveText(id==='BUG-0001'?'更新时间未知':'更新 26/09/12 07:03');
 const footerGeometry=await card.locator('footer').evaluate(el=>{const t=el.querySelector('.rc-updated').getBoundingClientRect(),a=el.querySelector('.rc-card-actions').getBoundingClientRect();return{overlap:t.left<a.right&&t.right>a.left&&t.top<a.bottom&&t.bottom>a.top,whiteSpace:getComputedStyle(el.querySelector('.rc-updated')).whiteSpace};});
 if(footerGeometry.overlap)throw Error('time overlaps actions');samples.push({id,theme,width,footerGeometry});
 await expect(card.locator('.rc-docs button').first()).toHaveText(id.startsWith('REQ-')?'requirement.md':'bug.md');
 await expect(card.getByRole('button',{name:name,exact:true})).toHaveCount(1);
 await expect(card.getByRole('button',{name:/Change 实施记录|需求追踪|缺陷追踪/})).toHaveCount(0);
 await expect(card.locator('.rc-doc-group').first().locator('button')).toHaveText([...(id.startsWith('REQ-')?['requirement.md','原型 · admin/prototype.html','原型 · web/prototype.html']:['bug.md']),'sprint.md','trace.md']);
 const groupStyles=await card.locator('.rc-doc-group').evaluateAll(els=>els.map(el=>{const s=getComputedStyle(el);return{gap:s.gap,borderTopWidth:s.borderTopWidth,marginTop:s.marginTop,paddingTop:s.paddingTop,width:s.width,scrollWidth:el.scrollWidth,clientWidth:el.clientWidth}}));
 if(groupStyles.some((s,i)=>s.borderTopWidth!=='0px'||s.paddingTop!=='0px'||s.marginTop!==(i?'4px':'0px')))throw Error('compact group spacing mismatch');
 if(groupStyles.some(s=>s.scrollWidth>s.clientWidth+1))throw Error('document group overflow');
 samples.push({id,theme,width,groupStyles});
 await card.locator("footer").evaluate(el=>el.scrollIntoView({block:"center",inline:"center"}));await page.screenshot({path:path.join(out,`prototype-persistent-card-${id}-${theme}-${width}.png`)});
 await card.getByRole('button',{name:name,exact:true}).click();const dialog=page.getByRole('dialog');
 await expect(dialog.locator('.rc-drawer-crumb')).toHaveText(id+'·'+name);
 await expect(dialog.getByRole('button',{name:'编辑',exact:true})).toHaveCount(0);
 await expect(dialog.getByTestId('markdown-rendered-preview')).not.toBeEmpty();
 const style=await dialog.locator('.rc-drawer-crumb').evaluate(el=>{const s=getComputedStyle(el);return{fontSize:s.fontSize,width:s.width,overflowWrap:s.overflowWrap}});samples.push({id,theme,width,style});
 await page.screenshot({path:path.join(out,`prototype-persistent-${id}-${theme}-${width}.png`)});
 await dialog.getByRole('button',{name:'关闭右侧抽屉',exact:true}).click();
}
missing=true;await page.locator('[data-issue-id="REQ-0022"]').getByRole('button',{name:'sprint.md',exact:true}).click();
await expect(page.getByRole('dialog')).toContainText(/(不存在|已移动|读取失败)/);
if(reads.some(url=>url.includes('/changes/')))throw Error('Change trace fallback');
await page.screenshot({path:path.join(out,`prototype-persistent-missing-${theme}-${width}.png`)});
if(errors.length)throw Error(errors.join('\n'));await page.close();
}const proto=await browser.newPage({viewport:{width:1440,height:1000}});await proto.goto('file://'+path.resolve('../../issues/requirements/review/REQ-0022-local-project-import-product-iteration/prototype/web/prototype.html'));await proto.locator('#sprint-doc').click();await expect(proto.locator('#trace-dialog')).toBeVisible();await proto.screenshot({path:path.join(out,'prototype-persistent-prototype.png')});await proto.close();fs.writeFileSync(path.join(out,'prototype-persistent-styles.json'),JSON.stringify({mode:'repository-documents-synthetic-http',samples,missingCases:3},null,2));console.log(JSON.stringify({cases:15,errors:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
