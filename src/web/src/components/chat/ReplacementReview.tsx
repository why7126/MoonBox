import { useEffect, useRef, useState } from 'react';
import { ChatDialog } from './ChatDialog';
import { chatRequest } from './chatApi';
import './replacement-review.css';

type RuleChange = {
  change_id: string; capability: string; requirement: string;
  before: string; after: string; protected_changes: string[]; affected_requirements: string[];
  review_reason: string | null; state: string; acceptance_ready: boolean;
  acceptance_blockers: string[]; archive_ready: boolean; archive_reason: string | null;
};
function readableRule(value: string) {
  return value.replace(/\s*#### Scenario:\s*/g, '\n\n场景：')
    .replace(/\s*- \*\*WHEN\*\*\s*/g, '\n当：')
    .replace(/\s*- \*\*THEN\*\*\s*/g, '\n结果：').trim();
}

export function ReplacementReview({ spaceId, repositoryId, changeId, openRequest = 0 }: {
  spaceId: string; repositoryId: string; changeId: string; openRequest?: number;
}) {
  const [open, setOpen] = useState(false);
  const [row, setRow] = useState<RuleChange | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const trigger = useRef<HTMLElement | null>(null);
  const lastRequest = useRef(0);
  const generation = useRef(0);

  useEffect(() => {
    if (openRequest > 0 && openRequest !== lastRequest.current) {
      trigger.current = document.activeElement as HTMLElement;
      setOpen(true);
    }
    lastRequest.current = openRequest;
  }, [openRequest]);
  async function refresh() {
    const current = ++generation.current;
    setRow(null);
    const query = new URLSearchParams({ space_id: spaceId, repository_id: repositoryId, change_id: changeId });
    const value = await chatRequest<RuleChange>(`/rule-changes?${query}`);
    if (current === generation.current) setRow(value);
    return value;
  }
  useEffect(() => {
    if (open) { setError(''); setMessage(''); void refresh().catch(failure => setError(failure instanceof Error ? failure.message : '规则修改读取失败')); }
    return () => { generation.current++; };
  }, [open, spaceId, repositoryId, changeId]);
  async function recheck() {
    if (busy) return;
    setBusy(true); setError(''); setMessage('');
    try {
      await refresh();
      setMessage('已重新读取当前规则与验收状态；归档仍须单独执行。');
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : '重新检查失败，请稍后再试');
    } finally { setBusy(false); }
  }
  return open && <div className="replacement-review-shell"><ChatDialog returnFocusRef={trigger} title="查看规则修改" testId="rule-change-drawer" busy={busy} closeOnOutside={false} onClose={() => setOpen(false)} footer={row &&
    <button type="button" data-testid="rule-change-recheck" disabled={busy} onClick={() => void recheck()}>重新检查归档</button>}>
    {error && <p role="alert">{error}</p>}
    {message && <p role="status">{message}</p>}
    {!row && !error && <p role="status">正在读取规则修改…</p>}
    {row && <>
      <p>{row.change_id} · {row.state === 'ready' ? '当前检查可继续' : row.state === 'unsupported' ? '当前修改不符合允许范围' : '归档仍有待处理项'}</p>
      <h3>{row.requirement}</h3>
      {row.affected_requirements.length > 1 && <p>本次共影响 {row.affected_requirements.length} 项规则：{row.affected_requirements.join('、')}。以下展示第一项。</p>}
      <details data-testid="rule-change-diff"><summary>查看原规则与修改后全文</summary><div className="replacement-diff-columns"><section><h4>原规则</h4><pre>{readableRule(row.before)}</pre></section><section><h4>修改后</h4><pre>{readableRule(row.after)}</pre></section></div></details>
      <section><h3>为什么修改</h3><p>请结合本对象关联的需求或缺陷说明核对修改原因；此处展示原规则与修改结果。</p></section>
      <section><h3>仍然禁止</h3><p>验收未完成、无权归档、历史记录不完整、内容被篡改或检查后发生变化，仍会阻断归档。</p></section>
      <section><h3>受影响验收</h3><p>{row.acceptance_ready ? '当前验收证据已就绪；最终归档仍单独检查。' : '验收证据尚未全部就绪；查看修改不能代替测试结果。'}</p>{row.acceptance_blockers.length > 0 && <p>{row.acceptance_blockers.join('、')}</p>}</section>
      <section><h3>归档检查</h3><p>{row.archive_ready ? '规则修改已通过当前检查；归档仍需单独执行。' : row.archive_reason || '归档尚未就绪。'}</p></section>
      {row.review_reason && <p role="alert">{row.review_reason}</p>}
    </>}
  </ChatDialog></div>;
}
