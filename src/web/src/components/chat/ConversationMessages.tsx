import { QuestionPanel } from "./QuestionPanel";
import { readTurnSummary, type TurnSummary } from "./sharedChatRead";
import { useConversationMessages, messageTime, type OrderedMessage } from "./useConversationMessages";
import type { GovernanceCandidate } from "./GovernanceResult";
import type { MessageRead as GeneratedMessageRead } from "../../api/generated/chat";
import { Fragment, useEffect, useRef, useState, type ReactNode } from "react";
import { Box, Check, CircleAlert, Copy, Sparkles } from "lucide-react";
import { TurnActivity } from "./TurnActivity";
import { SafeMarkdown } from "./SafeMarkdown";
import { ChatApiError, normalizeChatError, chatRequest, fetchChatMaterialBlob, type ExecutionConfig, type MaterialRef } from "./chatApi";
import { executionConfigLabel } from "./executionLabels";
type Message = OrderedMessage & Pick<GeneratedMessageRead, "output_partial" | "output_truncated" | "output_source" | "output_truncation_reason"> & { id: string; turn_id?: string; role: string; content: string; created_at: string; materials?: MaterialRef[]; effective_config?: ExecutionConfig; config_fallback_reason?: string | null };
type CopyState = "idle" | "copied" | "failed";
type PreviewMaterial = MaterialRef & { preview_url?: string };
function skillDisplayName(value: string) {
  return value.split("-").filter(Boolean).map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(" ") || value;
}
function messageContentForDisplay(row: Message, skills: MaterialRef[]) {
  if (row.role !== "user") return row.content;
  const content = visibleGovernancePrompt(row.content);
  return content
    .split(/\r?\n/)
    .filter(line => !/^\s*(?:[-*]\s*)?(?:Skill|图片|文件)\s*引用\s*[：:]/i.test(line))
    .join("\n")
    .trim();
}
function visibleGovernancePrompt(content: string) {
  const trimmed = content.trim();
  const [firstLine = "", ...restLines] = trimmed.split(/\r?\n/);
  const rest = restLines.join("\n");
  if (/^\/(?:bug|req)-generate\s+\S+/.test(firstLine.trim()) && /(所有生成Markdown|本次仅生成目标|治理成果以实际差异校验|同步前先检查 dry-run)/.test(rest)) {
    return firstLine.trim();
  }
  return content;
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
  const [turn, setTurn] = useState<TurnSummary | null>(null);
  useEffect(() => {
    setTurn(null);
    if (!row.turn_id) return;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout>, running = false;
    const load = async () => {
      if (document.hidden || controller.signal.aborted || running) return;
      running = true;
      try {
        const state = await readTurnSummary(row.turn_id!, controller.signal);
        if (controller.signal.aborted) return;
        setTurn(state);
        if (!["completed", "failed", "stopped"].includes(state.status)) timer = setTimeout(load, 3000);
      } catch (e) {
        if (!controller.signal.aborted) {
          setTurn(null);
          if (!(e instanceof ChatApiError && [401, 403, 404].includes(e.status))) timer = setTimeout(load, 3000);
        }
      } finally { running = false; }
    };
    const onVisible = () => { clearTimeout(timer); if (!document.hidden) void load(); };
    void load(); document.addEventListener('visibilitychange', onVisible);
    return () => { controller.abort(); clearTimeout(timer); document.removeEventListener('visibilitychange', onVisible); };
  }, [row.turn_id]);
  const usage = turn?.usage;
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
    <time>{messageTime(row)}</time>
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
export function ConversationMessages({ conversationId, onTrace, footer, rejectedGovernanceTurnIds = [], candidates = [], onDraft = () => {}, draftText = "" }: { footer?: ReactNode; candidates?: GovernanceCandidate[]; onDraft?: (text:string)=>void; draftText?:string; conversationId: string; onTrace?: (id: string) => void; rejectedGovernanceTurnIds?: string[] }) {
  const [preview, setPreview] = useState<PreviewMaterial | null>(null);
  const root = useRef<HTMLDivElement>(null), follow = useRef(true), [atBottom,setAtBottom] = useState(true);
  const { rows, more, loading, error, compatibility, loadOlder } = useConversationMessages<Message>(conversationId, () => {
    const scroller = root.current?.closest(".chat-conversation"), height = scroller?.scrollHeight || 0;
    return () => { if (scroller) scroller.scrollTop += scroller.scrollHeight - height; };
  });
  useEffect(() => {
    const scroller = root.current?.closest(".chat-conversation");
    const changed=()=>{if(scroller){follow.current=scroller.scrollHeight-scroller.scrollTop-scroller.clientHeight<100;setAtBottom(follow.current);}};
    scroller?.addEventListener("scroll",changed);return()=>scroller?.removeEventListener("scroll",changed);
  },[]);
  useEffect(()=>{ if(follow.current) root.current?.lastElementChild?.scrollIntoView?.({block:"end"}); },[rows]);
  const assistantTurnIds = new Set(rows.filter(row => row.role !== "user" && row.turn_id).map(row => row.turn_id));
  return <div className="chat-message-history" ref={root} data-testid="chat-message-history">
    {more && rows.length>0 && <button disabled={loading} onClick={()=>{follow.current=false;loadOlder();}}>加载更早消息</button>}
    {compatibility && <p role="status" className="chat-message-time">历史消息正在使用兼容模式，顺序可能尚未校正。</p>}
    {error && <p role="alert" className="chat-error">{error}</p>}
    {!rows.length && <p role="status">{loading?"正在读取消息…":error?"":"开始一个新话题"}</p>}
    {rows.map((row,rowIndex)=>{
      const skills=(row.materials||[]).filter(item=>item.kind==="skill");
      const attachments=row.role==="user"?(row.materials||[]).filter(item=>item.kind!=="skill"):[];
      const displayContent=messageContentForDisplay(row, skills);
      const effectiveConfig=executionConfigLabel(row.effective_config);
      return <Fragment key={row.id}><div className={`chat-message-block ${row.role === "user" ? "turn-user" : "turn-assistant"}`}>
        <article className={`chat-message ${row.role==="user"?"chat-message-user":""}`} key={row.id}>
          <strong>{row.role==="user"?"你":"助手"}</strong>
          {row.role!=="user"&&<span className="chat-assistant-avatar" aria-hidden="true"><Box size={15}/></span>}
          <div className={row.role==="user"?"chat-turn-content":"chat-assistant-col"}>
            {!!attachments.length && <div className="chat-message-attachments" data-testid="chat-message-attachments">
              {attachments.map((item,index)=><button type="button" key={`${item.kind}-${item.ref_id || item.name}-${index}`} className={`chat-message-attachment ${item.kind==="image"?"is-image":"is-file"}`} title={`${item.name} · ${item.size_bytes || 0} bytes`} aria-label={`查看附件 ${item.name}`} onClick={()=>setPreview({...item, preview_url: materialPreviewUrl(item)})}><MaterialThumbnail item={item}/></button>)}
            </div>}
            {row.role!=="user"&&row.turn_id&&onTrace&&!rows.slice(0,rowIndex).some(other=>other.role!=="user"&&other.turn_id===row.turn_id)&&<TurnActivity autoFollow={!rows.slice(rowIndex+1).some(other=>other.turn_id&&other.turn_id!==row.turn_id)} turnId={row.turn_id} onTrace={onTrace} hasBody={!!displayContent} partial={!!row.output_partial} truncated={!!row.output_truncated} truncationReason={row.output_truncation_reason} candidate={candidates.find(c => (c.turn_id || c.prepared_turn_id) === row.turn_id)} onDraft={onDraft} draftText={draftText}/>}

            <div className="chat-message-bubble">
              {row.role==="user"
                ? <UserMessageBody content={displayContent} skills={skills}/>
                : !!row.turn_id && rejectedGovernanceTurnIds.includes(row.turn_id)
                  ? <details data-testid="chat-rejected-governance-output"><summary>治理结果未通过校验；助手输出未经事实源确认，展开查看原文</summary>{!!displayContent && <SafeMarkdown content={displayContent}/>}</details>
                  : !!displayContent&&<SafeMarkdown content={displayContent}/>}
            </div>
            {row.role==="user"?<div className="chat-message-meta">
              {row.role==="user"&&effectiveConfig&&<><span className="chat-message-model" data-testid="chat-message-model">{effectiveConfig}{row.config_fallback_reason?` · ${row.config_fallback_reason}`:""}</span><span className="chat-message-sep">·</span></>}
              <time>{messageTime(row)}</time>
              <span className="chat-message-sep">·</span>
              <CopyMessageButton text={displayContent || row.content}/>
            </div>:<AssistantMeta row={row} skills={skills} displayContent={displayContent}/>}
          </div>
        </article>
      </div>{row.role==="user" && row.turn_id && <QuestionPanel turnId={row.turn_id}/>}
      {row.role==="user"&&row.turn_id&&onTrace&&!assistantTurnIds.has(row.turn_id)&&
        <div className="chat-message-block turn-assistant" data-testid="chat-pending-assistant">
          <article className="chat-message">
            <span className="chat-assistant-avatar" aria-hidden="true"><Box size={15}/></span>
            <div className="chat-assistant-col"><TurnActivity autoFollow={!rows.slice(rowIndex+1).some(other=>other.turn_id&&other.turn_id!==row.turn_id)} turnId={row.turn_id} onTrace={onTrace} candidate={candidates.find(c => (c.turn_id || c.prepared_turn_id) === row.turn_id)} onDraft={onDraft} draftText={draftText}/></div>
          </article>
        </div>}
      </Fragment>;
    })}
    {preview&&<MaterialPreviewDialog item={preview} onClose={()=>setPreview(null)}/>}
    {!atBottom && <button className="chat-jump-bottom" onClick={()=>{follow.current=true;root.current?.lastElementChild?.scrollIntoView?.({block:"end"});}}>回到最新消息</button>}
    {footer}
    <div aria-hidden="true"/>
  </div>;
}
