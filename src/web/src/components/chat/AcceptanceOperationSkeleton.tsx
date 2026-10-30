import {Button} from '../ui/Button';
import './acceptance-operation.css';

/** Preview-only layout: no API calls, state transitions or granted capabilities. */
export function AcceptanceOperationSkeleton() {
  return <article className="acceptance-operation" data-testid="acceptance-operation-skeleton" aria-busy="true">
    <div className="acceptance-heading"><strong>本次验收</strong><span data-testid="acceptance-stage">准备环境</span></div>
    <p data-testid="turn-status-feedback" role="status">正在准备隔离数据库与当前版本应用</p>
    <p className="acceptance-muted" data-testid="acceptance-checks">验收结果尚未产生 · 资源尚未释放</p>
    <details open data-testid="acceptance-details"><summary>执行详情</summary>
      <dl><div><dt>代码与计划</dt><dd>当前操作的授权快照</dd></div>
      <div><dt>数据库</dt><dd>独立 MySQL 8.4</dd></div>
      <div><dt>测试身份</dt><dd>仅限本任务的短期身份</dd></div>
      <div><dt>临时资源</dt><dd>准备中，完成后回收</dd></div></dl>
    </details>
    <div className="acceptance-actions" data-testid="acceptance-actions">
      <Button variant="ghost" disabled>查看证据</Button><Button variant="ghost" disabled>重新核验</Button>
      <Button variant="ghost" disabled>继续</Button><Button variant="ghost" disabled>停止</Button>
    </div>
    <small className="acceptance-muted">骨架预览 · 合成数据 · 按钮未接入真实操作</small>
  </article>;
}
