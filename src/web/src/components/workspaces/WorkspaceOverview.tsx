import type { WorkspaceView } from '../../api/generated/workspaces';
import type { ReactNode } from 'react';
import './workspace-overview.css';

export const workspacePurpose: Record<string,string> = {main:'主工作区',development:'独立开发工作区',integration:'组合验收工作区',recovery:'独立恢复目录',legacy:'历史工作区'};

export type WorkspaceOverviewState = 'loading' | 'ready' | 'error' | 'forbidden' | 'stale';
/** Presentation boundary: all identities and capabilities are supplied by the authenticated controller. */
export function WorkspaceOverview({ state, items, error, onReload, children }: {
  state: WorkspaceOverviewState; items: WorkspaceView[]; error?: string; onReload: () => void; children?: ReactNode;
}) {
  const message = state === 'loading' ? '正在读取工作区…' : state === 'forbidden' ? '当前没有访问此仓库的权限。'
    : state === 'stale' ? '工作区信息已变化，请重新读取。' : state === 'error' ? error || '暂时无法读取工作区，请重试。'
    : items.length ? '工作区信息已更新。' : '此仓库尚未登记工作区。';
  return <section className="moonbox-workspace-overview" data-testid="workspace-overview" aria-busy={state === 'loading'}>
    <header><div><p className="workspace-eyebrow">仓库与工作区</p><h1>工作区与交付进度</h1></div>
      <button type="button" onClick={onReload} disabled={state === 'loading'}>刷新</button></header>
    <div role="status" data-testid="workspace-status">{message}</div>
    {children || <>
    <section className="workspace-card" data-testid="workspace-summary" aria-label="工作区摘要">
      <h2>执行工作区</h2>
      {state === 'ready' && items.map(item => <article key={item.id} className="workspace-identity">
        <strong>{workspacePurpose[item.purpose] || '工作区'}</strong>
        <dl><div><dt>工作区</dt><dd>{item.id}</dd></div><div><dt>起始提交</dt><dd>{item.base_commit.slice(0, 12)}</dd></div>
          <div><dt>目录状态</dt><dd>{item.lifecycle === 'ready' ? '可用' : '准备中'}</dd></div></dl>
      </article>)}
      {state !== 'ready' || !items.length ? <p className="workspace-muted">工作区身份确认后，在这里查看目录状态和执行进度。</p> : null}
      <div className="workspace-actions" data-testid="workspace-actions">
        <button type="button" data-testid="workspace-picker" disabled>选择工作区</button>
        <button type="button" data-testid="workspace-create" disabled>创建独立工作区</button>
        <button type="button" data-testid="workspace-clean" disabled>清理工作区</button>
      </div>
    </section>
    <div className="workspace-delivery-grid">
      <section className="workspace-card" data-testid="recovery-summary"><h2>恢复点</h2>
        <p className="workspace-muted">恢复点信息尚未就绪。</p><div className="workspace-actions" data-testid="recovery-actions">
          <button type="button" data-testid="recovery-diff" disabled>查看差异</button>
          <button type="button" data-testid="recovery-restore" disabled>撤销选定修改</button>
        </div></section>
      <section className="workspace-card" data-testid="merge-summary"><h2>成果合入</h2>
        <p className="workspace-muted">当前没有可确认的合入候选。</p><div className="workspace-actions" data-testid="merge-actions">
          <button type="button" data-testid="merge-validate" disabled>验证候选</button>
          <button type="button" data-testid="merge-confirm" disabled>确认合入</button>
        </div></section>
    </div>
    <div data-testid="workspace-overlay-slot" />
    </>}
  </section>;
}
