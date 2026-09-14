const {chromium}=require('@playwright/test');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 const dir=path.resolve('../../openspec/changes/add-local-project-governance-loop/evidence/ui');fs.mkdirSync(dir,{recursive:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:18122/tests/governance-preview.html');
 await page.getByTestId('governance-result-preview').waitFor();
 await page.screenshot({path:path.join(dir,'skeleton-chat-dark.png'),fullPage:true});
 await page.getByTestId('governance-result-preview').click();
 const samples=[];
 for(const selector of ['.rc-sidebar','[data-testid=chat-project-status]','.pg-dialog','.pg-dialog-body','.pg-dialog footer']){
   samples.push(await page.locator(selector).evaluate((el)=>{const s=getComputedStyle(el);return{selector:el.className,width:s.width,fontSize:s.fontSize,lineHeight:s.lineHeight,padding:s.padding,gap:s.gap,background:s.backgroundColor,color:s.color,overflow:s.overflow,position:s.position};}));
 }
 await page.screenshot({path:path.join(dir,'skeleton-preview-dark.png')});
 await page.keyboard.press('Escape');
 if(await page.locator('.pg-dialog').evaluate(el=>el.open))throw Error('escape did not close');
 if(!await page.getByTestId('governance-result-preview').evaluate(el=>el===document.activeElement))throw Error('focus not restored');
 await page.evaluate(()=>{localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme:'light'}));dispatchEvent(new Event('moonbox.ui.preferences.changed'))});
 await page.getByTestId('governance-result-preview').click();
 await page.screenshot({path:path.join(dir,'skeleton-preview-light.png')});
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(dir,'skeleton-preview-mobile.png')});
 await page.setViewportSize({width:1440,height:480});
 await page.screenshot({path:path.join(dir,'preview-low-viewport.png')});
 if(!await page.getByTestId('governance-apply-close').isVisible())throw Error('close inaccessible');
 await page.getByTestId('governance-apply-close').click();
 await page.getByTestId('governance-result-preview').click();
 await page.mouse.click(2,2);
 if(await page.locator('.pg-dialog').evaluate(el=>el.open))throw Error('backdrop did not close');
 await page.setViewportSize({width:1440,height:1000});
 await page.goto('http://127.0.0.1:18122/tests/governance-preview.html?page=requirements&mock=workflow');
 await page.locator('.rc-stats').waitFor();
 await page.screenshot({path:path.join(dir,'skeleton-requirements-light.png'),fullPage:true});
 fs.writeFileSync(path.join(dir,'skeleton-styles.json'),JSON.stringify({mock:true,viewport:[1440,1000],samples,errors},null,2));
 console.log(JSON.stringify({errors,samples}));await browser.close();if(errors.length)process.exitCode=1;
})();
