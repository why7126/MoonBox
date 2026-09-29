import "../../src/styles/globals.css";
import { createRoot } from "react-dom/client";
import { CaptureWorkspace } from "../../src/components/requirement-center/capture/CaptureWorkspace";

const params = new URLSearchParams(location.search);
const light = params.get("theme") === "light";
const step = params.get("step") === "result" ? "result" : "input";
document.documentElement.dataset.theme = light ? "light" : "dark";
if (light) document.body.style.background = "#f4f6fa";

const sampleText = [
  "希望 Capture 弹窗只有一个 MD 编辑器，能直接放多张图片和多个文本文件。",
  "列表刷新后回到顶部像是问题，也请拆成候选。",
  "",
  "### 来源文件：notes.md",
  "",
  "```text",
  "补充材料：图片和文本文件都应在同一个编辑器材料流里。",
  "```",
].join("\n");

const inputView = <>
  <div className="capture-editor-panel" data-testid="capture-md-editor">
    <details className="capture-material-drawer" open>
      <summary><span>来源材料 · 5 项</span></summary>
      <div className="capture-chiprow" aria-label="来源材料列表">
        <div className="capture-source capture-material-card capture-material-chip text">
          <span aria-hidden="true">📝</span>
          <div><strong>MD 文本</strong></div>
        </div>
        {[1, 2, 3, 4].map((index) => <div className="capture-material-card capture-material-chip ready" key={index} data-testid="capture-image-card">
          <span aria-hidden="true">🖼️</span>
          <div><strong>图片 {index}</strong></div>
          <button type="button" disabled>×</button>
        </div>)}
        <label className="capture-material-add">
          <span>+ 添加图片或文本文件</span>
        </label>
      </div>
    </details>
    <textarea id="capture-raw-editor" aria-label="原始材料" readOnly value={sampleText} />
    <div className="capture-rowfoot">
      <span className="capture-save capture-save-saved" data-testid="capture-save-state">草稿已保存</span>
      <button type="button" className="capture-input-delete">删除草稿</button>
    </div>
  </div>
  <button type="button" className="capture-primary capture-input-submit" aria-label="AI 整理候选">AI 整理候选 →</button>
</>;

const resultView = <div className="capture-result" data-testid="capture-result-body">
  <div className="capture-result-hero">
    <div className="capture-doneicon" aria-hidden="true">✓</div>
    <h2>已生成 2 条采集记录</h2>
    <p className="capture-muted">已按最终类型分配编号，注册表与索引已同步。</p>
  </div>
  <div className="capture-result-list">
    <article className="capture-resultcard" data-testid="capture-result-card">
      <span className="capture-result-badge requirement">REQ-2031</span>
      <div className="capture-result-detail">
        <strong>Capture 弹窗统一使用支持多图片和多文本文件的 MD 编辑器</strong>
        <p>目录 <code>/issues/REQ-2031/</code></p>
        <p>文件 <code>capture.md</code> · <code>trace.md</code></p>
        <p>来源 notes.md · 来源依据 · 1</p>
      </div>
    </article>
    <article className="capture-resultcard" data-testid="capture-result-card">
      <span className="capture-result-badge bug">BUG-2101</span>
      <div className="capture-result-detail">
        <strong>列表刷新后滚动位置回到顶部</strong>
        <p>目录 <code>/issues/BUG-2101/</code></p>
        <p>文件 <code>capture.md</code> · <code>trace.md</code></p>
        <p>来源 notes.md · 来源依据 · 1</p>
      </div>
    </article>
  </div>
  <div className="capture-idempotent">
    <p><strong>幂等保护：</strong>本次确认已绑定候选版本，编号仅分配一次。重复点击「确认创建」或失败重试都会返回同一批记录，不会重复创建。</p>
    <p><strong>产物边界：</strong>这一步只生成采集记录（capture.md / trace.md），正式的 requirement.md / bug.md 留到后续生成阶段。</p>
  </div>
</div>;

createRoot(document.getElementById("root")!).render(<>
  <p style={{ color: light ? "#677085" : "#98a0b3", textAlign: "center", font: "13px system-ui" }}>
    UI 骨架审阅 · 合成数据 · 不调用 AI、不保存草稿、不创建记录
  </p>
  <CaptureWorkspace
    step={step}
    saveState="saved"
    onClose={() => {}}
    materials={null}
    actions={step === "result" ? <button type="button" className="capture-primary">完成</button> : null}
  >
    {step === "result" ? resultView : inputView}
  </CaptureWorkspace>
</>);
