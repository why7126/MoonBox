import { useEffect, useRef, useState, type ReactNode } from "react";
import { AlertCircle, X } from "lucide-react";
import "./requirement-center-error.css";
import { GovernanceError } from "../../components/workbench/governanceApi";

export type ReadFailure = { status?: number; code?: number; kind?: string; requestId?: string };
export function readFailure(error: unknown): ReadFailure {
  if (!(error instanceof GovernanceError)) return {};
  return { status: error.status, code: Number.isFinite(error.code) ? error.code : undefined, kind: ["source_invalid", "source_changing", "source_unavailable"].includes(error.kind || "") ? error.kind : undefined, requestId: typeof error.requestId === "string" && /^[a-zA-Z0-9_-]{1,128}$/.test(error.requestId) ? error.requestId : undefined };
}

export function RequirementCenterError({ drawer = false, busy = false, onRetry, onDetails, children }: {
  drawer?: boolean; busy?: boolean; onRetry: () => void; onDetails: () => void; children?: ReactNode;
}) {
  const prefix = drawer ? "rc-document-error" : "rc-error";
  return <section className="rc-read-error" aria-label={drawer ? "文档加载失败" : "需求中心加载失败"}>
    <AlertCircle size={20} aria-hidden="true" />
    <div><h3>{drawer ? "文档暂时无法加载" : "需求中心暂时无法加载"}</h3>
      <p>{children || "当前项目数据读取失败，请稍后重试或查看详情。"}</p>
      <div className="rc-read-error-actions">
        <button type="button" className="rc-primary-action" data-testid={`${prefix}-retry`} disabled={busy} aria-busy={busy} onClick={onRetry}>{busy ? "正在加载…" : "重新加载"}</button>
        <button type="button" className="rc-secondary-action" data-testid={`${prefix}-details-trigger`} onClick={onDetails}>查看详情</button>
      </div>
    </div>
  </section>;
}

export function RequirementCenterErrorDetails({ onClose, failure }: { onClose: () => void; failure: ReadFailure }) {
  const root = useRef<HTMLElement>(null);
  const close = useRef(onClose); close.current = onClose;
  const [copied, setCopied] = useState("");
  const reason = failure.status === 401 || failure.status === 403 ? "当前访问权限已失效。" : failure.status === 404 ? "文档不存在或已移动。" : failure.kind === "source_invalid" ? "项目数据格式暂不可解析。" : failure.kind === "source_changing" ? "项目文件正在更新，本次未能读取完整版本。" : "项目数据暂时无法读取。";
  const action = failure.kind === "source_invalid" ? "请修复项目文件格式后重新加载；可提供请求编号协助排查。" : "请确认项目和访问权限后重新加载；若仍失败，可提供请求编号协助排查。";
  const diagnostic = [reason, action, failure.code !== undefined ? `错误码：${failure.code}` : "", failure.requestId ? `请求编号：${failure.requestId}` : ""].filter(Boolean).join("\n");
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    root.current?.focus();
    const key = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); event.stopImmediatePropagation(); close.current(); return; }
      if (event.key !== "Tab") return;
      const targets = [...(root.current?.querySelectorAll<HTMLButtonElement>('button:not(:disabled)') || [])];
      const first = targets[0], last = targets[targets.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && (document.activeElement === first || document.activeElement === root.current)) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || document.activeElement === root.current)) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", key, true);
    return () => { document.removeEventListener("keydown", key, true); if (previous?.isConnected) previous.focus(); };
  }, []);
  const copy = async () => {
    try { await navigator.clipboard.writeText(diagnostic); setCopied("已复制"); }
    catch { setCopied("复制失败，请手动选择诊断信息"); }
  };
  return <div className="rc-error-backdrop" onClick={event => { if (event.target === event.currentTarget) onClose(); }}>
    <section className="rc-error-dialog" ref={root} tabIndex={-1} role="dialog" aria-modal="true" aria-labelledby="rc-error-dialog-title" data-testid="rc-error-details-dialog">
      <header><h2 id="rc-error-dialog-title">加载失败详情</h2><button type="button" aria-label="关闭加载失败详情" data-testid="rc-error-details-close" onClick={onClose}><X size={18} /></button></header>
      <div className="rc-error-dialog-body"><p>{reason}</p><p>{action}</p><dl>
        {failure.code !== undefined && <><dt>错误码</dt><dd>{failure.code}</dd></>}
        <dt>请求编号</dt><dd>{failure.requestId || "本次响应未提供请求编号"}</dd>
      </dl><span role="status">{copied}</span></div>
      <footer><button type="button" className="rc-secondary-action" data-testid="rc-error-copy" onClick={() => void copy()}>复制诊断信息</button><button type="button" className="rc-primary-action" onClick={onClose}>关闭</button></footer>
    </section>
  </div>;
}
