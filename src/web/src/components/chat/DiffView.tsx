import { useEffect, useState } from "react";
import { chatRequest } from "./chatApi";
import { FileContent } from "./FileContent";
export type FileDiff = {
  file_id?: string;
  before_file_id?: string;
  path: string;
  status: string;
  previous_path?: string;
  patch?: string | null;
  reason?: string | null;
  before_size?: number | null;
  after_size?: number | null;
  workspace_status?: string | null;
};
export type DiffData = { available: boolean; reason?: string; files: FileDiff[]; cumulative_files?: FileDiff[]; format_version?: number };
const labels: Record<string, string> = { added: "新增", deleted: "删除", modified: "修改", renamed: "重命名" };

function fileStatusLabel(file: FileDiff) {
  if (file.status === "added" && file.workspace_status === "untracked") return "新增（未跟踪）";
  return labels[file.status] || file.status;
}

function workspaceStatusText(file: FileDiff) {
  if (file.workspace_status === "untracked") return "当前工作区：未跟踪";
  if (file.workspace_status === "mismatch") return "快照内容与当前磁盘内容不一致，页面展示的是执行快照。";
  if (file.workspace_status === "missing") return "当前工作区：文件不存在";
  if (file.workspace_status === "present") return "当前工作区：文件存在";
  if (file.workspace_status === "unknown") return "当前工作区状态暂不可确认";
  return null;
}

export function DiffView({ diff, turnId }: { diff: DiffData | null; turnId?: string }) {
  const [scope, setScope] = useState("turn");
  const [batch, setBatch] = useState<{ files: FileDiff[]; next_cursor: string | null } | null>(null);
  const [cursor, setCursor] = useState<string | null>(null), [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    setBatch(null); setError("");
    if (!turnId || diff?.format_version !== 2) return;
    const controller = new AbortController(); setBusy(true);
    const query = new URLSearchParams({ scope }); if (cursor) query.set("cursor", cursor);
    void chatRequest<{ files: FileDiff[]; next_cursor: string | null }>(`/turns/${turnId}/files?${query}`, { signal: controller.signal })
      .then(value => { if (!controller.signal.aborted) setBatch(value); })
      .catch(cause => { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : "文件列表读取失败"); })
      .finally(() => { if (!controller.signal.aborted) setBusy(false); });
    return () => controller.abort();
  }, [turnId, diff?.format_version, scope, cursor, retry]);
  const files = batch?.files || (scope === "turn" ? diff?.files : diff?.cumulative_files);
  return <section className="chat-panel-section section-block" data-testid="chat-diff"><h3 className="section-title">文件变更</h3>
    <label className="range-row"><span className="range-label">比较范围</span><select className="round-select small" aria-label="Diff 比较范围" value={scope} onChange={e => { setCursor(null); setScope(e.target.value); }}><option value="turn">本轮执行快照</option><option value="cumulative">会话累计快照</option></select></label>
    {error && <p role="alert">{error} <button onClick={() => setRetry(value => value + 1)}>重试读取</button></p>}
    {busy && <p role="status">正在读取文件列表…</p>}
    {batch?.next_cursor && <button disabled={busy} onClick={() => setCursor(batch.next_cursor)}>读取下一页文件</button>}
    {cursor && <button disabled={busy} onClick={() => setCursor(null)}>从头读取文件</button>}
    {diff?.available && <p className="diff-snapshot-note">这里展示执行时保存的差异快照。未提供当前工作区状态时，不代表文件仍与磁盘一致。</p>}
    {!diff?.available ? <p>{diff?.reason || "尚无可信差异快照。"}</p> : !files ? <p>此轮未保存累计差异。</p> : !files.length ? <p>{scope === "turn" ? "本轮没有文件变更。" : "会话没有累计文件变更。"}</p> : <div className="file-diff-list">{files.map(file => <details className="chat-file-diff file-diff-row" key={file.path}>
      <summary><span className={`fd-badge ${file.status === "added" ? "add" : "mod"}`}>{fileStatusLabel(file)}</span> <span className="fd-path">{file.path}</span></summary>
      {file.previous_path && <p>原路径：{file.previous_path}</p>}
      {turnId && file.file_id && <FileContent turnId={turnId} fileId={file.file_id} beforeFileId={file.before_file_id} scope={scope} />}
      <p>{file.before_size ?? 0} → {file.after_size ?? 0} 字节</p>
      {workspaceStatusText(file) && <p className={file.workspace_status === "mismatch" ? "diff-workspace-warning" : "diff-workspace-status"}>{workspaceStatusText(file)}</p>}
      {file.reason ? <p>{file.reason}。</p> : file.patch ? <pre>{file.patch.split("\n").map((line, i) => <span className={line.startsWith("+") ? "chat-diff-add" : line.startsWith("-") ? "chat-diff-remove" : ""} key={i}>{line}{"\n"}</span>)}</pre> : <p>内容未变化，仅文件元数据发生变化。</p>}
    </details>)}</div>}
  </section>;
}
