const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs');const path=require('node:path');
(async()=>{
const data=JSON.parse(fs.readFileSync(process.env.BOARD_CONTEXT,'utf8'));
const output=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');
const browser=await chromium.launch({headless:true});const samples=[];
try{
for(const [theme,width,height] of [['dark',1440,1000],['light',1440,1000],['dark',390,844]]){
 const page=await browser.newPage({viewport:{width,height}});let release;let gate=new Promise(r=>release=r);let reads=0;const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test-token'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/**',async route=>{
  const url=new URL(route.request().url());let response=data;
  if(url.pathname.endsWith('/projects'))response={...data,projects:[{space_id:'space',repository_id:'moonbox',status:'connected',readonly:false}]};
  else if(url.pathname.endsWith('/context')){reads++;await gate;response={...data,snapshot_revision:'loading-'+reads};}
  else throw Error('unexpected request '+url.pathname);
  await route.fulfill({json:{code:0,data:response}});
 });
 await page.goto('http://127.0.0.1:18122/tests/governance-board-preview.html');
 await expect(page.locator('.rc-loading-card')).toHaveCount(9);
 await expect(page.locator('.rc-state-panel')).toHaveCount(0);
 await expect(page.locator('.rc-empty-stage')).toHaveCount(0);
 await expect(page.locator('.rc-stats strong')).toHaveText(['','','','']);
 const measure=()=>page.locator('.rc-stats,.rc-toolbar,.rc-board,.rc-column-head,.rc-column').evaluateAll(es=>es.map(el=>{const r=el.getBoundingClientRect(),s=getComputedStyle(el);return{selector:el.className,top:r.top,height:r.height,fontSize:s.fontSize,padding:s.padding,background:s.backgroundColor};}));
 const before=await measure();await page.screenshot({path:path.join(output,`loading-${theme}-${width}.png`)});
 release();await expect(page.locator('.rc-card')).toHaveCount(data.issues.length);
 await expect(page.locator('.rc-loading-card')).toHaveCount(0);
 const after=await measure();const shifts=after.map((x,i)=>Math.abs(x.top-before[i].top));
 if(Math.max(...shifts)>1)throw Error('layout shift '+JSON.stringify({before,after,shifts}));
 const search=page.getByPlaceholder('搜索 ID、标题、文档或负责人');await search.fill('REQ-0022');
 gate=new Promise(r=>release=r);const old=reads;await page.getByRole('button',{name:'刷新需求中心',exact:true}).click();
 await expect.poll(()=>reads).toBeGreaterThan(old);
 await expect(page.locator('.rc-loading-card')).toHaveCount(0);await expect(page.locator('.rc-card')).toHaveCount(1);await expect(search).toHaveValue('REQ-0022');
 release();await expect(page.getByRole('button',{name:'刷新需求中心',exact:true})).not.toBeDisabled();
 if(errors.length)throw Error(errors.join('\n'));
 samples.push({theme,width,height,before,after,maxTopShift:Math.max(...shifts),errors});await page.close();
}
fs.writeFileSync(path.join(output,'loading-styles.json'),JSON.stringify({mode:'delayed-synthetic-http',samples},null,2));
console.log(JSON.stringify(samples.map(({theme,width,maxTopShift,errors})=>({theme,width,maxTopShift,errors}))));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
