const {chromium}=require(process.cwd()+'/node_modules/@playwright/test');
const fs=require('node:fs');
const origin=process.argv[2] || 'http://127.0.0.1:18112';
const evidenceDir=process.argv[3] || '../../openspec/changes/add-chat-workbench-codex/evidence/ui';
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 await page.goto(origin+'/chat'); await page.waitForLoadState('networkidle');
 if(new URL(page.url()).pathname!=='/login')throw Error('Unauthenticated Chat route must redirect to login');
 await page.addInitScript(()=>localStorage.setItem('moonbox.session',JSON.stringify({username:'视觉测试',started_at:'2026-09-08'})));
 await page.goto(origin+'/chat'); await page.waitForLoadState('networkidle');
 const dir=evidenceDir; fs.mkdirSync(dir,{recursive:true});
 const results=[];
 for(const [theme,width,height] of [['dark',1440,900],['light',1440,900],['light',1024,600],['light',390,844]]){
  await page.setViewportSize({width,height});
  if(theme==='light'&&await page.getByTestId('chat-shell').getAttribute('data-theme')==='dark')await page.getByTestId('chat-theme-toggle').click();
  if(width<1281&&await page.getByTestId('chat-execution-panel').count())await page.getByRole('button',{name:'关闭执行详情'}).click();
  await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  await page.screenshot({path:dir+`/skeleton-${theme}-${width}.png`,fullPage:true});
  const styles=await page.evaluate(()=>{
   const props=['width','height','gridTemplateColumns','backgroundColor','color','fontFamily','fontSize','lineHeight','padding','gap','borderRadius','overflow','position'];
   const selectors=['.chat-shell','.rc-sidebar','.rc-nav-item.active','.chat-composer','[data-testid="chat-send"]','.chat-execution-panel'];
   return Object.fromEntries(selectors.map(s=>{const e=document.querySelector(s);return [s,e?Object.fromEntries(props.map(p=>[p,getComputedStyle(e)[p]])):null]}));
  });
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  const send=await page.getByTestId('chat-send').boundingBox();
  if(overflow||!send||send.x+send.width>width||send.y+send.height>height)throw Error('Skeleton viewport failed: '+width);
  if(!await page.getByTestId('chat-send').isDisabled())throw Error('Send must be disabled');
  results.push({theme,width,height,overflow,sendVisible:true,styles});
 }
 fs.writeFileSync(dir+'/skeleton-computed.json',JSON.stringify(results,null,2));
 await page.setViewportSize({width:1440,height:900}); await page.goto(origin+'/dev/design-system'); await page.waitForLoadState('networkidle'); const baseline=await page.locator('.ds-preview').evaluate(e=>({fontFamily:getComputedStyle(e).fontFamily,fontSize:getComputedStyle(e).fontSize,lineHeight:getComputedStyle(e).lineHeight,button:[...e.querySelectorAll('button')].map(b=>({className:b.className,fontSize:getComputedStyle(b).fontSize,padding:getComputedStyle(b).padding,borderRadius:getComputedStyle(b).borderRadius}))}));fs.writeFileSync(dir+'/ds-baseline.json',JSON.stringify(baseline,null,2)); await browser.close(); console.log(JSON.stringify({screenshots:4,viewportChecks:'pass',sendDisabled:true,loginGuard:'pass'}));
})();
