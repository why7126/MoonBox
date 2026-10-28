import {chromium} from '@playwright/test';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1440,height:900}});
 const requests=[],timeline=[];
 page.on('response',async r=>{
  if(r.url().includes('completion-verification')){
   const body=await r.json();requests.push(r.request().method());
   timeline.push({elapsed_ms:Date.now()-start,state:body.data?.state,queue:body.data?.auto_verification?.state});
  }
 });
 const start=Date.now();
 await page.goto(process.env.CHAT_BROWSER_URL);
 await page.getByTestId('state').filter({hasText:'verification_waiting'}).waitFor();
 await page.getByTestId('state').filter({hasText:'validated'}).waitFor({timeout:20000});
 assert.equal(await page.getByTestId('answer').textContent(),'重复措辞。重复措辞。');
 assert(requests.length>=2&&requests.length<=4);
 assert(requests.every(x=>x==='GET'));
 await page.screenshot({path:process.env.CHAT_BROWSER_SCREENSHOT});
 console.log(JSON.stringify({viewport:'1440x900',requests:requests.length,post_count:0,timeline,answer_copies:1,legitimate_repeated_phrases:2}));
}finally{await browser.close();}
