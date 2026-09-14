import { governanceRequest, type Application } from "../workbench/governanceApi";
import { useEffect, useRef, useState } from "react";
import "../../styles/project-governance.css";
export type GovernanceCandidate = { id: string; object_id: string; state: string; files: {path: string; diff: string}[]; manifest_hash: string; revision: string | number };
export function GovernanceResult({ candidate, previewOnly = false }: { candidate?: GovernanceCandidate; previewOnly?: boolean }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const trigger = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [operation, setOperation] = useState<Application | null>(null);
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  const key = useRef(crypto.randomUUID());
  const candidateId = candidate?.id;
  useEffect(() => { setOpen(false); setConfirmed(false); setOperation(null); setError(""); key.current = crypto.randomUUID(); }, [candidateId]);
  useEffect(() => {
    if (!candidateId || previewOnly) return;
    const stored = sessionStorage.getItem(`moonbox.governance.operation:${candidateId}`);
    if (!stored) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const row = await governanceRequest<Application>(`/api/v1/chat/governance-applications/${encodeURIComponent(stored)}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setOperation(row);
        if (["pending", "applying", "recovering"].includes(row.state)) timer = setTimeout(poll, 1000);
      } catch (e) { if (!controller.signal.aborted) { setError(e instanceof Error ? e.message : "应用状态读取失败"); timer = setTimeout(poll, 3000); } }
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [candidateId, previewOnly, busy]);
  const apply = async () => {
    if (!candidate || !confirmed || busy || previewOnly) return;
    setBusy(true); setError("");
    try {
      const row = await governanceRequest<Application>(`/api/v1/chat/governance-candidates/${candidate.id}/applications`, { method: "POST", body: JSON.stringify({ expected_manifest_hash: candidate.manifest_hash, candidate_revision: Number(candidate.revision), idempotency_key: key.current, maintenance_confirmed: true }) });
      sessionStorage.setItem(`moonbox.governance.operation:${candidate.id}`, row.id); setOperation(row);
    } catch (e) { setError(e instanceof Error ? e.message : "应用请求失败，可重试"); }
    finally { setBusy(false); }
  };
  const state = operation?.state || candidate?.state || "";
  const labels: Record<string, string> = { prepared: "等待发送", running: "正在生成", pending: operation ? "排队应用" : "待应用成果", applying: "正在应用", recovering: "正在恢复", recovery_blocked: "恢复已暂停", conflict: "版本冲突", failed: "应用失败", rejected: "成果未通过校验", applied: "已应用" };
  useEffect(() => { if (open) dialog.current?.showModal(); else dialog.current?.close(); }, [open]);
  const close = () => { setOpen(false); trigger.current?.focus(); };
  if (!candidate) return null;
  return <section className="pg-result" aria-label="治理成果">
    <div><strong>{candidate.object_id}</strong><span className="pg-badge">{labels[state] || state}{previewOnly ? " · 模拟" : ""}</span></div>
    <p>{state === "prepared" ? "建议指令已填入输入框，请检查后手动发送。" : state === "rejected" ? "本轮结果未满足治理文件范围与状态约束，可在轨迹中查看执行结果。" : "执行成果保存在独立副本中。审阅完整差异后，再应用到项目。"}</p>
    <button ref={trigger} data-testid="governance-result-preview" disabled={!candidate.files.length} onClick={() => setOpen(true)}>查看成果 · {candidate.files.length} 个文件</button>
    <dialog ref={dialog} className="pg-dialog" data-testid="governance-apply-dialog" aria-labelledby="pg-result-title" onCancel={event => { event.preventDefault(); close(); }} onClickCapture={event => {
      if (event.target !== event.currentTarget) return;
      const rect=event.currentTarget.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) close();
    }}>
      <header><div><h2 id="pg-result-title">审阅治理成果</h2><p>{candidate.object_id}{previewOnly ? " · Skeleton 模拟数据" : ""}</p></div><button data-testid="governance-apply-close" onClick={close}>关闭</button></header>
      <div className="pg-dialog-body"><p>本次应用文件</p><ul>{candidate.files.map(file => <li key={file.path}>{file.path}</li>)}</ul>
        {candidate.files.map(file => <section key={file.path}><h3>{file.path}</h3><pre>{file.diff}</pre></section>)}
        <p className="pg-notice">应用前请暂停其他编辑器和脚本的写入。系统会重新检查源文件版本；发现冲突时整批停止。</p>
        <p role="status" data-testid="governance-application-state">{previewOnly ? "此预览不执行请求、不写入仓库。" : labels[state] || state}</p>
        {state === "conflict" && <p>源文件已变化，本次未完成应用。请从需求卡片重新准备会话。</p>}
        {state === "recovery_blocked" && <p role="alert">发现无法自动确认的文件状态，已保留现场并暂停写入。请联系管理员核对恢复记录。</p>}
        {state === "applied" && <p>项目文件已更新，需求中心将自动同步。</p>}
        {error && <p role="alert">{error}</p>}
        <label><input type="checkbox" data-testid="governance-maintenance-confirm" checked={confirmed} disabled={previewOnly || state !== "pending" || Boolean(operation)} onChange={event => setConfirmed(event.target.checked)} />我已暂停其他编辑器和脚本的写入，并确认当前维护窗口有效</label>
      </div>
      <footer><span>确认后才更新项目事实源</span><button data-testid="governance-apply-confirm" onClick={() => void apply()} disabled={previewOnly || !confirmed || busy || state !== "pending" || Boolean(operation)}>确认应用{previewOnly ? "（预览）" : ""}</button></footer>
    </dialog>
  </section>;
}
