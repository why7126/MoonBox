// Repository-derived data through synthetic HTTP; this does not observe a deployment.
const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const data=JSON.parse(fs.readFileSync(process.env.BOARD_CONTEXT,'utf8'));
 const output=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');
 const browser=await chromium.launch({headless:true});
 try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}});let reads=0;const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test-token'})));
 await page.route('**/api/**',async route=>{
  const url=new URL(route.request().url());let response=data;
  if(url.pathname.endsWith('/projects'))response={...data,projects:[{space_id:'space',repository_id:'moonbox',status:'connected',readonly:false}]};
  else if(url.pathname.endsWith('/context')){reads++;response={...data,snapshot_revision:'fixture-'+reads};}
  else throw Error('unexpected endpoint '+url.pathname);
  await route.fulfill({json:{code:0,data:response}});
 });
 await page.goto((process.env.BOARD_URL||'http://127.0.0.1:18122')+'/tests/governance-board-preview.html');
 await expect(page.getByText('REQ-0022',{exact:true})).toHaveCount(1);
 await expect(page.getByTestId('project-binding')).toHaveCount(0);
 await expect(page.locator('.rc-card')).toHaveCount(38);
 await expect(page.locator('[data-stage="done"] .rc-card')).toHaveCount(34);
 await expect(page.locator('[data-stage="done"] .rc-blocked')).toHaveCount(0);
 await expect(page.locator('[data-stage="acceptance"] .rc-card')).toHaveCount(4);
 await expect(page.locator('[data-stage="ready-dev"] .rc-card')).toHaveCount(0);
 const samples=[];
 for(const theme of ['dark','light']){
  await page.evaluate(theme=>{localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));dispatchEvent(new Event('moonbox.ui.preferences.changed'));},theme);
  await expect(page.locator('main.requirement-center')).toHaveAttribute('data-theme',theme);
  samples.push(await page.locator('.rc-content').evaluate(el=>{const s=getComputedStyle(el);return {theme:document.querySelector('main').dataset.theme,gridTemplateRows:s.gridTemplateRows,gap:s.gap,overflow:s.overflow,children:[...el.children].map(c=>({class:c.className,top:c.getBoundingClientRect().top,height:c.getBoundingClientRect().height}))};}));
  await page.screenshot({path:path.join(output,'modify-board-'+theme+'-1440.png'),fullPage:true});
 }
 await page.locator('.rc-board-wrap').evaluate(el=>el.scrollLeft=el.scrollWidth);
 await page.screenshot({path:path.join(output,'modify-board-completed-1440.png'),fullPage:true});
 const search=page.getByPlaceholder('搜索 ID、标题、文档或负责人');await search.fill('REQ-0022');
 await expect(page.locator('.rc-card')).toHaveCount(1);
 const before=reads;await page.getByRole('button',{name:'刷新需求中心',exact:true}).click();
 await expect.poll(()=>reads).toBeGreaterThan(before);await expect(search).toHaveValue('REQ-0022');
 await page.screenshot({path:path.join(output,'modify-board-filter-refresh.png'),fullPage:true});
 await search.fill('');await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(output,'modify-board-mobile.png'),fullPage:true});
 samples.push(await page.getByRole('button',{name:'刷新需求中心',exact:true}).evaluate(el=>{const s=getComputedStyle(el);return{selector:'refresh',fontSize:s.fontSize,padding:s.padding,title:el.title,disabled:el.disabled};}));
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(output,'modify-board-styles.json'),JSON.stringify({mode:'synthetic-http-repository-data',stats:data.stats,stages:data.issues.reduce((a,i)=>(a[i.stage]=(a[i.stage]||0)+1,a),{}),reads,errors,samples},null,2));
 console.log(JSON.stringify({stats:data.stats,reads,errors,visual:'1440 dark/light; 390; filter and refresh'}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
