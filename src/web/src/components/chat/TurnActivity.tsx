import { useEffect, useState } from "react";
import { ChevronRight } from "lucide-react";
import { ChatApiError, chatRequest, type TurnRead } from "./chatApi";
import { readChatEvents, type ChatEvent } from "./chatEvents";
import { traceNodes } from "./TrajectoryView";
import { executionConfigLabel } from "./executionLabels";
const labels: Record<string,string> = {queued:"排队中",connecting:"连接中",running:"执行中",stopping:"停止中",unknown:"状态未知",completed:"已完成",failed:"本轮运行失败",stopped:"已停止"};
type UsagePayload = { reasoning_duration_ms?: number; thinking_duration_ms?: number };
function durationLabel(ms?: number) {
 if (typeof ms !== "number" || !Number.isFinite(ms) || ms < 0) return "";
 if (ms < 1000) return `${Math.round(ms)} 毫秒`;
 const seconds = Math.round(ms / 1000);
 if (seconds < 60) return `${seconds}秒`;
 return `${Math.floor(seconds / 60)}分钟${seconds % 60}秒`;
}
export function TurnActivity({turnId,onTrace}:{turnId:string;onTrace:(id:string)=>void}) {
 const [events,setEvents]=useState<ChatEvent[]>([]),[turn,setTurn]=useState<TurnRead|null>(null),[error,setError]=useState("");
 useEffect(()=>{const controller=new AbortController();let timer:ReturnType<typeof setTimeout>,cursor=0;
 const poll=async()=>{try{const batch=await readChatEvents(turnId,cursor,controller.signal);const state=await chatRequest<TurnRead>(`/turns/${turnId}`,{signal:controller.signal});if(controller.signal.aborted)return;
 if(batch.length){cursor=batch[batch.length-1].sequence;setEvents(old=>[...old,...batch].slice(-1000));}setTurn(state);setError("");
 if(batch.length===200||!["completed","failed","stopped"].includes(state.status))timer=setTimeout(poll,batch.length===200?0:3000);
 }catch(e){if(!controller.signal.aborted){setError(e instanceof Error?e.message:"读取过程失败");if(e instanceof ChatApiError&&[401,403,404].includes(e.status)){setEvents([]);setTurn(null);}else timer=setTimeout(poll,3000);}}};void poll();return()=>{controller.abort();clearTimeout(timer);};},[turnId]);
 const nodes=traceNodes(events),tools=nodes.filter(n=>n.type==="execution.tool");
 const active=turn&&!["completed","failed","stopped"].includes(turn.status);
 const config=turn?.effective_config;
 const usage = events.filter(event => event.type === "execution.usage").map(event => event.payload as UsagePayload).filter(Boolean).slice(-1)[0];
 const reasoningDuration = durationLabel(usage?.reasoning_duration_ms ?? usage?.thinking_duration_ms);
 const statusLabel = turn ? labels[turn.status] || turn.status : "查看执行过程";
 const statusText = turn?.status === "completed" && reasoningDuration ? `${statusLabel}（思考 ${reasoningDuration}）` : statusLabel;
 return <div className="chat-turn-activity"><button className="chat-tool-summary" onClick={()=>onTrace(turnId)}><span className="status-dot"/>{tools.length?<>已读 <b>{tools.length} 次</b>工具调用 · </>:null}{statusText}<ChevronRight size={13}/>{config&&<span className="chat-effective-config" data-testid="chat-effective-config">{executionConfigLabel(config)}{turn?.config_fallback_reason?` · ${turn.config_fallback_reason}`:""}</span>}</button>{error&&<p role="alert">{error}</p>}{turn?.status==="failed"&&<p role="alert">本轮执行失败，已产生的内容保留。请在轨迹中查看详情或重试。</p>}{active&&<p role="status">{String(nodes.filter(n=>n.type==="execution.output").slice(-1)[0]?.payload.text||"正在等待执行结果…")}</p>}</div>;
}
