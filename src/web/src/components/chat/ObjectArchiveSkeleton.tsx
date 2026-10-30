import { Button } from "../ui/Button";
import './object-archive.css';

/** Preview only: no requests and no executable actions. */
export function ObjectArchiveSkeleton() {
  return <section className="object-archive-panel" data-testid="object-archive-panel" aria-label="对象归档状态">
    <header><div><strong>对象归档状态</strong><p>当前对象 · 不代表某一轮对话的执行结果</p></div><Button variant="ghost" disabled>刷新状态</Button></header>
    <article data-testid="object-archive-operation">
      <strong>示例对象 · 归档收尾待处理</strong>
      <p>原操作已保存，当前文档还有 2 项需要核对。</p>
      <details open><summary>查看问题</summary><p className="object-archive-location">issues/requirements/archive/REQ-0001-example/trace.md · 第 12 行</p><p>核对当前状态和证据入口，历史过程保留。</p></details>
      <Button variant="ghost" disabled>继续原操作</Button>
    </article>
    <p role="status">骨架预览 · 尚未接入真实查询；继续操作前会展示确认对话框。</p>
    <div data-testid="object-archive-dialog-slot" hidden />
  </section>;
}
