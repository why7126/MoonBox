import { useEffect, useRef, useState, type ReactNode } from "react";
import { ChatDialog } from "./ChatDialog";
import { chatRequest, type ConversationRead } from "./chatApi";
type ObjectItem = { id: string; title: string; version?: string };
type Relations = { primary: ObjectItem | null; references: ObjectItem[] };
const empty: Relations = { primary: null, references: [] };
export function RelationsBar({ conversation, onSaved, projectStatus }: { conversation: ConversationRead | null; onSaved?: () => void; projectStatus?: ReactNode }) {
  const [value, setValue] = useState<Relations>(empty), [open, setOpen] = useState(false), [error, setError] = useState("");
  useEffect(() => {
    setValue(empty); setError(""); setOpen(false);
    if (!conversation) return;
    const controller = new AbortController();
    chatRequest<Relations>(`/conversations/${conversation.id}/relations`, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setValue(data);
    }).catch(e => { if (!controller.signal.aborted) setError(e.message); });
    return () => controller.abort();
  }, [conversation?.id]);
  return <><div className="chat-relations-bar" data-testid="chat-relations-bar">
    {projectStatus}
    <span>主对象 <b>{value.primary?.id || "未关联"}</b>{!!value.references?.length && <span> · {value.references.length} 个引用</span>}</span>
    <button type="button" disabled={!conversation || !!conversation.archived || !!conversation.active_turn_id} data-testid="chat-relations-trigger" onClick={() => setOpen(true)}>管理关联</button>
  </div>{error && <p className="chat-error" role="alert">{error}</p>}
    {open && conversation && <RelationsDialog conversationId={conversation.id} initial={value} onClose={() => setOpen(false)} onSave={data => { setValue(data); setError(""); setOpen(false); onSaved?.(); }} />}</>;
}
export function RelationsDialog({ conversationId, initial, onClose, onSave }: { conversationId: string; initial: Relations; onClose: () => void; onSave: (value: Relations) => void }) {
  const [primary, setPrimary] = useState(initial.primary?.id || ""), [references, setReferences] = useState(initial.references?.map(r => r.id) || []);
  const [known, setKnown] = useState<ObjectItem[]>([...(initial.primary ? [initial.primary] : []), ...(initial.references || [])]);
  const [items, setItems] = useState<ObjectItem[]>([]), [query, setQuery] = useState(() => new URLSearchParams(window.location.search).get("object_id") || "");
  const [loading, setLoading] = useState(true), [busy, setBusy] = useState(false), [error, setError] = useState(""), [reason, setReason] = useState("");
  const pending = useRef(false);
  useEffect(() => {
    const controller = new AbortController(); setLoading(true);
    const timer = setTimeout(() => {
      chatRequest<{ items: ObjectItem[]; reason?: string }>(`/conversations/${conversationId}/objects?q=${encodeURIComponent(query)}`, { signal: controller.signal }).then(data => {
        if (controller.signal.aborted) return;
        setItems(data.items); setKnown(current => [...new Map([...current, ...data.items].map(r => [r.id, r])).values()]); setReason(data.reason || ""); setLoading(false);
      }).catch(e => { if (!controller.signal.aborted) { setItems([]); setError(e.message); setLoading(false); } });
    }, 150);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [conversationId, query]);
  async function save() {
    if (pending.current) return;
    pending.current = true; setBusy(true); setError("");
    try { onSave(await chatRequest<Relations>(`/conversations/${conversationId}/relations`, { method: "PUT", body: JSON.stringify({ primary: primary || null, references }) })); }
    catch (e) { setError(e instanceof Error ? e.message : "保存失败"); }
    finally { pending.current = false; setBusy(false); }
  }
  return <ChatDialog title="管理关联" testId="chat-relations-dialog" busy={busy} onClose={onClose} footer={<><button type="button" disabled={busy} data-testid="chat-modal-cancel" onClick={onClose}>取消</button><button type="button" disabled={busy || loading} data-testid="chat-modal-submit" onClick={save}>{busy ? "保存中…" : "保存关联"}</button></>}>
    <p>关联调整仅影响下一轮。已有轮次保留当时的引用快照。取消或关闭会丢弃本次调整。</p>
    <label>搜索对象<input aria-label="搜索关联对象" value={query} disabled={busy} onChange={e => setQuery(e.target.value)} placeholder="编号或标题" /></label>
    <label>主对象<select aria-label="主对象" value={primary} disabled={busy} onChange={e => { setPrimary(e.target.value); setReferences(current => current.filter(id => id !== e.target.value)); }}><option value="">不关联主对象</option>{known.map(item => <option key={item.id} value={item.id}>{item.id} · {item.title}</option>)}</select></label>
    <fieldset disabled={busy} className="chat-relation-options"><legend>引用对象（最多 10 个）</legend>{loading ? <p role="status">正在读取授权对象…</p> : !items.length ? <p>{reason || "没有匹配的可访问对象"}</p> : items.map(item => <label key={item.id}><input type="checkbox" aria-label={`引用 ${item.id}`} checked={references.includes(item.id)} disabled={item.id === primary || (!references.includes(item.id) && references.length >= 10)} onChange={e => setReferences(current => e.target.checked ? [...current, item.id] : current.filter(id => id !== item.id))} /><span>{item.id}<small>{item.title}</small></span></label>)}</fieldset>
    {!!references.length && <p>已选引用：{references.map(id => <button type="button" key={id} disabled={busy} aria-label={`移除 ${id}`} onClick={() => setReferences(current => current.filter(value => value !== id))}>{id} ×</button>)}</p>}
    {error && <p role="alert" className="chat-error">{error}</p>}
  </ChatDialog>;
}
