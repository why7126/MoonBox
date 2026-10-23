import {useCallback,useEffect,useRef,useState} from 'react';
import {GovernanceError,governanceRequest} from '../workbench/governanceApi';
import type {DirectVerificationResponse} from '../../api/generated/governance';
import {directVerificationReasons as reasons} from './directVerificationReasons';

export function DirectCompletion({turnId,expanded,onState}:{turnId:string;expanded:boolean;onState:(state:string)=>void}){
 const [facts,setFacts]=useState<DirectVerificationResponse|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const lock=useRef(false),alive=useRef(true),observer=useRef(onState);observer.current=onState;
 const url=`/api/v1/chat/turns/${encodeURIComponent(turnId)}/completion-verification`;
 const read=useCallback(async(signal?:AbortSignal)=>{try{const f=await governanceRequest<DirectVerificationResponse>(url,{signal});if(!alive.current||signal?.aborted)return;setFacts(f);observer.current(f.state);setError('');}catch{if(alive.current&&!signal?.aborted)setError('核验状态暂不可读，请稍后重试。');}},[url]);
 useEffect(()=>{alive.current=true;setFacts(null);setError('');const c=new AbortController();void read(c.signal);return()=>{alive.current=false;c.abort();};},[read]);
 const verify=async()=>{if(lock.current||!facts?.can_verify||!facts.version)return;lock.current=true;setBusy(true);try{
 const f=await governanceRequest<DirectVerificationResponse>(url,{method:'POST',body:JSON.stringify({expected_version:facts.version})});if(!alive.current)return;setFacts(f);observer.current(f.state);setError('');window.dispatchEvent(new Event('governance-operation-verified'));
 }catch(e){if(alive.current)setError(e instanceof GovernanceError?(reasons[e.kind||'']||e.message):e instanceof Error?e.message:'核验未通过，原成果和保护已保留。');}finally{lock.current=false;if(alive.current)setBusy(false);}};
 return <div hidden={!expanded} data-testid="direct-completion-detail">
 {facts&&<p>{facts.reason_code==='direct_historical_verified'?reasons.direct_historical_verified:['validated','recovered_valid'].includes(facts.state)?'成果已核验，原执行历史保留。':reasons[facts.reason_code||'']||'成果待核验。'}</p>}
 {facts?.historical_evidence_missing&&facts.can_verify&&facts.reason_code!=='direct_historical_evidence_missing'&&<p>{reasons.direct_historical_evidence_missing}</p>}
 {Boolean(facts?.differences?.length)&&<ul>{facts?.differences?.map(d=><li key={d.path}>{({added:'新增',deleted:'删除',modified:'修改'} as Record<string,string>)[d.kind]||d.kind}：{d.path}</li>)}</ul>}
 {facts?.last_checked_at&&<small>最近核验：{new Date(facts.last_checked_at).toLocaleString()}</small>}
 <div className="recovery-actions">{facts?.can_verify&&<button data-testid="direct-completion-verify" disabled={busy} onClick={()=>void verify()}>{busy?'核验中…':'核验当前成果'}</button>}{error&&<button disabled={busy} onClick={()=>void read()}>刷新核验状态</button>}</div>
 {error&&<p role="status">{error}</p>}
 </div>;
}
