const {chromium}=require('@playwright/test');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
	 const browser=await chromium.launch({headless:true});
	 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
	 const base=process.env.CAPTURE_SKELETON_BASE||'http://127.0.0.1:5189';
	 const dir=path.resolve(__dirname,'../../../openspec/changes/add-capture-multimodal-candidate-review/evidence');fs.mkdirSync(dir,{recursive:true});const results=[];
	 for(const [width,height,theme,step] of [[1440,1000,'dark','input'],[1440,1000,'light','input'],[390,844,'light','input'],[1440,1000,'dark','result'],[1440,1000,'light','result'],[390,844,'light','result']]){
	  await page.setViewportSize({width,height});await page.goto(`${base}/tests/fixtures/capture-skeleton.html?theme=${theme}&step=${step}`);
	  await page.getByTestId(step==='result'?'capture-result-body':'capture-md-editor').waitFor();await page.evaluate(()=>document.fonts.ready);
	  const selectors=step==='result'?['.capture-workspace','.capture-result','.capture-resultcard','.capture-result-badge','.capture-idempotent','.capture-doneicon','.capture-progress strong']:['.capture-workspace','.capture-material-drawer','.capture-editor-panel textarea','.capture-material-chip','.capture-input-submit','.capture-kicker','.capture-progress strong'];
	  const styles=await page.evaluate((selectors)=>selectors.map(selector=>{const el=document.querySelector(selector),s=getComputedStyle(el),r=el.getBoundingClientRect();return {selector,width:r.width,height:r.height,padding:s.padding,font:s.font,fontSize:s.fontSize,color:s.color,background:s.backgroundColor,overflow:s.overflow}}),selectors);
	  if(styles[0].width>901)throw Error('workspace too wide');if(step==='input'&&width===1440&&styles[1].width<700)throw Error('material drawer width');
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('horizontal overflow');
  await page.screenshot({path:path.join(dir,`skeleton-${step}-${width}-${theme}.png`),fullPage:true});results.push({width,height,theme,step,styles});
 }
 fs.writeFileSync(path.join(dir,'skeleton-styles.json'),JSON.stringify({fixture:true,errors,results},null,2));await browser.close();if(errors.length)throw Error(errors.join('\n'));console.log('Skeleton: input/result 1440px dark/light and 390px passed; synthetic fixture, no API calls.');
})().catch(e=>{console.error(e.message);process.exit(1)});
