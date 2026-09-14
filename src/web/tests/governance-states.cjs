const {chromium}=require('@playwright/test');const fs=require('node:fs'),path=require('node:path');
(async()=>{const browser=await chromium.launch();try{
 const page=await browser.newPage(),dir=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui'),samples=[];
 for(const state of ['pending','conflict','failed','recovery_blocked','applied'])for(const [theme,width,height] of [['dark',1440,1000],['light',1440,600],['light',390,844]]){
  await page.setViewportSize({width,height});await page.goto(`http://127.0.0.1:18122/tests/governance-preview.html?state=${state}`);
  await page.evaluate(theme=>{localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));dispatchEvent(new Event('moonbox.ui.preferences.changed'))},theme);
  await page.getByTestId('governance-result-preview').click();
  await page.screenshot({path:path.join(dir,`state-${state}-${theme}-${width}.png`)});
  samples.push(await page.locator('.pg-dialog').evaluate((el,args)=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return{...args,width:s.width,font:s.fontSize,background:s.backgroundColor,color:s.color,inside:r.left>=0&&r.right<=innerWidth,footerVisible:el.querySelector('footer').getBoundingClientRect().bottom<=innerHeight}}, {state,theme,viewport:[width,height]}));
 }
 fs.writeFileSync(path.join(dir,'state-styles.json'),JSON.stringify({synthetic:true,samples},null,2));if(samples.some(x=>!x.inside||!x.footerVisible))throw Error('viewport containment failure');console.log(JSON.stringify({screenshots:samples.length,containment:true}));
}finally{await browser.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
