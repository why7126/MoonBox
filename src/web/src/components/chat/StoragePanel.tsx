import type { ReactNode } from "react";
import "./storage-panel.css";

export type StoragePanelProps = {
  stage: string;
  summary: string;
  reason?: string;
  savedLabel?: string;
  recoveryLabel?: string;
  busy?: boolean;
  onRead?: () => void;
  onRecover?: () => void;
  children?: ReactNode;
};

/** Presentation boundary: authority and progress always come from the caller. */
export function StoragePanel(props: StoragePanelProps) {
  return <section className="chat-storage-panel" data-testid="chat-storage-panel" aria-label="执行与保存状态">
    <h3 data-testid="chat-storage-stage">{props.stage}</h3>
    <p role="status" aria-live="polite">{props.summary}</p>
    {props.reason && <details data-testid="chat-storage-reason"><summary>查看原因与处理说明</summary><p>{props.reason}</p></details>}
    <div className="chat-storage-actions">
      <button type="button" data-testid="chat-saved-result" disabled={!props.onRead || props.busy} onClick={props.onRead}>{props.savedLabel || "查看已保存内容"}</button>
      {props.recoveryLabel && <button type="button" data-testid="chat-recovery-action" disabled={!props.onRecover || props.busy} onClick={props.onRecover}>{props.busy ? "正在核验…" : props.recoveryLabel}</button>}
    </div>
    {props.children && <div className="chat-result-page" data-testid="chat-result-page">{props.children}</div>}
  </section>;
}
