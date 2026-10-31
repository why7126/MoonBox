import { readTurnSummary, type TurnSummary } from "./sharedChatRead";
import { FullOutput } from "./FullOutput";
import {DirectCompletion} from "./DirectCompletion";
import { RecoveryOperationPanel, type RecoveryOperation } from "./RecoveryOperationPanel";
import { projectRunStatus } from "./turnStatus";
import type { GovernanceCandidate } from "./GovernanceResult";
import { useEffect, useState } from "react";
import { ChevronRight } from "lucide-react";
import { ChatApiError, normalizeChatError } from "./chatApi";
import { readChatEvents, type ChatEvent } from "./chatEvents";
import { traceNodes } from "./TrajectoryView";
import { executionConfigLabel } from "./executionLabels";
const preparationErrors: Record<string,string> = {
 container_toolchain_unavailable:"执行镜像工具链不完整或版本不匹配，本轮尚未启动。请按标准部署脚本更新执行镜像后重试。",
 workspace_unapplied_changes:"工作区有尚未应用的成果，已保留，不能覆盖。请先核对上一轮成果再重试。",
 workspace_fact_source_stale:"治理文件版本已变化，本轮尚未启动。请刷新后重新发送。",
 governance_validation_failed:"治理前置校验未通过，本轮尚未启动。请核对对象状态和必需文档。",
 workspace_prepare_failed:"工作区准备失败，本轮尚未启动，已有成果保留。请检查服务日志后重试。",
};
function durationLabel(ms?: number) {
 if (typeof ms !== "number" || !Number.isFinite(ms) || ms < 0) return "";
 if (ms < 1000) return `${Math.round(ms)} 毫秒`;
 const seconds = Math.round(ms / 1000);
 if (seconds < 60) return `${seconds}秒`;
 return `${Math.floor(seconds / 60)}分钟${seconds % 60}秒`;
}
export function TurnActivity({turnId,onTrace,hasBody=false,partial=false,truncated=false,truncationReason,candidate,onDraft=()=>{},draftText="",autoFollow=false}:{autoFollow?:boolean;turnId:string;onTrace:(id:string)=>void;hasBody?:boolean;partial?:boolean;truncated?:boolean;truncationReason?:string|null;candidate?:GovernanceCandidate;onDraft?:(text:string)=>void;draftText?:string}) {
 const [fullOutput,setFullOutput]=useState(false);
 const [directState,setDirectState]=useState('');
 const [expanded,setExpanded]=useState(false),[operation,setOperation]=useState<RecoveryOperation|null>(null),[operationError,setOperationError]=useState(false);
 const [events,setEvents]=useState<ChatEvent[]>([]),[turn,setTurn]=useState<TurnSummary|null>(null),[error,setError]=useState("");
 useEffect(() => {
   setEvents([]); setTurn(null); setDirectState(''); setError(''); setOperation(null); setOperationError(false); setExpanded(false);
   const controller = new AbortController();
   let timer: ReturnType<typeof setTimeout>, cursor = 0, running = false;
   const poll = async () => {
     if (document.hidden || controller.signal.aborted || running) return;
     running = true;
     try {
       const state = await readTurnSummary(turnId, controller.signal);
       if (controller.signal.aborted) return;
       setTurn(state); setError('');
       if (["completed", "failed", "stopped"].includes(state.status)) return;
       const batch = await readChatEvents(turnId, cursor, controller.signal);
       if (controller.signal.aborted) return;
       if (batch.length) { cursor = batch[batch.length - 1].sequence; setEvents(old => [...old, ...batch].slice(-1000)); }
       timer = setTimeout(poll, batch.length === 200 ? 0 : 3000);
     } catch (e) {
       if (!controller.signal.aborted) {
         const normalized = normalizeChatError(e, '执行状态暂不可读，正在重试');
         setError(normalized instanceof Error ? normalized.message : '执行状态暂不可读，正在重试');
         if (normalized instanceof ChatApiError && [401, 403, 404].includes(normalized.status)) { setEvents([]); setTurn(null); }
         else timer = setTimeout(poll, 3000);
       }
     } finally { running = false; }
   };
   const onVisible = () => { clearTimeout(timer); if (!document.hidden) void poll(); };
   void poll(); document.addEventListener('visibilitychange', onVisible);
   return () => { controller.abort(); clearTimeout(timer); document.removeEventListener('visibilitychange', onVisible); };
 }, [turnId]);
 const nodes=traceNodes(events),tools=nodes.filter(n=>n.type==="execution.tool");
 const active=turn&&["queued","connecting","running","stopping"].includes(turn.status);
 const preparationError=turn?.status==="failed" ? preparationErrors[turn.error_code||""] : undefined;
 const config=turn?.effective_config;
 const processOutput=String(nodes.filter(n=>n.type==="execution.output").slice(-1)[0]?.payload.text||"");
 const usage = turn?.usage;
 const reasoningDuration = durationLabel(usage?.reasoning_duration_ms ?? usage?.thinking_duration_ms);
 const projected=projectRunStatus({status:turn?.status,operation,business:!!candidate,rejected:candidate?.state==='rejected',error:!!error||operationError,hasBody,partial,truncated,truncationReason});
 const statusText=preparationError?'执行前阻断':directState==='verification_waiting'?'核验状态更新中':directState==='auto_checking'?'自动核验中':directState==='verification_blocked'?'核验待处理':directState==='needs_review'?'结果待核验':['validated','recovered_valid'].includes(directState)&&turn?.status==='completed'?'成果已核验':projected.label;
 return <div className="chat-turn-activity" data-testid="turn-status-root" data-turn-id={turnId}>
 <button className="chat-tool-summary" data-testid="turn-status-trigger" aria-expanded={expanded} aria-controls={`turn-detail-${turnId}`} onClick={()=>setExpanded(v=>!v)}><span className="status-dot"/><strong>{statusText}</strong>{projected.detail&&<span>{projected.detail}</span>}{(turn?.tool_count ?? tools.length)>0&&<span>{turn?.tool_count ?? tools.length} 次工具调用</span>}<ChevronRight size={13}/>{config&&<span className="chat-effective-config" data-testid="chat-effective-config">{executionConfigLabel(config)}{turn?.config_fallback_reason?` · ${turn.config_fallback_reason}`:""}{reasoningDuration?` · 思考 ${reasoningDuration}`:''}</span>}</button>
 <div data-testid="turn-status-feedback" role="status" aria-live="polite">{projected.notes.map(note=><p key={note}>{note}</p>)}{preparationError&&<p>{preparationError}</p>}{error&&<p>{error}</p>}</div>
 {truncated&&['preview_limit','read_window'].includes(truncationReason||'')&&<button type="button" className="chat-full-output-open" onClick={()=>setFullOutput(true)}>查看完整输出</button>}
 {fullOutput&&<FullOutput key={turnId} turnId={turnId} preferFinal={!partial} onClose={()=>setFullOutput(false)}/>}
 {active&&!hasBody&&<p data-testid="turn-process-output" aria-live="off">{processOutput||"正在等待执行结果…"}</p>}
 <div hidden={!expanded} id={`turn-detail-${turnId}`} data-testid="turn-execution-detail"><button onClick={()=>onTrace(turnId)}>查看本轮轨迹</button></div>
 {turn?.direct_action&&!candidate?.recovery_operation_id&&['completed','failed','stopped'].includes(turn.status)&&<DirectCompletion key={turnId} turnId={turnId} autoFollow={autoFollow} expanded={expanded} onState={setDirectState}/>}
 {candidate?.recovery_operation_id&&<RecoveryOperationPanel key={candidate.recovery_operation_id} operationId={candidate.recovery_operation_id} refreshKey={`${turn?.status||''}:${candidate.state}`} onDraft={onDraft} draftText={draftText} collapsed={!expanded} writesDisabled={!!error || (!!operation && operation.historical_result==='verified' && !!turn && ['running','stopping'].includes(turn.status))} onOperation={setOperation} onReadError={setOperationError}/>}
 </div>;
}
