import {useEffect,useRef,useState} from 'react';
import {governanceRequest} from '../workbench/governanceApi';
import {ChatDialog} from './ChatDialog';
import {verificationReason} from './RecoveryOperationPanel';
import {DirectCompletion} from './DirectCompletion';
import {Button} from '../ui/Button';
export type VerificationFacts={verification_operation_id?:string|null;view_turn_id?:string|null;historical_result?:string;verification_reason?:string|null;last_checked_at?:string|null;verification_actions?:string[];verification_differences?:string[]};
export function OperationVerification({facts,onRefresh,onOriginal,disabled=false}:{facts:VerificationFacts;onRefresh:()=>void;onOriginal?:()=>void;disabled?:boolean}) {
 const [busy,setBusy]=useState(false),[error,setError]=useState(''),[open,setOpen]=useState(false);
 const lock=useRef(false),alive=useRef(true);
 const [expanded,setExpanded]=useState(false);
 const verified=useRef(false);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;};},[]);
 const verify=async()=>{
   if(lock.current||busy||disabled||!facts.verification_operation_id||!facts.verification_actions?.includes('verify'))return;
   lock.current=true;setBusy(true);
   try{await governanceRequest(`/api/v1/chat/governance-operations/${encodeURIComponent(facts.verification_operation_id)}/verifications`,{method:'POST'});if(!alive.current)return;setError('');onRefresh();window.dispatchEvent(new Event('governance-operation-verified'));}
   catch{if(alive.current)setError('状态核验失败，保留上次事实，请稍后重试。');}
   finally{lock.current=false;if(alive.current)setBusy(false);}
 };
 if(!facts.verification_operation_id&&facts.view_turn_id)return <details className="rc-operation-details" data-testid="requirement-operation-status" onClick={e=>e.stopPropagation()} onToggle={e=>setExpanded(e.currentTarget.open)}>
 <summary>状态详情</summary>
 <DirectCompletion turnId={facts.view_turn_id} expanded={expanded} disabled={disabled} onState={state=>{if(['validated','recovered_valid'].includes(state)&&!verified.current){verified.current=true;onRefresh();}}}/>
 {onOriginal&&<Button variant="ghost" onClick={onOriginal} data-testid="operation-original-run">查看原执行</Button>}
 </details>;
 if(!facts.verification_operation_id && !facts.verification_reason && facts.historical_result!=="verified")return null;
 return <details className="rc-operation-details" data-testid="requirement-operation-status" onClick={e=>e.stopPropagation()}>
 <summary>状态详情</summary>
 {facts.historical_result==='verified'&&<p>历史成果已应用并核验</p>}
 {facts.verification_reason&&<p>{verificationReason(facts.verification_reason)}</p>}
 {facts.last_checked_at&&<small>最近核验：{new Date(facts.last_checked_at).toLocaleString()}</small>}
 <div className="recovery-actions">{facts.verification_operation_id&&facts.verification_actions?.includes('verify')&&<button disabled={busy||disabled} onClick={()=>void verify()} data-testid="operation-verify">{busy?'核验中…':'重新核验'}</button>}
 {!!facts.verification_differences?.length&&<button data-testid="operation-differences" onClick={()=>setOpen(true)}>查看差异</button>}
 {onOriginal&&facts.view_turn_id&&<button onClick={onOriginal} data-testid="operation-original-run">查看原执行</button>}</div>
 {error&&<p role="status">{error}</p>}
 {open&&<ChatDialog title="相关变化" testId="operation-differences-dialog" onClose={()=>setOpen(false)}><p>操作：{facts.verification_operation_id}</p>{facts.verification_differences?.map(d=><p key={d}>{d}</p>)}</ChatDialog>}
 </details>;
}
