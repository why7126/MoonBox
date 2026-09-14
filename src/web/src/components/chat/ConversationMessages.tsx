import { useEffect, useRef, useState } from "react";
import { TurnActivity } from "./TurnActivity";
import { SafeMarkdown } from "./SafeMarkdown";
import { ChatApiError, chatRequest } from "./chatApi";
type Message = { id: string; turn_id?: string; role: string; content: string; created_at: string };
export function ConversationMessages({ conversationId, onTrace }: { conversationId: string; onTrace?: (id: string) => void }) {
  const [rows, setRows] = useState<Message[]>([]), [page,setPage] = useState(1), [more,setMore] = useState(true), [loading,setLoading] = useState(true), [error,setError] = useState("");
  const root = useRef<HTMLDivElement>(null), follow = useRef(true), [atBottom,setAtBottom] = useState(true);
  useEffect(() => {
    const scroller = root.current?.closest(".chat-conversation");
    const changed=()=>{if(scroller){follow.current=scroller.scrollHeight-scroller.scrollTop-scroller.clientHeight<100;setAtBottom(follow.current);}};
    scroller?.addEventListener("scroll",changed);return()=>scroller?.removeEventListener("scroll",changed);
  },[]);
  useEffect(()=>{ if(follow.current) root.current?.lastElementChild?.scrollIntoView?.({block:"end"}); },[rows]);
  useEffect(() => {
    const controller=new AbortController();let timer:ReturnType<typeof setTimeout>;
    const merge=(items:Message[])=>setRows(old=>[...new Map([...old,...items].map(r=>[r.id,r])).values()].sort((a,b)=>a.created_at.localeCompare(b.created_at)||a.id.localeCompare(b.id)));
    const read=async (older=false)=>{
      try {
        const data=await chatRequest<{items:Message[]}>(`/conversations/${conversationId}/messages?page=${older?page:1}`,{signal:controller.signal});
        if(controller.signal.aborted)return;
        const scroller=root.current?.closest(".chat-conversation"), height=scroller?.scrollHeight||0;
        merge(data.items);setError("");setLoading(false);
        if(older||page===1)setMore(data.items.length===20);
        if(older && scroller)requestAnimationFrame(()=>{if(!controller.signal.aborted)scroller.scrollTop+=scroller.scrollHeight-height;});
      } catch(e){if(!controller.signal.aborted){setError(e instanceof Error?e.message:"读取失败");setLoading(false);if(e instanceof ChatApiError&&[401,403,404].includes(e.status))setRows([]);}}
    };
    const poll=async()=>{await read();if(!controller.signal.aborted)timer=setTimeout(poll,3000);};
    if(page>1)void read(true);void poll();return()=>{controller.abort();clearTimeout(timer);};
  },[conversationId,page]);
  return <div className="chat-message-history" ref={root} data-testid="chat-message-history">
    {more && rows.length>0 && <button disabled={loading} onClick={()=>{follow.current=false;setLoading(true);setPage(p=>p+1);}}>加载更早消息</button>}
    {error && <p role="alert" className="chat-error">{error}</p>}
    {!rows.length && <p role="status">{loading?"正在读取消息…":error?"":"开始一个新话题"}</p>}
    {rows.map(row=><div key={row.id}><article className={`chat-message ${row.role==="user"?"chat-message-user":""}`} key={row.id}>
      <strong>{row.role==="user"?"你":"助手"}</strong><SafeMarkdown content={row.content}/>
      <div className="chat-message-meta"><time>{new Date(row.created_at).toLocaleString()}</time><button aria-label="复制消息" onClick={()=>{void navigator.clipboard?.writeText(row.content).catch(()=>{});}}>复制</button>{row.turn_id&&onTrace&&<button onClick={()=>onTrace(row.turn_id!)}>查看本轮轨迹</button>}</div>
    </article>{row.role==="user"&&row.turn_id&&onTrace&&<TurnActivity turnId={row.turn_id} onTrace={onTrace}/>}</div>)}
    {!atBottom && <button className="chat-jump-bottom" onClick={()=>{follow.current=true;root.current?.lastElementChild?.scrollIntoView?.({block:"end"});}}>回到最新消息</button>}
    <div aria-hidden="true"/>
  </div>;
}
