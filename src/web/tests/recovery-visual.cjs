const {chromium}=require('@playwright/test');const fs=require('fs');const path=require('path');
(async()=>{
const output=path.resolve('../../openspec/changes/add-governance-command-durable-recovery/evidence/visual');fs.mkdirSync(output,{recursive:true});
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:900}});let mode='recoverable',posts=0;
const original={id:'isolated-operation',object_id:'REQ-9000-isolated',action:'req-review',stage:'validation',state:'waiting',version:4,execution_terminal:'stopped',reason_code:null,allowed_actions:['refresh','resume','evidence'],auto_retry_count:3,manual_count:0,recovery_expires_at:'2026-10-26T00:00:00Z',candidate_id:'isolated-candidate',application_id:null};
await page.route('**/api/v1/chat/governance-operations/**',async route=>{
if(route.request().method()==='POST'){posts++;await new Promise(r=>setTimeout(r,700));return route.fulfill({json:{data:{state:'claimed'}}});}
const data={...original};if(mode==='stale'){data.version=5;}if(mode==='completed'){Object.assign(data,{state:'completed',stage:'complete',allowed_actions:['refresh','evidence']});}if(mode==='expired'){Object.assign(data,{reason_code:'recovery_expired',allowed_actions:['refresh','evidence','regenerate']});}if(mode==='blocked'){Object.assign(data,{reason_code:'binding_changed',allowed_actions:['refresh','evidence']});}return route.fulfill({json:{data}});
});
await page.goto('http://127.0.0.1:5197/tests/recovery-preview.html');await page.getByTestId('recovery-resume').waitFor();
const shot=async name=>page.screenshot({path:path.join(output,name+'.png')});await shot('recoverable-1440');await page.getByTestId('recovery-resume').click();await shot('confirmation-1440');
const styles=[];for(const selector of ['recovery-panel','recovery-resume-dialog','recovery-resume'])styles.push(await page.getByTestId(selector).evaluate((e,selector)=>{const s=getComputedStyle(e);return {selector,width:e.getBoundingClientRect().width,font:s.fontSize,background:s.backgroundColor,maxHeight:s.maxHeight,overflow:s.overflow,border:s.borderRadius}},selector));
await page.getByTestId('recovery-confirm').click();await shot('submitting-1440');await page.getByTestId('recovery-resume-dialog').waitFor({state:'hidden'});if(posts!==1)throw Error('duplicate post');
await page.getByTestId('recovery-resume').click();mode='stale';await page.getByText('状态已变化，请关闭后重新确认。').waitFor();if(!await page.getByTestId('recovery-confirm').isDisabled())throw Error('stale confirmation enabled');await shot('stale-confirmation-1440');await page.keyboard.press('Escape');
for(const next of ['completed','blocked','expired']){mode=next;await page.getByTestId('recovery-refresh').click();await page.waitForTimeout(150);await shot(next+'-1440');}
mode='recoverable';await page.setViewportSize({width:390,height:844});await page.reload();await page.getByTestId('recovery-resume').click();await shot('confirmation-390');
const narrow=await page.getByTestId('recovery-resume-dialog').evaluate(e=>({width:e.getBoundingClientRect().width,viewport:innerWidth,scroll:document.documentElement.scrollWidth}));if(narrow.width>358.5||narrow.scroll>390)throw Error('narrow overflow');
await page.keyboard.press('Escape');await page.getByTestId('recovery-resume-dialog').waitFor({state:'hidden'});if(await page.evaluate(()=>document.activeElement?.getAttribute('data-testid'))!=='recovery-resume')throw Error('focus not restored');
await page.getByTestId('recovery-reason').evaluate(e=>{e.textContent='项目绑定与原成果版本需要重新核验，已保留原始状态和证据。'.repeat(12)});await shot('long-reason-390');
await page.setViewportSize({width:1440,height:900});await page.evaluate(()=>document.documentElement.dataset.theme='light');await shot('light-1440');
fs.writeFileSync(path.join(output,'computed-style.json'),JSON.stringify({evidence_kind:'synthetic_component',styles,narrow,posts,keyboard:'passed'},null,2));await browser.close();console.log('10 screenshots; single submit; keyboard and layout passed (synthetic component)');
})().catch(e=>{console.error(e.message);process.exit(1)});
