import { createRoot } from 'react-dom/client';
import { ChangePriorityEditor } from '../pages/catalog/ChangePriorityEditor';
import '../styles/globals.css';
import '../styles/tokens.generated.css';
import '../styles/project-governance.css';
import '../styles/change-priority.css';
createRoot(document.getElementById('root')!).render(<main className="requirement-center theme-light" style={{padding:32,display:'block'}}>
  <h1>独立 Change 优先级 · 结构确认</h1><p>合成样本，不调用接口或保存数据。</p>
  <article className="rc-card" style={{maxWidth:560,marginTop:24}}>
    <strong>add-governance-consistency</strong><h2>治理文档一致性优化</h2>
    <div className="rc-card-tags"><span className="rc-tag" data-testid="change-priority-badge">优先级 P2</span><span className="rc-tag">负责人未分配</span></div>
    <ChangePriorityEditor id="visual-fixture" priority="P2" version={"a".repeat(64)} project={{space_id:"space",repository_id:"repo",status:"connected",readonly:false}} onSaved={async()=>{}} />
  </article></main>);
