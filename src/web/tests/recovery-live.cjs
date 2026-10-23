const {chromium}=require('@playwright/test');const fs=require('fs');const path=require('path');
(async()=>{
const root=process.env.RECOVERY_LIVE_ROOT;if(!root?.startsWith('/private/tmp/moonbox-governance-live-'))throw Error('isolated root required');
const settings=JSON.parse(fs.readFileSync(path.join(root,'browser.json'))),oid=process.env.RECOVERY_SAMPLE||'REQ-9094-recovery-normal';
const browser=await chromium.launch({headless:true}),page=await browser.newPage({viewport:{width:1440,height:900}});let token;
page.on('response',async r=>{if(r.url().endsWith('/api/v1/auth/login')&&r.ok())token=(await r.json()).data.access_token;});
await page.goto(settings.url+'/login');await page.getByLabel('用户名',{exact:true}).fill('alice');await page.getByLabel('密码',{exact:true}).fill(settings.password);await page.getByRole('button',{name:'登录并开启宝盒'}).click();
for(let n=0;n<100&&!token;n++)await page.waitForTimeout(100);if(!token)throw Error('login failed');
const api=async(url,data)=>{for(let n=0;n<30;n++){const r=await page.request.fetch(settings.url+'/api/v1/chat'+url,{method:data?'POST':'GET',timeout:120000,headers:{Authorization:'Bearer '+token},...(data?{data}:{})});const b=await r.json();if(!data&&r.status()===503&&n<29){await page.waitForTimeout(1000);continue;}if(!r.ok())throw Error(JSON.stringify({path:url,status:r.status(),code:b.code,message:b.message}));return b.data;}};
const action=oid.startsWith('REQ')?'req-review':'bug-review',observationOnly=Boolean(process.env.RECOVERY_TURN_ID);
const existing=observationOnly?await api('/turns/'+process.env.RECOVERY_TURN_ID):null;
const session=existing?{conversation_id:existing.conversation_id}:await api('/object-sessions',{space_id:'space',repository_id:'moonbox-validation',object_id:oid,action,idempotency_key:oid});
await page.goto(settings.url+'/chat?conversation_id='+session.conversation_id+'&space_id=space');
const turn=existing||await api('/conversations/'+session.conversation_id+'/turns',{client_request_id:process.env.RECOVERY_REQUEST_KEY||'live-'+oid,prompt:`/${action} ${oid} --approve\n仅评审这个隔离样本，保留完整文档并迁移至review。除 status、updated_at、lifecycle、lifecycle_stage 外，主文档和 trace 的 frontmatter 必须与原准备基准 git HEAD 保持一致（包括 prototype_gate）；不能根据正文推测并改写其他元数据。若工作区保留上轮成果，只修复越界字段，保留其余原成果。先dry-run再正式Workflow Sync。不实施、不新建Issue/Change/Sprint；按授权跳过用量落盘。`});
console.log(JSON.stringify({sample:oid,conversation_id:session.conversation_id,turn_id:turn.id,event:observationOnly?'observing_existing':'started'}));
let result,interrupted=Boolean(existing&&oid.endsWith('-recovery')&&existing.status==='stopped');const until=Date.now()+900000;
while(Date.now()<until){result=await api('/turns/'+turn.id);if(!observationOnly&&oid.endsWith('-recovery')&&!interrupted&&fs.existsSync(path.join(root,'tail-observed.json'))){const tail=JSON.parse(fs.readFileSync(path.join(root,'tail-observed.json')));if(tail.conversation_id===session.conversation_id){if(process.env.RECOVERY_CRASH==='1'){
fs.writeFileSync(path.join(root,'recovery-restart-needed.json'),JSON.stringify({turn_id:turn.id,conversation_id:session.conversation_id,mode:'service_crash'}));console.log('actual model output observed; waiting for service crash/restart');
let restarted=false;for(let n=0;n<300;n++){const p=path.join(root,'recovery-restarted.json');if(fs.existsSync(p)&&JSON.parse(fs.readFileSync(p)).turn_id===turn.id){restarted=true;break;}await page.waitForTimeout(1000);}if(!restarted)throw Error('service crash/restart checkpoint timeout');interrupted=true;
}else{await api('/turns/'+turn.id+'/interrupt',{});interrupted=true;console.log('stop requested after model output');}}}if(['completed','failed','stopped'].includes(result.status))break;await page.waitForTimeout(2000);}
if(!observationOnly&&interrupted&&process.env.RECOVERY_WAIT_RESTART==='1'&&process.env.RECOVERY_CRASH!=='1'){
 fs.writeFileSync(path.join(root,'recovery-restart-needed.json'),JSON.stringify({turn_id:turn.id,conversation_id:session.conversation_id}));
 let restarted=false;
 for(let n=0;n<300;n++){const p=path.join(root,'recovery-restarted.json');if(fs.existsSync(p)&&JSON.parse(fs.readFileSync(p)).turn_id===turn.id){restarted=true;break;}await page.waitForTimeout(1000);}
 if(!restarted)throw Error('explicit isolated restart checkpoint timeout');
}
await page.waitForTimeout(3000);
const items=(await api('/conversations/'+session.conversation_id+'/governance-candidates')).items,candidate=items.find(c=>c.prepared_turn_id===turn.id||c.turn_id===turn.id);let operation=candidate?.recovery_operation_id?await api('/governance-operations/'+candidate.recovery_operation_id):null;
for(let n=0;n<60&&operation?.state==='active';n++){await page.waitForTimeout(1000);operation=await api('/governance-operations/'+operation.id);}
if(!observationOnly&&operation?.allowed_actions.includes('resume')&&interrupted){await page.reload();await page.getByTestId('recovery-resume').waitFor({timeout:120000});await page.getByTestId('recovery-resume').click();await page.getByTestId('recovery-confirm').click();for(let n=0;n<60;n++){operation=await api('/governance-operations/'+operation.id);if(operation.state==='completed')break;await page.waitForTimeout(1000);}}
await page.reload();await page.getByTestId('recovery-panel').waitFor({state:'visible',timeout:120000});await page.getByTestId('recovery-panel').scrollIntoViewIfNeeded();if(operation?.state==='completed')await page.getByTestId('recovery-business-state').filter({hasText:'业务已完成'}).waitFor({timeout:120000});const out=path.resolve('../../openspec/changes/add-governance-command-durable-recovery/evidence/live');fs.mkdirSync(out,{recursive:true});const previous=path.join(out,oid+'.json');if(fs.existsSync(previous)){const prior=JSON.parse(fs.readFileSync(previous));if(prior.turn_id!==turn.id){fs.renameSync(previous,path.join(out,oid+'-'+prior.turn_id+'.json'));const oldImage=path.join(out,oid+'.png');if(fs.existsSync(oldImage))fs.renameSync(oldImage,path.join(out,oid+'-'+prior.turn_id+'.png'));}}await page.getByTestId('recovery-panel').screenshot({path:path.join(out,oid+'.png')});
const finalCandidate=(await api('/conversations/'+session.conversation_id+'/governance-candidates')).items.find(c=>c.id===candidate?.id);
const restartHistory=path.join(root,'restart-history.json');const restart=fs.existsSync(restartHistory)?JSON.parse(fs.readFileSync(restartHistory)).find(r=>r.turn_id===turn.id):null;if(restart)interrupted=true;
const summary={interruption_mode:restart?.mode||null,evidence_kind:'observed_product',sample:oid,conversation_id:session.conversation_id,turn_id:turn.id,terminal:result.status,error_code:result.error_code,interrupted,candidate_state:finalCandidate?.state,operation};fs.writeFileSync(path.join(out,oid+'.json'),JSON.stringify(summary,null,2));console.log(JSON.stringify(summary));await browser.close();if(operation?.state!=='completed')process.exitCode=2;
})().catch(e=>{console.error(String(e.message).split('Call log:')[0].replace(/Bearer \S+/g,'Bearer [redacted]'));process.exit(1)});
