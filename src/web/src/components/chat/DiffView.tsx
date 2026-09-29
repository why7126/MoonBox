import { useState } from "react";
export type FileDiff = {
  path: string;
  status: string;
  previous_path?: string;
  patch?: string | null;
  reason?: string | null;
  before_size?: number | null;
  after_size?: number | null;
  workspace_status?: string | null;
};
export type DiffData = { available: boolean; reason?: string; files: FileDiff[]; cumulative_files?: FileDiff[] };
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

export function DiffView({ diff }: { diff: DiffData | null }) {
  const [scope, setScope] = useState("turn");
  const files = scope === "turn" ? diff?.files : diff?.cumulative_files;
  return <section className="chat-panel-section section-block" data-testid="chat-diff"><h3 className="section-title">文件变更</h3>
    <label className="range-row"><span className="range-label">比较范围</span><select className="round-select small" aria-label="Diff 比较范围" value={scope} onChange={e => setScope(e.target.value)}><option value="turn">本轮执行快照</option><option value="cumulative">会话累计快照</option></select></label>
    {diff?.available && <p className="diff-snapshot-note">这里展示执行结束时保存的差异快照；当前状态来自本地工作区实时校验。</p>}
    {!diff?.available ? <p>{diff?.reason || "尚无可信差异快照。"}</p> : !files ? <p>此轮未保存累计差异。</p> : !files.length ? <p>{scope === "turn" ? "本轮没有文件变更。" : "会话没有累计文件变更。"}</p> : <div className="file-diff-list">{files.map(file => <details className="chat-file-diff file-diff-row" key={file.path}>
      <summary><span className={`fd-badge ${file.status === "added" ? "add" : "mod"}`}>{fileStatusLabel(file)}</span> <span className="fd-path">{file.path}</span></summary>
      {file.previous_path && <p>原路径：{file.previous_path}</p>}
      <p>{file.before_size ?? 0} → {file.after_size ?? 0} 字节</p>
      {workspaceStatusText(file) && <p className={file.workspace_status === "mismatch" ? "diff-workspace-warning" : "diff-workspace-status"}>{workspaceStatusText(file)}</p>}
      {file.reason ? <p>{file.reason}；仅展示文件元数据。</p> : file.patch ? <pre>{file.patch.split("\n").map((line, i) => <span className={line.startsWith("+") ? "chat-diff-add" : line.startsWith("-") ? "chat-diff-remove" : ""} key={i}>{line}{"\n"}</span>)}</pre> : <p>内容未变化，仅文件元数据发生变化。</p>}
    </details>)}</div>}
  </section>;
}
