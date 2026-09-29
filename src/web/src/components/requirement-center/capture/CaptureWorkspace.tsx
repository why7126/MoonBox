import type { ReactNode } from "react";
import "./capture.css";
import { Button } from "../../ui/Button";

export type CaptureStep = "input" | "review" | "result";
export type CaptureSaveState = "saving" | "saved" | "failed" | "conflict";

/** Layout only: identities, saved versions and task results come from its controller. */
export function CaptureWorkspace({ step, materials, children, actions, saveState, onClose }: {
  step: CaptureStep;
  materials: ReactNode;
  children: ReactNode;
  actions?: ReactNode;
  saveState: CaptureSaveState;
  onClose: () => void;
}) {
  const labels: Record<CaptureSaveState, string> = {
    saving: "正在保存…", saved: "草稿已保存", failed: "保存失败，请重试", conflict: "草稿已更新，请核对后保存",
  };
  const stepLabel: Record<CaptureStep, string> = {
    input: "第 1 步 · 原始材料",
    review: "第 2 步 · 审阅候选",
    result: "第 3 步 · 创建结果",
  };
  return <section className="capture-workspace" data-step={step} data-testid="capture-workspace" aria-label="新建 Capture">
    <header className="capture-header">
      <div className="capture-topbar">
        <span className="capture-kicker">新建 CAPTURE</span>
        <Button variant="ghost" type="button" aria-label="关闭 Capture" data-testid="capture-close" onClick={onClose}>关闭 ×</Button>
      </div>
      <div className="capture-progress" aria-label="采集步骤">
        <span className={step === "input" ? "active" : "done"} aria-hidden="true" />
        <span className={step === "review" ? "active" : step === "result" ? "done" : ""} aria-hidden="true" />
        <span className={step === "result" ? "active" : ""} aria-hidden="true" />
        <strong>{stepLabel[step]}</strong>
      </div>
    </header>
    <main className="capture-layout" data-testid="capture-layout">
      <div className="capture-content" data-testid={`capture-${step}`} aria-live="polite">
        {step === "input" && materials}
        {children}
      </div>
    </main>
    {actions && <footer className="capture-actions" data-testid="capture-actions">
      <span className={`capture-save capture-save-${saveState}`} data-testid="capture-save-state" role="status">{labels[saveState]}</span>
      <div className="capture-action-buttons">{actions}</div>
    </footer>}
  </section>;
}
