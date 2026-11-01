import { createRoot } from 'react-dom/client';
import { DeliveryCardIdentity } from '../pages/catalog/DeliveryCardIdentity';
import '../styles/globals.css';
import '../styles/tokens.generated.css';
import '../styles/project-governance.css';

// Development-only visual fixture: no API, credentials, persistence or commands.
const samples = [
  { stage: '研发中', id: 'add-chat-validation-orchestration', sources: [{ id: 'REQ-0048', type: 'requirement', title: 'Chat 隔离验收环境编排与原操作续接' }], sprint: 'sprint-016', title: 'Chat 隔离验收环境编排与原操作续接' },
  { stage: '验收中', id: 'fix-requirement-center-refresh', sources: [{ id: 'BUG-0056', type: 'bug', title: '需求中心读取性能' }], sprint: 'sprint-014', title: '需求中心首屏与刷新性能修复' },
  { stage: '已完成', id: 'add-isolated-candidate-validation', sources: [{ id: 'REQ-0048', type: 'requirement', title: 'Chat 隔离验收环境编排与原操作续接' }], sprint: 'sprint-015', title: '固定候选隔离验收' },
];
function Preview() {
  return <main className="requirement-center theme-light" style={{ padding: 28, display: "block" }}><p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>实施骨架 · 合成样本 · 仅确认结构与密度，任务及动作尚未接入</p>
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,minmax(300px,1fr))', gap: 24, overflowX: 'auto' }}>
      {samples.map(card => <section key={card.id}><h2 style={{ fontSize: 18, marginBottom: 20 }}>{card.stage}</h2>
        <article className={`rc-card ${card.sources[0].type}`} data-testid="rc-delivery-card">
          <DeliveryCardIdentity id={card.id} changeId={card.id} sources={card.sources} sprintId={card.sprint}>
            <h3 className="rc-card-title">{card.title}</h3>
          </DeliveryCardIdentity><div className="rc-card-tags"><span className="rc-tag">产品团队</span><span className="rc-tag">人力待估算</span></div>
          <div className="rc-docs">{['Issue', 'Change', 'Sprint'].map(group => <div className="rc-doc-group" key={group}><span className="rc-doc-source">{group}</span><button disabled>{group === 'Issue' ? 'requirement.md' : group === 'Change' ? 'tasks.md' : 'sprint.md'}</button></div>)}</div>
          <p className="rc-progress">当前交付进度区域</p><footer><span>更新时间区域</span><button disabled>查看进度 →</button></footer>
        </article></section>)}
    </div>
    <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginTop: 30 }}>
      {['前期 Issue 保留', '多来源：一张交付卡', '独立 Change', '加载中', '暂无交付', '读取失败 / 重试', '权限不足 / 禁用'].map(state => <div key={state} data-testid="rc-skeleton-state" style={{ border: '1px solid #DDE3EE', padding: 16 }}>{state}</div>)}
    </div>
  </main>;
}
createRoot(document.getElementById('root')!).render(<Preview />);
