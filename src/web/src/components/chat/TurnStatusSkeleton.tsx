import { RecoveryOperationSkeleton } from './RecoveryOperationPanel';
/** Layout gate only; the loading state never grants an operation capability. */
export function TurnStatusSkeleton() {
 return <article data-testid="turn-status-root" className="chat-assistant-col" aria-busy="true">
  <button className="chat-tool-summary" data-testid="turn-status-trigger" aria-expanded="true" disabled>正在读取状态 · 执行详情</button>
  <p data-testid="turn-status-feedback" role="status">骨架预览 · 状态与动作由真实 API 决定</p>
  <div data-testid="turn-body">消息正文保留在本轮状态下方。</div>
  <div data-testid="turn-execution-detail"><RecoveryOperationSkeleton /></div>
 </article>;
}
