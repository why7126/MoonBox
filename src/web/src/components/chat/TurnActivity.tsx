import { useEffect, useState } from "react";
import { ChatApiError, chatRequest, type TurnRead } from "./chatApi";
import { readChatEvents, type ChatEvent } from "./chatEvents";
import { traceNodes } from "./TrajectoryView";
const labels: Record<string,string> = {queued:"排队中",connecting:"连接中",running:"执行中",stopping:"停止中",unknown:"状态未知",completed:"已完成",failed:"本轮运行失败",stopped:"已停止"};
export function TurnActivity({turnId,onTrace}:{turnId:string;onTrace:(id:string)=>void}) {
 const [events,setEvents]=useState<ChatEvent[]>([]),[turn,setTurn]=useState<TurnRead|null>(null),[error,setError]=useState("");
 useEffect(()=>{const controller=new AbortController();let timer:ReturnType<typeof setTimeout>,cursor=0;
 const poll=async()=>{try{const batch=await readChatEvents(turnId,cursor,controller.signal);const state=await chatRequest<TurnRead>(`/turns/${turnId}`,{signal:controller.signal});if(controller.signal.aborted)return;
 if(batch.length){cursor=batch[batch.length-1].sequence;setEvents(old=>[...old,...batch].slice(-1000));}setTurn(state);setError("");
 if(batch.length===200||!["completed","failed","stopped"].includes(state.status))timer=setTimeout(poll,batch.length===200?0:3000);
 }catch(e){if(!controller.signal.aborted){setError(e instanceof Error?e.message:"读取过程失败");if(e instanceof ChatApiError&&[401,403,404].includes(e.status)){setEvents([]);setTurn(null);}else timer=setTimeout(poll,3000);}}};void poll();return()=>{controller.abort();clearTimeout(timer);};},[turnId]);
 const nodes=traceNodes(events),tools=nodes.filter(n=>n.type==="execution.tool");
 const active=turn&&!["completed","failed","stopped"].includes(turn.status);
 return <div className="chat-turn-activity"><button onClick={()=>onTrace(turnId)}>{tools.length?`已读 ${tools.length} 次工具调用 · `:""}{turn?labels[turn.status]||turn.status:"查看执行过程"} ›</button>{error&&<p role="alert">{error}</p>}{turn?.status==="failed"&&<p role="alert">本轮执行失败，已产生的内容保留。请在轨迹中查看详情或重试。</p>}{active&&<p role="status">{String(nodes.filter(n=>n.type==="execution.output").slice(-1)[0]?.payload.text||"正在等待执行结果…")}</p>}</div>;
}
