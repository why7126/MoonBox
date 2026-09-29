import { useEffect, useRef, useState } from "react";
import { Box, Check, CircleAlert, Copy, Sparkles } from "lucide-react";
import { TurnActivity } from "./TurnActivity";
import { SafeMarkdown } from "./SafeMarkdown";
import { ChatApiError, chatRequest, fetchChatMaterialBlob, type ExecutionConfig, type MaterialRef, type TurnRead } from "./chatApi";
import { readChatEvents, type ChatEvent } from "./chatEvents";
import { executionConfigLabel } from "./executionLabels";
type Message = { id: string; turn_id?: string; role: string; content: string; created_at: string; materials?: MaterialRef[]; effective_config?: ExecutionConfig; config_fallback_reason?: string | null };
type UsagePayload = {
  total_tokens?: number;
  input_tokens?: number;
  output_tokens?: number;
  reasoning_tokens?: number;
  first_token_ms?: number;
  first_token_latency_ms?: number;
  duration_ms?: number;
  reasoning_duration_ms?: number;
  thinking_duration_ms?: number;
};
type CopyState = "idle" | "copied" | "failed";
type PreviewMaterial = MaterialRef & { preview_url?: string };
function skillDisplayName(value: string) {
  return value.split("-").filter(Boolean).map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(" ") || value;
}
function messageContentForDisplay(row: Message, skills: MaterialRef[]) {
  if (row.role !== "user") return row.content;
  return row.content
    .split(/\r?\n/)
    .filter(line => !/^\s*(?:[-*]\s*)?(?:Skill|图片|文件)\s*引用\s*[：:]/i.test(line))
    .join("\n")
    .trim();
}
function splitFirstMessageBlock(content: string) {
  const trimmed = content.trim();
  if (!trimmed) return { first: "", rest: "" };
  const match = /\n\s*\n/.exec(trimmed);
  if (!match) return { first: trimmed, rest: "" };
  return {
    first: trimmed.slice(0, match.index).trim(),
    rest: trimmed.slice(match.index + match[0].length).trim(),
  };
}
function materialPreviewUrl(item: MaterialRef) {
  const metadata = item.metadata || {};
  return metadata.preview_url || metadata.url || metadata.download_url || metadata.content_url
    || (item.kind === "image" && item.ref_id ? `/api/v1/chat/materials/${encodeURIComponent(item.ref_id)}/content` : "");
}
function materialTypeLabel(item: MaterialRef) {
  if (item.kind === "image") return (item.mime_type || "").split("/")[1]?.toUpperCase() || "IMG";
  return "FILE";
}
function MaterialPreviewDialog({ item, onClose }: { item: PreviewMaterial; onClose: () => void }) {
  const objectUrl = useMaterialObjectUrl(item.preview_url || "", item.kind === "image");
  const src = objectUrl || "";
  return <div className="chat-material-preview-backdrop" role="presentation" onClick={onClose}>
    <section className="chat-material-preview" role="dialog" aria-modal="true" aria-label={`查看附件 ${item.name}`} onClick={event => event.stopPropagation()}>
      <header><div><strong>{item.name}</strong><small>{item.mime_type || "未知类型"} · {item.size_bytes || 0} bytes</small></div><button type="button" onClick={onClose}>关闭</button></header>
      {src ? <img src={src} alt={item.name} /> : <div className="chat-material-preview-empty">
        <b>{materialTypeLabel(item)}</b>
        <p>{item.preview_url ? "正在读取图片预览…" : "当前历史摘要未包含可预览地址，仅展示材料摘要。"}</p>
      </div>}
    </section>
  </div>;
}
function useMaterialObjectUrl(path: string, enabled = true) {
  const [url, setUrl] = useState("");
  useEffect(() => {
    if (!path || !enabled) { setUrl(""); return; }
    const controller = new AbortController();
    let objectUrl = "";
    setUrl("");
    fetchChatMaterialBlob(path, controller.signal)
      .then(blob => {
        if (controller.signal.aborted) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch(() => {
        if (!controller.signal.aborted) setUrl("");
      });
    return () => {
      controller.abort();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path, enabled]);
  return url;
}
function MaterialThumbnail({ item }: { item: MaterialRef }) {
  const path = materialPreviewUrl(item);
  const src = useMaterialObjectUrl(path, item.kind === "image");
  return <>
    {src && <img src={src} alt="" aria-hidden="true" />}
    <b>{materialTypeLabel(item)}</b>
    <span>{item.name}</span>
    <small>{`${item.mime_type || ""} ${item.size_bytes || 0} bytes`}</small>
  </>;
}
function durationLabel(ms?: number) {
  if (typeof ms !== "number" || !Number.isFinite(ms) || ms < 0) return "";
  if (ms < 1000) return `${Math.round(ms)} 毫秒`;
  const seconds = Math.round(ms / 1000);
  if (seconds < 60) return `${seconds}秒`;
  return `${Math.floor(seconds / 60)}分钟${seconds % 60}秒`;
}
function latestUsage(events: ChatEvent[]) {
  return events.filter(event => event.type === "execution.usage").map(event => event.payload as UsagePayload).filter(Boolean).slice(-1)[0];
}
async function copyText(text: string) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      // Fall back below for browsers or permission states that reject clipboard writes.
    }
  }
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.setAttribute("readonly", "true");
  textarea.style.position = "fixed";
  textarea.style.left = "-9999px";
  textarea.style.top = "0";
  document.body.appendChild(textarea);
  textarea.focus();
  textarea.select();
  try {
    return document.execCommand?.("copy") === true;
  } catch {
    return false;
  } finally {
    document.body.removeChild(textarea);
  }
}
function CopyMessageButton({ text }: { text: string }) {
  const [state, setState] = useState<CopyState>("idle");
  useEffect(() => {
    if (state === "idle") return;
    const timer = setTimeout(() => setState("idle"), 1500);
    return () => clearTimeout(timer);
  }, [state]);
  const label = state === "copied" ? "已复制" : state === "failed" ? "复制失败" : "复制消息";
  const Icon = state === "copied" ? Check : state === "failed" ? CircleAlert : Copy;
  return <button className={`chat-message-copy ${state}`} aria-label={label} title={label} onClick={async()=>setState(await copyText(text) ? "copied" : "failed")}><Icon size={13} aria-hidden="true"/></button>;
}
function AssistantMeta({ row, skills, displayContent }: { row: Message; skills: MaterialRef[]; displayContent: string }) {
  const [events, setEvents] = useState<ChatEvent[]>([]);
  const [turn, setTurn] = useState<TurnRead | null>(null);
  useEffect(() => {
    if (!row.turn_id) return;
    const controller = new AbortController();
    const load = async () => {
      try {
        const [batch, state] = await Promise.all([
          readChatEvents(row.turn_id!, 0, controller.signal),
          chatRequest<TurnRead>(`/turns/${row.turn_id}`, { signal: controller.signal }),
        ]);
        if (!controller.signal.aborted) { setEvents(batch); setTurn(state); }
      } catch {
        if (!controller.signal.aborted) { setEvents([]); setTurn(null); }
      }
    };
    void load();
    return () => controller.abort();
  }, [row.turn_id]);
  const usage = latestUsage(events);
  const firstToken = durationLabel(usage?.first_token_latency_ms ?? usage?.first_token_ms);
  const reasoningDuration = durationLabel(usage?.reasoning_duration_ms ?? usage?.thinking_duration_ms);
  const usageDuration = durationLabel(usage?.duration_ms);
  const totalDuration = !usageDuration && turn && ["completed", "failed", "stopped"].includes(turn.status)
    ? durationLabel(new Date(turn.updated_at).getTime() - new Date(turn.created_at).getTime())
    : "";
  const tokenText = typeof usage?.total_tokens === "number"
    ? `Token ${usage.total_tokens}${typeof usage.input_tokens === "number" ? ` / 输入 ${usage.input_tokens}` : ""}${typeof usage.output_tokens === "number" ? ` / 输出 ${usage.output_tokens}` : ""}${typeof usage.reasoning_tokens === "number" ? ` / 思考 ${usage.reasoning_tokens}` : ""}`
    : "";
  const skillTitle = skills.map(item => skillDisplayName(item.name)).join("、");
  return <div className="chat-message-meta chat-assistant-meta">
    <CopyMessageButton text={displayContent || row.content}/>
    {!!skills.length&&<><span className="chat-message-sep">·</span><button type="button" className="chat-skill-meta" aria-label={`使用的 Skill：${skillTitle}`} title={`Skills\n${skillTitle}`}><Sparkles size={14} aria-hidden="true"/></button></>}
    <span className="chat-message-sep">·</span>
    <time>{new Date(row.created_at).toLocaleString()}</time>
    {!!firstToken&&<><span className="chat-message-sep">·</span><span>首 Token {firstToken}</span></>}
    {!!reasoningDuration&&<><span className="chat-message-sep">·</span><span>思考 {reasoningDuration}</span></>}
    {!!(usageDuration || totalDuration)&&<><span className="chat-message-sep">·</span><span>耗时 {usageDuration || totalDuration}</span></>}
    {!!tokenText&&<><span className="chat-message-sep">·</span><span>{tokenText}</span></>}
  </div>;
}
function UserMessageBody({ content, skills }: { content: string; skills: MaterialRef[] }) {
  const { first, rest } = splitFirstMessageBlock(content);
  return <>
    {(!!skills.length || !!first) && <div className="chat-user-inline-flow" data-testid="chat-user-inline-flow">
      {!!skills.length && <span className="chat-message-skills" data-testid="chat-message-skills">
        {skills.map((item,index)=><span key={`${item.ref_id || item.name}-${index}`} className="chat-message-skill"><Sparkles size={13} aria-hidden="true"/><span>{skillDisplayName(item.name)}</span></span>)}
      </span>}
      {!!first && <span className="chat-user-inline-text">{first}</span>}
    </div>}
    {!!rest && <SafeMarkdown content={rest}/>}
  </>;
}
export function ConversationMessages({ conversationId, onTrace }: { conversationId: string; onTrace?: (id: string) => void }) {
  const [rows, setRows] = useState<Message[]>([]), [page,setPage] = useState(1), [more,setMore] = useState(true), [loading,setLoading] = useState(true), [error,setError] = useState("");
  const [preview, setPreview] = useState<PreviewMaterial | null>(null);
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
  const assistantTurnIds = new Set(rows.filter(row => row.role !== "user" && row.turn_id).map(row => row.turn_id));
  return <div className="chat-message-history" ref={root} data-testid="chat-message-history">
    {more && rows.length>0 && <button disabled={loading} onClick={()=>{follow.current=false;setLoading(true);setPage(p=>p+1);}}>加载更早消息</button>}
    {error && <p role="alert" className="chat-error">{error}</p>}
    {!rows.length && <p role="status">{loading?"正在读取消息…":error?"":"开始一个新话题"}</p>}
    {rows.map(row=>{
      const skills=(row.materials||[]).filter(item=>item.kind==="skill");
      const attachments=row.role==="user"?(row.materials||[]).filter(item=>item.kind!=="skill"):[];
      const displayContent=messageContentForDisplay(row, skills);
      const effectiveConfig=executionConfigLabel(row.effective_config);
      return <div className={`chat-message-block ${row.role === "user" ? "turn-user" : "turn-assistant"}`} key={row.id}>
        <article className={`chat-message ${row.role==="user"?"chat-message-user":""}`} key={row.id}>
          <strong>{row.role==="user"?"你":"助手"}</strong>
          {row.role!=="user"&&<span className="chat-assistant-avatar" aria-hidden="true"><Box size={15}/></span>}
          <div className={row.role==="user"?"chat-turn-content":"chat-assistant-col"}>
            {!!attachments.length && <div className="chat-message-attachments" data-testid="chat-message-attachments">
              {attachments.map((item,index)=><button type="button" key={`${item.kind}-${item.ref_id || item.name}-${index}`} className={`chat-message-attachment ${item.kind==="image"?"is-image":"is-file"}`} title={`${item.name} · ${item.size_bytes || 0} bytes`} aria-label={`查看附件 ${item.name}`} onClick={()=>setPreview({...item, preview_url: materialPreviewUrl(item)})}><MaterialThumbnail item={item}/></button>)}
            </div>}
            {row.role!=="user"&&row.turn_id&&onTrace&&<TurnActivity turnId={row.turn_id} onTrace={onTrace}/>}
            <div className="chat-message-bubble">
              {row.role==="user"
                ? <UserMessageBody content={displayContent} skills={skills}/>
                : !!displayContent&&<SafeMarkdown content={displayContent}/>}
            </div>
            {row.role==="user"?<div className="chat-message-meta">
              {row.role==="user"&&effectiveConfig&&<><span className="chat-message-model" data-testid="chat-message-model">{effectiveConfig}{row.config_fallback_reason?` · ${row.config_fallback_reason}`:""}</span><span className="chat-message-sep">·</span></>}
              <time>{new Date(row.created_at).toLocaleString()}</time>
              <span className="chat-message-sep">·</span>
              <CopyMessageButton text={displayContent || row.content}/>
            </div>:<AssistantMeta row={row} skills={skills} displayContent={displayContent}/>}
          </div>
        </article>{row.role==="user"&&row.turn_id&&onTrace&&!assistantTurnIds.has(row.turn_id)&&<TurnActivity turnId={row.turn_id} onTrace={onTrace}/>}
      </div>;
    })}
    {preview&&<MaterialPreviewDialog item={preview} onClose={()=>setPreview(null)}/>}
    {!atBottom && <button className="chat-jump-bottom" onClick={()=>{follow.current=true;root.current?.lastElementChild?.scrollIntoView?.({block:"end"});}}>回到最新消息</button>}
    <div aria-hidden="true"/>
  </div>;
}
