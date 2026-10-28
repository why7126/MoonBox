import {useDirectVerification} from './useDirectVerification';
import {directVerificationReasons as reasons} from './directVerificationReasons';

export function DirectCompletion({turnId,expanded,onState,autoFollow=false,disabled=false}:{turnId:string;expanded:boolean;onState:(state:string)=>void;autoFollow?:boolean;disabled?:boolean}){
 const {facts,busy,error,paused,read,verify}=useDirectVerification(turnId,autoFollow,expanded,onState);
 return <div hidden={!expanded} data-testid="direct-completion-detail">
 {facts&&<p>{['direct_historical_verified','direct_successor_verified','direct_successor_available'].includes(facts.reason_code||'')?reasons[facts.reason_code||'']:['validated','recovered_valid'].includes(facts.state)?'成果已核验，原执行历史保留。':['pending','checking'].includes(facts.auto_verification?.state||'')?'正在自动核验，无需重复操作。':facts.auto_verification?.state==='blocked'?(reasons[facts.auto_verification.reason_code||'']||'自动核验未通过，请核对成果后重试。'):reasons[facts.reason_code||'']||(autoFollow?'核验状态更新中。':'成果待核验。')}</p>}
 {facts?.historical_evidence_missing&&facts.can_verify&&facts.reason_code!=='direct_historical_evidence_missing'&&<p>{reasons.direct_historical_evidence_missing}</p>}
 {Boolean(facts?.differences?.length)&&<ul>{facts?.differences?.map(d=><li key={d.path}>{({added:'新增',deleted:'删除',modified:'修改'} as Record<string,string>)[d.kind]||d.kind}：{d.path}</li>)}</ul>}
 {facts?.last_checked_at&&<small>最近核验：{new Date(facts.last_checked_at).toLocaleString()}</small>}
 {Boolean(Object.keys(facts?.successor_evidence||{}).length)&&<details data-testid="direct-successor-evidence"><summary>查看后续完成证据</summary><ul>{Object.entries(facts?.successor_evidence||{}).map(([change,run])=><li key={change} style={{overflowWrap:'anywhere'}}>验收报告：openspec/changes/{change}/evidence/acceptance/{run}/summary.md</li>)}</ul></details>}
 <div className="recovery-actions">{facts?.can_verify&&<button data-testid="direct-completion-verify" disabled={busy||disabled} onClick={()=>void verify()}>{busy?'核验中…':'核验当前成果'}</button>}{(error||paused)&&<button disabled={busy} onClick={()=>void read()}>刷新核验状态</button>}</div>
 {paused&&<p role="status">自动跟进已暂停，可刷新状态。</p>}
 {error&&<p role="status">{error}</p>}
 </div>;
}
