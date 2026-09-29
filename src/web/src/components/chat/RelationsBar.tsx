import { useEffect, useRef, useState, type ReactNode } from "react";
import { ChatDialog } from "./ChatDialog";
import { chatRequest, type ConversationRead } from "./chatApi";
type ObjectKind = "REQ" | "BUG" | "OBJECT";
type ObjectItem = { id: string; title: string; version?: string; kind?: ObjectKind | string };
type Relations = { primary: ObjectItem | null; references: ObjectItem[] };
const empty: Relations = { primary: null, references: [] };
function objectKind(item: Pick<ObjectItem, "id" | "kind">): ObjectKind {
  if (item.kind === "REQ" || item.kind === "BUG") return item.kind;
  if (item.id.startsWith("REQ-")) return "REQ";
  if (item.id.startsWith("BUG-")) return "BUG";
  return "OBJECT";
}
function normalizeItems(items: ObjectItem[]) {
  return items.map(item => ({ ...item, kind: objectKind(item) }));
}
export function RelationsBar({ conversation, onSaved, projectStatus }: { conversation: ConversationRead | null; onSaved?: (relations: Relations) => void; projectStatus?: ReactNode }) {
  const [value, setValue] = useState<Relations>(empty), [open, setOpen] = useState(false), [error, setError] = useState("");
  const [candidates, setCandidates] = useState<ObjectItem[]>([]), [candidatesLoading, setCandidatesLoading] = useState(false), [candidatesReason, setCandidatesReason] = useState("");
  useEffect(() => {
    setValue(empty); setCandidates([]); setCandidatesReason(""); setCandidatesLoading(false); setError(""); setOpen(false);
    if (!conversation) return;
    const controller = new AbortController();
    chatRequest<Relations>(`/conversations/${conversation.id}/relations`, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) setValue(data);
    }).catch(e => { if (!controller.signal.aborted) setError(e.message); });
    setCandidatesLoading(true);
    chatRequest<{ items: ObjectItem[]; reason?: string }>(`/conversations/${conversation.id}/objects`, { signal: controller.signal }).then(data => {
      if (!controller.signal.aborted) { setCandidates(normalizeItems(data.items)); setCandidatesReason(data.reason || ""); setCandidatesLoading(false); }
    }).catch(e => { if (!controller.signal.aborted) { setCandidates([]); setCandidatesReason(e.message); setCandidatesLoading(false); } });
    return () => controller.abort();
  }, [conversation?.id]);
  return <><div className="chat-relations-bar" data-testid="chat-relations-bar">
    {projectStatus}
    <span>主对象 <b>{value.primary?.id || "未关联"}</b>{!!value.references?.length && <span> · {value.references.length} 个引用</span>}</span>
    <button type="button" disabled={!conversation || !!conversation.archived || !!conversation.active_turn_id} data-testid="chat-relations-trigger" onClick={() => setOpen(true)}>管理关联</button>
  </div>{error && <p className="chat-error" role="alert">{error}</p>}
    {open && conversation && <RelationsDialog conversationId={conversation.id} initial={value} initialCandidates={candidates} initialLoading={candidatesLoading} initialReason={candidatesReason} onClose={() => setOpen(false)} onSave={data => { setValue(data); setError(""); setOpen(false); onSaved?.(data); }} />}</>;
}
export function RelationsDialog({ conversationId, initial, initialCandidates = [], initialLoading = false, initialReason = "", onClose, onSave }: { conversationId: string; initial: Relations; initialCandidates?: ObjectItem[]; initialLoading?: boolean; initialReason?: string; onClose: () => void; onSave: (value: Relations) => void }) {
  const [primary, setPrimary] = useState(initial.primary?.id || ""), [references, setReferences] = useState(initial.references?.map(r => r.id) || []);
  const [items, setItems] = useState<ObjectItem[]>(() => normalizeItems([...(initial.primary ? [initial.primary] : []), ...(initial.references || []), ...initialCandidates]));
  const [query, setQuery] = useState(() => new URLSearchParams(window.location.search).get("object_id") || "");
  const [loading, setLoading] = useState(initialLoading && !initialCandidates.length), [refreshing, setRefreshing] = useState(initialLoading && !!initialCandidates.length);
  const [loadedOnce, setLoadedOnce] = useState(!!initialCandidates.length || !!initialReason || !initialLoading);
  const [busy, setBusy] = useState(false), [error, setError] = useState(""), [reason, setReason] = useState(initialReason);
  const pending = useRef(false);
  useEffect(() => {
    const controller = new AbortController();
    if (loadedOnce) setRefreshing(true); else setLoading(true);
    const timer = setTimeout(() => {
      chatRequest<{ items: ObjectItem[]; reason?: string }>(`/conversations/${conversationId}/objects?q=${encodeURIComponent(query)}`, { signal: controller.signal }).then(data => {
        if (controller.signal.aborted) return;
        setItems(normalizeItems([...(initial.primary ? [initial.primary] : []), ...(initial.references || []), ...data.items]));
        setReason(data.reason || ""); setLoadedOnce(true); setLoading(false); setRefreshing(false);
      }).catch(e => { if (!controller.signal.aborted) { setError(e.message); setLoadedOnce(true); setLoading(false); setRefreshing(false); } });
    }, 150);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [conversationId, query]);
  function setPrimaryObject(id: string) {
    setPrimary(id);
    setReferences(current => current.filter(value => value !== id));
  }
  function toggleReference(id: string, checked: boolean) {
    setReferences(current => checked ? [...current, id].slice(0, 10) : current.filter(value => value !== id));
  }
  async function save() {
    if (pending.current) return;
    pending.current = true; setBusy(true); setError("");
    try { onSave(await chatRequest<Relations>(`/conversations/${conversationId}/relations`, { method: "PUT", body: JSON.stringify({ primary: primary || null, references }) })); }
    catch (e) { setError(e instanceof Error ? e.message : "保存失败"); }
    finally { pending.current = false; setBusy(false); }
  }
  const uniqueItems = [...new Map(items.map(item => [item.id, item])).values()];
  return <ChatDialog title="管理关联" testId="chat-relations-dialog" busy={busy} onClose={onClose} footer={<><button type="button" disabled={busy} data-testid="chat-modal-cancel" onClick={onClose}>取消</button><button type="button" disabled={busy || loading} data-testid="chat-modal-submit" onClick={save}>{busy ? "保存中…" : "保存关联"}</button></>}>
    <p>关联调整仅影响下一轮。已有轮次保留当时的引用快照。取消或关闭会丢弃本次调整。</p>
    <label className="chat-relation-combobox">关联对象
      <input role="combobox" aria-label="搜索关联对象" aria-controls="chat-relation-listbox" aria-expanded="true" value={query} disabled={busy} onChange={e => setQuery(e.target.value)} placeholder="搜索编号或标题，直接在列表中设为主对象或引用对象" />
    </label>
    <div className="chat-relation-selection" aria-live="polite">
      <span>主对象 <b>{primary || "未关联"}</b></span>
      {!!primary && <button type="button" disabled={busy} onClick={() => setPrimary("")}>清除主对象</button>}
      {!!references.length && <span>引用 {references.length}/10</span>}
    </div>
    <fieldset disabled={busy} className="chat-relation-options"><legend>对象候选（搜索、主对象与引用对象合并）</legend>
      {refreshing && <p className="chat-relation-refresh" role="status">正在更新候选…</p>}
      {loading ? <p role="status">正在读取授权对象…</p> : !uniqueItems.length ? <p>{reason || "没有匹配的可访问对象"}</p> : <div id="chat-relation-listbox" role="listbox" aria-label="可关联对象">
        {uniqueItems.map(item => {
          const kind = objectKind(item);
          return <div key={item.id} className={`chat-relation-row type-${kind}`} role="option" aria-selected={primary === item.id || references.includes(item.id)}>
            <span className="chat-relation-kind">{kind}</span>
            <span className="chat-relation-text"><b>{item.id}</b><small>{item.title}</small></span>
            <span className="chat-relation-actions">
              <label><input type="radio" name="chat-primary-object" aria-label={`设为主对象 ${item.id}`} checked={primary === item.id} onChange={() => setPrimaryObject(item.id)} />主对象</label>
              <label><input type="checkbox" aria-label={`引用 ${item.id}`} checked={references.includes(item.id)} disabled={item.id === primary || (!references.includes(item.id) && references.length >= 10)} onChange={e => toggleReference(item.id, e.target.checked)} />引用</label>
            </span>
          </div>;
        })}
      </div>}
    </fieldset>
    {!!references.length && <p className="chat-relation-chips">已选引用：{references.map(id => <button type="button" key={id} disabled={busy} aria-label={`移除 ${id}`} onClick={() => setReferences(current => current.filter(value => value !== id))}>{id} ×</button>)}</p>}
    {error && <p role="alert" className="chat-error">{error}</p>}
  </ChatDialog>;
}
