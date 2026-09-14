import { useLayoutEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { chatRequest, type Capabilities, type ConversationRead, type TurnRead } from "./chatApi";

/** 内存草稿同时保留不确定请求的标识，切换历史后重试仍复用原请求。 */
export type DraftState = { text: string; repository?: string; creationId?: string; conversation?: ConversationRead; request?: { prompt: string; id: string } };
export function Composer({ conversation, capabilities, onSubmitted, initialDraft, onDraft, unavailableReason, draftState, onCreated, onBusyChange, spaceId }: { spaceId?: string; unavailableReason?: string; initialDraft: string; onDraft: (value: string) => void; conversation: ConversationRead | null; capabilities: Capabilities | null; onSubmitted: () => void; draftState?: DraftState; onCreated?: (row: ConversationRead) => void; onBusyChange?: (busy: boolean) => void }) {
  const fallback = useRef<DraftState>({ text: initialDraft });
  const attempt = draftState || fallback.current;
  const [draft, setDraft] = useState(attempt.text), [busy, setBusy] = useState(false), [error, setError] = useState("");
  const [chosen, setChosen] = useState(attempt.repository || "");
  const input = useRef<HTMLTextAreaElement>(null), pending = useRef(false);
  const repositories = capabilities?.repositories || [];
  const repository = repositories.some(row => row.id === chosen) ? chosen : !chosen && repositories.length === 1 ? repositories[0].id : "";
  const disabled = !!conversation?.archived || !!conversation?.active_turn_id || !capabilities?.execution_ready || (!conversation && (!repository || !onCreated || !spaceId));
  const hint = unavailableReason || (!capabilities?.execution_ready ? capabilities?.reason || "执行服务未就绪 · 可先编写草稿" : conversation?.archived ? "已归档 · 只读" : conversation?.active_turn_id ? "原运行尚未终止 · 可先编写草稿" : !conversation && !repository ? "请选择本次对话使用的仓库" : "");
  useLayoutEffect(() => { if (input.current) { input.current.style.height = "auto"; input.current.style.height = `${Math.min(200,Math.max(44,input.current.scrollHeight))}px`; } }, [draft]);
  async function send() {
    if (pending.current || disabled || !draft.trim()) return;
    if (!attempt.request || attempt.request.prompt !== draft) attempt.request = { prompt: draft, id: crypto.randomUUID() };
    pending.current = true; setBusy(true); onBusyChange?.(true); setError("");
    try {
      let target = conversation || attempt.conversation;
      if (!target) {
        attempt.creationId ||= crypto.randomUUID(); attempt.repository = repository; setChosen(repository);
        target = await chatRequest<ConversationRead>("/conversations", { method: "POST", body: JSON.stringify({ space_id: spaceId, repository_id: repository, title: draft.trim().slice(0,80), client_request_id: attempt.creationId }) });
        attempt.conversation = target;
      }
      const turn = await chatRequest<TurnRead>(`/conversations/${target.id}/turns`, { method: "POST", body: JSON.stringify({ prompt: attempt.request.prompt, client_request_id: attempt.request.id }) });
      attempt.text = ""; attempt.request = undefined; attempt.creationId = undefined; attempt.conversation = undefined; setDraft(""); onDraft("");
      if (!conversation) onCreated?.({ ...target, active_turn_id: turn.id });
      onSubmitted();
    } catch (e) { setError(e instanceof Error ? e.message : "发送失败，草稿已保留"); }
    finally { pending.current = false; setBusy(false); onBusyChange?.(false); }
  }
  return <div className="chat-composer" data-testid="chat-composer">
    {!conversation && <label className="chat-draft-repository">仓库 <select aria-label="会话仓库" data-testid="chat-draft-repository" value={repository} disabled={busy || !!attempt.creationId || !repositories.length} onChange={e => { setChosen(e.target.value); attempt.repository = e.target.value; }}><option value="" disabled>{repositories.length ? "选择仓库" : "暂无可用仓库"}</option>{repositories.map(row => <option key={row.id} value={row.id}>{row.id}</option>)}</select></label>}
    <label className="chat-input-label" htmlFor="chat-prompt">消息</label>
    <textarea ref={input} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing && e.keyCode !== 229) { e.preventDefault(); void send(); } }} id="chat-prompt" data-testid="chat-prompt" maxLength={32000} value={draft} onChange={e => { setDraft(e.target.value); attempt.text = e.target.value; onDraft(e.target.value); }} placeholder="发消息或描述任务…" disabled={!!conversation?.archived || busy} aria-describedby={hint ? "chat-composer-hint" : undefined} />
    {error && <p role="alert" className="chat-error">{error}</p>}
    <div className="chat-composer-actions">{hint && <span id="chat-composer-hint">{hint}</span>}<button type="button" className="chat-send" data-testid="chat-send" disabled={disabled || busy || !draft.trim()} onClick={() => void send()}><Send size={14} />{busy ? "发送中…" : "发送"}</button></div>
  </div>;
}
