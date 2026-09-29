import { useEffect, useMemo, useState } from "react";
import { Archive, Pencil, Pin, RotateCcw, Search, Trash2 } from "lucide-react";
import { ChatDialog } from "./ChatDialog";
import { chatRequest, type ConversationRead } from "./chatApi";
import type { useChatWorkbench } from "./useChatWorkbench";
export type SessionDialog = { kind: "history" } | { kind: "rename" | "delete"; row: ConversationRead } | null;
export function SessionDialogs({ model: m, dialog, setDialog }: { model: ReturnType<typeof useChatWorkbench>; dialog: SessionDialog; setDialog: (value: SessionDialog) => void }) {
  const [title, setTitle] = useState(dialog?.kind === "rename" ? dialog.row.title : "");
  const [deletion, setDeletion] = useState<{ allowed: boolean; reason?: string; workspace_hash?: string | null } | null>(null);
  const groupedSessions = useMemo(() => {
    const now = Date.now(), week = 7 * 24 * 60 * 60 * 1000;
    const groups = [
      { label: "置顶", rows: m.sessions.filter(row => row.pinned) },
      { label: "最近 7 天", rows: m.sessions.filter(row => !row.pinned && now - new Date(row.updated_at).getTime() <= week) },
      { label: "更早", rows: m.sessions.filter(row => !row.pinned && now - new Date(row.updated_at).getTime() > week) },
    ];
    return groups.filter(group => group.rows.length);
  }, [m.sessions]);
  useEffect(() => {
    if (dialog?.kind !== "delete") return;
    const controller = new AbortController();
    chatRequest<{ allowed: boolean; reason?: string; workspace_hash?: string | null }>(`/conversations/${dialog.row.id}/deletion-check`, { signal: controller.signal }).then(data => { if (!controller.signal.aborted) setDeletion(data); }).catch(e => { if (!controller.signal.aborted) setDeletion({ allowed: false, reason: e.message }); });
    return () => controller.abort();
  }, []);
  if (!dialog) return null;
  const close = () => { if (!m.busy) { m.setError(""); setDialog(null); } };
  const cancel = <button type="button" data-testid="chat-modal-cancel" disabled={m.busy} onClick={close}>取消</button>;
  if (dialog.kind === "history") return <ChatDialog title="会话历史" testId="chat-history-dialog" busy={m.busy} onClose={close} footer={<><span>{m.total} 个会话</span><button disabled={m.page === 1 || m.loading} onClick={() => m.setPage(m.page - 1)}>上一页</button><span>{m.page}</span><button disabled={m.page * 20 >= m.total || m.loading} onClick={() => m.setPage(m.page + 1)}>下一页</button></>}>
    <p className="chat-history-privacy">会话仅本人可查看，同时遵循空间、仓库与关联对象权限。</p>
    <div className="chat-history-filter"><label className="chat-history-search"><Search size={15} /><input aria-label="搜索会话" placeholder="搜索标题或关联对象" value={m.query} onChange={e => { m.setQuery(e.target.value); m.setPage(1); }} /></label><select aria-label="历史状态" value={String(m.archived)} onChange={e => { m.setArchived(e.target.value === "all" || e.target.value === "pinned" ? e.target.value : e.target.value === "true"); m.setPage(1); }}><option value="all">全部</option><option value="pinned">置顶</option><option value="false">进行中</option><option value="true">已归档</option></select></div>
    {m.error && <p role="alert" className="chat-error">{m.error}</p>}
    {m.loading ? <p role="status">正在读取会话…</p> : !m.sessions.length ? <p className="chat-history-empty">暂无匹配会话</p> : <div className="chat-history-list">
      {groupedSessions.map(group => <section key={group.label} className="chat-history-group" aria-label={group.label}>
        <h3>{group.label}</h3>
        {group.rows.map(row => <article className={`chat-history-row ${row.pinned ? "is-pinned" : ""}`} key={row.id}>
          <button className="chat-session-title" onClick={() => { m.setSelected(row); close(); }}>{row.pinned && <Pin size={13} fill="currentColor" />}<span>{row.title}</span><small>{row.repository_id} · {new Date(row.updated_at).toLocaleString()}</small></button>
          <div className="chat-history-actions" aria-label={`${row.title} 操作`}>
            <button aria-label={row.pinned ? "取消置顶" : "置顶"} title={row.pinned ? "取消置顶" : "置顶"} disabled={m.busy} onClick={() => void m.patch(row, { pinned: !row.pinned })}><Pin size={14} fill={row.pinned ? "currentColor" : "none"} /></button>
            <button aria-label="重命名" title="重命名" data-testid="chat-rename-trigger" disabled={m.busy} onClick={() => setDialog({ kind: "rename", row })}><Pencil size={14} /></button>
            <button aria-label={row.archived ? "恢复" : "归档"} title={row.archived ? "恢复" : "归档"} data-testid={row.archived ? "chat-restore" : "chat-archive"} disabled={m.busy || Boolean(row.active_turn_id)} onClick={() => void m.patch(row, { archived: !row.archived })}>{row.archived ? <RotateCcw size={14} /> : <Archive size={14} />}</button>
            <button aria-label="删除" title="删除" className="danger" data-testid="chat-delete-trigger" disabled={m.busy || Boolean(row.active_turn_id)} onClick={() => setDialog({ kind: "delete", row })}><Trash2 size={14} /></button>
          </div>
        </article>)}
      </section>)}
    </div>}
  </ChatDialog>;
  if (dialog.kind === "rename") return <ChatDialog title="重命名会话" testId="chat-rename-dialog" busy={m.busy} onClose={close} footer={<>{cancel}<button data-testid="chat-modal-submit" disabled={m.busy || !title.trim()} onClick={async () => { if (await m.patch(dialog.row, { title: title.trim() })) setDialog(null); }}>{m.busy ? "保存中…" : "保存"}</button></>}>
    <label>会话标题<input aria-label="会话标题" maxLength={200} value={title} onChange={e => setTitle(e.target.value)} /></label>{m.error && <p role="alert" className="chat-error">{m.error}</p>}
  </ChatDialog>;
  if (dialog.kind !== "delete") return null;
  return <ChatDialog title="删除会话" testId="chat-delete-confirm" busy={m.busy} onClose={close} footer={<>{cancel}<button data-testid="chat-modal-submit" disabled={m.busy || !deletion?.allowed} onClick={async () => { if (await m.remove(dialog.row, deletion?.workspace_hash)) setDialog(null); }}>{m.busy ? "删除中…" : "确认删除"}</button></>}>
    <p>确认删除“{dialog.row.title}”？代码将独立保留。历史正文删除后无法在会话中恢复，执行副本和备份将按配置单独跟踪清理，不会立即宣称彻底删除。</p>{!deletion ? <p role="status">正在检查工作区及清理条件…</p> : !deletion.allowed && <p role="alert">{deletion.reason || "当前无法删除"}</p>}{m.error && <p role="alert" className="chat-error">{m.error}</p>}
  </ChatDialog>;
}
