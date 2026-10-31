// Explicit synthetic browser fixture. Real components and API; no model invocation.
import {useEffect,useState,useRef} from 'react';
import {createRoot} from 'react-dom/client';
import {ConversationMessages} from '../src/components/chat/ConversationMessages';
import {RecoveryOperationPanel} from '../src/components/chat/RecoveryOperationPanel';
import {ExecutionPanel} from '../src/components/chat/ExecutionPanel';
import '../src/styles/globals.css';
import '../src/styles/chat-workbench.css';
localStorage.setItem('moonbox.session',JSON.stringify({username:'synthetic',access_token:'synthetic-fixture-only'}));
const cacheMode=new URLSearchParams(location.search).get('cache')==='no-store'?'no-store':'default';
if(cacheMode==='no-store'){const original=window.fetch.bind(window);window.fetch=(input,init)=>original(input,{...init,cache:'no-store'});}
type Sample={id:string;label:string;turns:number;events:number};
function App(){
 const [slow,setSlow]=useState(false),[nextState,setNextState]=useState("running");
 const [samples,setSamples]=useState<Sample[]>([]),[index,setIndex]=useState(0),[mounted,setMounted]=useState(false),[visible,setVisible]=useState(false),[round,setRound]=useState(0),[metrics,setMetrics]=useState(''),[focus,setFocus]=useState('');
 useEffect(()=>{fetch('/api/fixture/history-scenes').then(r=>r.json()).then(setSamples);},[]);
 useEffect(()=>{
  if(!mounted)return;
  let body:number|null=null,status:number|null=null;const start=performance.now();
  const observe=()=>{
   if(body===null && document.querySelector('.chat-message-bubble')?.textContent)body=performance.now()-start;
   const states=[...document.querySelectorAll('[data-testid="turn-status-trigger"]')];
   if(status===null && states.length===samples[index]?.turns && states.every(e=>e.textContent?.includes('已完成')))status=performance.now()-start;
  };
  const observer=new MutationObserver(observe);observer.observe(document.body,{childList:true,subtree:true});observe();
  const measure=()=>{
   observe();
   const entries=performance.getEntriesByType('resource') as PerformanceResourceTiming[];
   const lanes:Record<string,PerformanceResourceTiming[]>={};
   const grouped:Record<string,{count:number;bytes:number;duration:number[];waiting:number[];queue_connect:number[];same_key_peak:number}>={};
   for(const entry of entries){const url=new URL(entry.name);if(!url.pathname.startsWith('/api/v1/chat/'))continue;
    const name=url.pathname.replace(/\/turns\/[^/]+/,'/turns/ROUND').replace(/\/conversations\/[^/]+/,'/conversations/CONVERSATION')+url.search;
    const item=grouped[name]??={count:0,bytes:0,duration:[],waiting:[],queue_connect:[],same_key_peak:0};item.count++;item.bytes+=entry.transferSize;item.duration.push(Math.round(entry.duration));item.waiting.push(Math.round(entry.responseStart-entry.requestStart));item.queue_connect.push(Math.round(entry.requestStart-entry.fetchStart));
    const lane=lanes[entry.name]??=[];lane.push(entry);
    const marks=lane.flatMap(e=>[[e.startTime,1],[e.responseEnd,-1]]).sort((a,b)=>a[0]-b[0]||a[1]-b[1]);let active=0,peak=0;for(const [,delta] of marks){active+=delta;peak=Math.max(peak,active);}item.same_key_peak=Math.max(item.same_key_peak,peak);
   }
   setMetrics(JSON.stringify({cache:cacheMode,sample:samples[index]?.label,body_ms:body&&Math.round(body),status_ms:status&&Math.round(status),elapsed_ms:Math.round(performance.now()-start),requests:grouped},null,2));
  };
  const timer=setInterval(measure,250);return()=>{clearInterval(timer);observer.disconnect();};
 },[mounted,round,index,samples]);
 const latest=useRef(metrics);latest.current=metrics;
 const [records,setRecords]=useState<unknown[]>([]),[sweeping,setSweeping]=useState(false);
 const sweep=async()=>{
  setSweeping(true);setRecords([]);const collected:unknown[]=[];
  for(const sampleIndex of [0,1])for(let repeat=1;repeat<=3;repeat++)for(const visit of ['first','revisit']){
   setMounted(false);setIndex(sampleIndex);setVisible(false);await new Promise(r=>setTimeout(r,100));
   performance.clearResourceTimings();setMounted(true);setRound(v=>v+1);
   await new Promise(r=>setTimeout(r,2000));
   collected.push({...JSON.parse(latest.current||'{}'),repeat,visit});setRecords([...collected]);
  }
  setSweeping(false);
 };
 const sample=samples[index];
 return <main className="chat-shell" style={{display:'block',padding:24,overflow:'auto',height:'100vh'}}>
 <h1>BUG-0058 隔离浏览器验收</h1><p>合成历史 · 真实组件 / API · 无模型调用 · 不写产品数据 · 接口缓存 {cacheMode}</p>
 <button onClick={()=>setSlow(v=>!v)}>切换五秒恢复样本</button>{slow&&<RecoveryOperationPanel operationId="synthetic-slow" onDraft={()=>{}}/>}
 <label>样本<select aria-label="样本" value={index} onChange={e=>{setMounted(false);setIndex(Number(e.target.value));setVisible(false);}}>{samples.map((s,i)=><option key={s.id} value={i}>{s.label}</option>)}</select></label>
 {index===4&&<><label>合成状态<select aria-label="合成状态" value={nextState} onChange={e=>setNextState(e.target.value)}>{['queued','running','stopping','unknown','completed'].map(s=><option key={s}>{s}</option>)}</select></label><button onClick={()=>void fetch(`/api/fixture/history-state/${samples[index].id}/${nextState}`,{method:'POST'})}>更新合成状态</button></>}
 <button onClick={()=>{performance.clearResourceTimings();setVisible(false);setMounted(true);setRound(v=>v+1);}}>进入 / 重访</button>
 <button onClick={()=>setMounted(false)}>离开样本</button>
 <button onClick={()=>setVisible(v=>!v)}>{visible?'收起详情':'展开详情'}</button>
 <button disabled={sweeping} onClick={()=>void sweep()}>运行 12 个对照样本</button><output data-testid="sweep-state">{sweeping?"采样中":"采样结束"}</output><details><summary>批次结果</summary><pre data-testid="sweep-results">{JSON.stringify(records)}</pre></details>
 <details><summary>脱敏测量结果</summary><pre data-testid="history-metrics">{metrics}</pre></details>
 {mounted&&sample&&<section key={`${sample.id}:${round}`} className="chat-main" style={{maxWidth:1100,margin:'auto'}}>
  <div className="chat-conversation"><ConversationMessages conversationId={sample.id} onTrace={id=>{setFocus(id);setVisible(true);}}/></div>
  <div hidden={!visible}><ExecutionPanel visible={visible} conversation={{id:sample.id} as any} focusTurn={focus}/></div>
 </section>}
 </main>;
}
createRoot(document.getElementById('root')!).render(<App/>);
