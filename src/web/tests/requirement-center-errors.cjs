const {chromium,expect}=require('@playwright/test');
const fs=require('node:fs');const path=require('node:path');
const base=process.env.BUG_UI_URL||'http://127.0.0.1:18135/tests/governance-board-preview.html';
const output=path.resolve('../../logs/bug0016');fs.mkdirSync(output,{recursive:true});
const fixture={current_user:{name:'验收账号'},workspaces:[{workspace_id:'space',name:'本地验证项目'}],selected_workspace_id:'space',snapshot_revision:'same',stats:{total:1,requirements:1,bugs:0,blocked:0,drift:0},issues:[{id:'REQ-0099',type:'requirement',title:'加载失败后的恢复验证',stage:'capture',priority:'P2',owner:'产品',documents:['capture.md'],document_entries:[{name:'capture.md',type:'markdown',editable:true,url:'/api/v1/requirement-center/issues/REQ-0099-test/documents/capture.md'}],updated_at:'now'}]};
(async()=>{const browser=await chromium.launch({headless:true});const evidence=[];
try{for(const [theme,width,height] of [['dark',1440,1000],['light',1440,1000],['dark',390,844],['light',390,844]]){
 const context=await browser.newContext({viewport:{width,height},permissions:['clipboard-read','clipboard-write']});const page=await context.newPage();let failure=true,docFailure=true;const errors=[];let active=0,maxActive=0;
 page.on('pageerror',e=>errors.push(e.message));
 await page.addInitScript(theme=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收账号',access_token:'synthetic-test'}));localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},theme);
 await page.route('**/api/**',async route=>{const url=new URL(route.request().url());let data=fixture;let status=200;
 if(url.pathname.endsWith('/projects'))data={...fixture,projects:[{space_id:'space',repository_id:'repo',readonly:false,status:'connected'}]};
 else if(url.pathname.endsWith('/context')){active++;maxActive=Math.max(maxActive,active);await new Promise(r=>setTimeout(r,100));status=failure?503:200;active--;}
 else if(url.pathname.includes('/documents/')){status=docFailure?503:200;data={content:'# 恢复后的文档',version:'a'.repeat(64)};}
 else data={ready:false};
 await route.fulfill({status,headers:{'X-Request-ID':'browser-validation'},json:status===200?{code:0,data}:{code:2603,message:'safe',data:{kind:'source_invalid',request_id:'browser-validation'}}});});
 await page.goto(base);await expect(page.getByTestId('rc-error-retry')).toBeVisible();
 await page.screenshot({path:path.join(output,`error-${theme}-${width}.png`)});
 await page.getByTestId('rc-error-details-trigger').click();await expect(page.getByTestId('rc-error-details-dialog')).toBeVisible();
 const errorStyles=await page.locator('.rc-read-error,.rc-read-error h3,.rc-read-error p,.rc-read-error-actions button,.rc-error-backdrop').evaluateAll(es=>es.map(el=>{const s=getComputedStyle(el);return {selector:el.className||el.tagName,fontFamily:s.fontFamily,fontSize:s.fontSize,lineHeight:s.lineHeight,padding:s.padding,gap:s.gap,border:s.border,background:s.backgroundColor,color:s.color,position:s.position,zIndex:s.zIndex,overflow:s.overflow};}));
 const style=await page.locator('.rc-error-dialog,.rc-error-dialog h2,.rc-error-dialog-body,.rc-error-dialog footer button').evaluateAll(es=>es.map(el=>{const s=getComputedStyle(el),r=el.getBoundingClientRect();return {selector:el.className||el.tagName,font:s.fontFamily,fontSize:s.fontSize,lineHeight:s.lineHeight,padding:s.padding,gap:s.gap,border:s.border,background:s.backgroundColor,color:s.color,position:s.position,zIndex:s.zIndex,overflow:s.overflow,width:r.width,left:r.left,right:r.right};}));
 if(style[0].left<0||style[0].right>width)throw Error('dialog outside viewport');
 await page.screenshot({path:path.join(output,`details-${theme}-${width}.png`)});
 await page.getByTestId('rc-error-copy').click();await expect(page.getByText('已复制',{exact:true})).toBeVisible();
 const clipboard=await page.evaluate(()=>navigator.clipboard.readText());if(!clipboard.includes('browser-validation'))throw Error('copy missing request id');
 await page.keyboard.press('Escape');await expect(page.getByTestId('rc-error-details-trigger')).toBeFocused();
 failure=false;await page.getByTestId('rc-error-retry').click();await expect(page.getByText('加载失败后的恢复验证',{exact:true})).toBeVisible();
 failure=true;await page.getByRole('button',{name:'刷新需求中心',exact:true}).click();await expect(page.getByLabel('更新失败',{exact:true})).toBeVisible();await page.screenshot({path:path.join(output,`stale-${theme}-${width}.png`)});
 await page.getByRole('button',{name:/capture.md/}).click();await expect(page.getByTestId('rc-document-error-retry')).toBeVisible();await page.screenshot({path:path.join(output,`drawer-${theme}-${width}.png`)});
 await page.getByTestId('rc-document-error-details-trigger').click();await page.keyboard.press('Tab');await expect(page.getByTestId('rc-error-details-close')).toBeFocused();await page.keyboard.press('Shift+Tab');await expect(page.getByRole('button',{name:'关闭',exact:true})).toBeFocused();
 await page.keyboard.press('Escape');await expect(page.getByTestId('markdown-drawer')).toBeVisible();await expect(page.getByTestId('rc-document-error-details-trigger')).toBeFocused();
 docFailure=false;await page.getByTestId('rc-document-error-retry').click();await expect(page.getByRole('heading',{name:'恢复后的文档'})).toBeVisible();
 if(errors.length)throw Error(errors.join('\n'));if(maxActive!==1)throw Error('duplicate context');
 evidence.push({theme,width,height,style,errorStyles,maxActive,pageErrors:errors});await context.close();
}fs.writeFileSync(path.join(output,'ui-validation.json'),JSON.stringify({boundary:'真实浏览器与真实页面组件；合成HTTP错误/恢复，非实际部署',evidence},null,2));console.log(JSON.stringify(evidence.map(({theme,width,maxActive,pageErrors})=>({theme,width,maxActive,pageErrors}))));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
