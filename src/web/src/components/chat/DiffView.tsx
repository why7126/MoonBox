import { useState } from "react";
export type FileDiff = { path: string; status: string; previous_path?: string; patch?: string | null; reason?: string | null; before_size?: number | null; after_size?: number | null };
export type DiffData = { available: boolean; reason?: string; files: FileDiff[]; cumulative_files?: FileDiff[] };
const labels: Record<string, string> = { added: "新增", deleted: "删除", modified: "修改", renamed: "重命名" };
export function DiffView({ diff }: { diff: DiffData | null }) {
  const [scope, setScope] = useState("turn");
  const files = scope === "turn" ? diff?.files : diff?.cumulative_files;
  return <section className="chat-panel-section" data-testid="chat-diff"><h3>文件变更</h3>
    <label>比较范围<select aria-label="Diff 比较范围" value={scope} onChange={e => setScope(e.target.value)}><option value="turn">本轮变更</option><option value="cumulative">会话累计变更</option></select></label>
    {!diff?.available ? <p>{diff?.reason || "尚无可信差异快照。"}</p> : !files ? <p>此轮未保存累计差异。</p> : !files.length ? <p>{scope === "turn" ? "本轮没有文件变更。" : "会话没有累计文件变更。"}</p> : files.map(file => <details className="chat-file-diff" key={file.path}>
      <summary><span className="chat-badge">{labels[file.status] || file.status}</span> {file.path}</summary>
      {file.previous_path && <p>原路径：{file.previous_path}</p>}
      <p>{file.before_size ?? 0} → {file.after_size ?? 0} 字节</p>
      {file.reason ? <p>{file.reason}；仅展示文件元数据。</p> : file.patch ? <pre>{file.patch.split("\n").map((line, i) => <span className={line.startsWith("+") ? "chat-diff-add" : line.startsWith("-") ? "chat-diff-remove" : ""} key={i}>{line}{"\n"}</span>)}</pre> : <p>内容未变化，仅文件元数据发生变化。</p>}
    </details>)}
  </section>;
}
