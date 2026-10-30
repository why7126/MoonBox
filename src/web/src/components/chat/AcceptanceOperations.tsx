import { useEffect, useRef, useState } from 'react';
import { governanceRequest } from '../workbench/governanceApi';
import { Button } from '../ui/Button';
import { ChatDialog } from './ChatDialog';
import './acceptance-operation.css';

export type AcceptanceOperation = {
  id: string; source_turn_id: string; change_id: string; status: string; version: number;
  cleanup_state: string; cancel_requested: boolean; ready: boolean; reason_code: string | null;
  reason_message?: string | null;
  expires_at: number | null; allowed_actions: string[];
  checks: { ac_id: string; status: string; reason_code: string | null; evidence_available: boolean }[];
};
const stages: Record<string, string> = {
  queued: '等待准备', preparing: '准备环境', ready: '环境就绪', running: '执行验收',
  blocked: '等待处理', passed: '验收通过', failed: '验收未通过', cancelled: '已停止',
};
const resources: Record<string, string> = {
  not_created: '尚未创建', active: '使用中', releasing: '回收中', released: '已释放', cleanup_failed: '回收失败',
};
const checks: Record<string, string> = { pending: '待验收', stale: '需重新核验', passed: '通过', failed: '未通过', blocked: '受阻' };

/** Refresh only reads. A mutation requires a deliberate action and current version. */
export function AcceptanceOperations({ conversationId }: { conversationId: string }) {
  const [items, setItems] = useState<AcceptanceOperation[]>([]);
  const [error, setError] = useState('');
  const [stopping, setStopping] = useState<AcceptanceOperation | null>(null);
  const [busy, setBusy] = useState(false);
  const [evidence, setEvidence] = useState<{ ac_id: string; status: string; evidence: { kind?: string; digest?: string } }[] | null>(null);
  const mutation = useRef(false);
  const scope = useRef(conversationId); scope.current = conversationId;
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    setItems([]); setError(''); setStopping(null); setEvidence(null);
    const read = async () => {
      try {
        const response = await governanceRequest<{ items: AcceptanceOperation[] }>(
          `/api/v1/chat/conversations/${encodeURIComponent(conversationId)}/acceptance-operations`,
          { signal: controller.signal });
        if (!controller.signal.aborted) { setItems(response.items); setError(''); }
      } catch (cause) {
        if (!controller.signal.aborted) {
          setItems([]); setError(cause instanceof Error ? cause.message : '验收状态暂不可用');
        }
      }
      if (!controller.signal.aborted) timer = setTimeout(read, 4000);
    };
    void read(); return () => { controller.abort(); clearTimeout(timer); };
  }, [conversationId, refresh]);
  const stop = async () => {
    if (!stopping || mutation.current) return;
    mutation.current = true; setBusy(true); const original = conversationId;
    try {
      const item = await governanceRequest<AcceptanceOperation>(
        `/api/v1/chat/acceptance-operations/${encodeURIComponent(stopping.id)}/stop`,
        { method: 'POST', body: JSON.stringify({ version: stopping.version }) });
      if (scope.current === original) {
        setItems(previous => previous.map(old => old.id === item.id ? item : old)); setStopping(null); setError('');
      }
    } catch (cause) {
      if (scope.current === original) setError(cause instanceof Error ? cause.message : '停止失败，请刷新后重试');
    } finally { mutation.current = false; setBusy(false); }
  };
  const action = async (item: AcceptanceOperation, name: string) => {
    if (mutation.current || !item.allowed_actions.includes(name)) return;
    mutation.current = true; setBusy(true); const original = conversationId;
    try {
      const base = `/api/v1/chat/acceptance-operations/${encodeURIComponent(item.id)}`;
      if (name === 'archive-evidence') {
        const result = await governanceRequest<{ items: { summary: { checks: NonNullable<typeof evidence> } }[] }>(base + '/evidence/archive');
        if (scope.current === original) setEvidence(result.items.flatMap(record => record.summary.checks));
      } else if (name === 'evidence') {
        const result = await governanceRequest<{ checks: NonNullable<typeof evidence> }>(base + '/evidence');
        if (scope.current === original) setEvidence(result.checks);
      } else {
        const updated = await governanceRequest<AcceptanceOperation>(name === 'verify' ? base : base + '/' + name,
          name === 'verify' ? { headers: { 'X-Acceptance-Action': 'verify' } } : { method: 'POST', body: JSON.stringify({ version: item.version }) });
        if (scope.current === original) setItems(previous => previous.map(old => old.id === updated.id ? updated : old));
      }
      if (scope.current === original) setError('');
    } catch (cause) {
      if (scope.current === original) setError(cause instanceof Error ? cause.message : '操作未完成，请重新核验');
    } finally { mutation.current = false; setBusy(false); }
  };
  return <>
    {error && <div role="alert" className="acceptance-operation">{error}<Button variant="ghost" onClick={() => setRefresh(v => v + 1)}>刷新状态</Button></div>}
    {items.map(item => <article key={item.id} className="acceptance-operation" data-testid="acceptance-operation">
      <div className="acceptance-heading"><strong>本次验收</strong><span data-testid="acceptance-stage">{stages[item.status] || '状态待核验'}</span></div>
      <p role="status">{item.ready ? '验收通过，临时资源已释放' : item.cancel_requested ? '已停止验收，保留已有结果并等待资源回收' : '验收结果与资源回收分别记录'}</p>
      <p className="acceptance-muted">资源：{resources[item.cleanup_state] || '待核验'}</p>
      {item.reason_message && <p role="status">{item.reason_message}</p>}
      <details data-testid="acceptance-details"><summary>执行详情</summary>
        <dl><div><dt>变更</dt><dd>{item.change_id}</dd></div>
          <div><dt>环境期限</dt><dd>{item.expires_at ? new Date(item.expires_at * 1000).toLocaleString() : '分配环境后确定'}</dd></div></dl>
        <ul>{item.checks.map(check => <li key={check.ac_id}>{check.ac_id}：{checks[check.status] || '待核验'}{check.evidence_available && ' · 已记录证据'}</li>)}</ul>
      </details>
      <div className="acceptance-actions" data-testid="acceptance-actions">
        {([['evidence', '查看证据'], ['archive-evidence', '长期摘要'], ['verify', '重新核验'], ['resume', '继续'], ['cleanup-retries', '重试清理']] as const).map(([name, label]) =>
          item.allowed_actions.includes(name) && <Button key={name} variant="ghost" data-testid={`acceptance-${name}`} disabled={busy} onClick={() => void action(item, name)}>{label}</Button>)}
        {item.allowed_actions.includes('stop') && <Button variant="ghost" data-testid="acceptance-stop" disabled={busy} onClick={() => setStopping(item)}>停止</Button>}
      </div>
    </article>)}
    {stopping && <ChatDialog title="停止本次验收" testId="acceptance-stop-dialog" busy={busy} onClose={() => setStopping(null)}
      footer={<><Button variant="ghost" disabled={busy} onClick={() => setStopping(null)}>返回</Button><Button disabled={busy} onClick={() => void stop()}>{busy ? '正在停止…' : '确认停止'}</Button></>}>
      <p>停止后不会自动继续原操作。已有验收结果会保留，临时资源将进入回收流程。</p>
      {error && <p role="alert">{error}</p>}
    </ChatDialog>}
    {evidence && <ChatDialog title="验收证据摘要" testId="acceptance-evidence-dialog" onClose={() => setEvidence(null)}>
      {evidence.length ? <ul>{evidence.map((check, index) => <li key={`${check.ac_id}-${index}`}>{check.ac_id} · {checks[check.status] || '待核验'}
        <p>类别：{check.evidence.kind || '未记录'}</p><p className="acceptance-muted">摘要：{check.evidence.digest || '未记录'}</p></li>)}</ul> : <p>当前没有可读取的在线证据。</p>}
    </ChatDialog>}
  </>;
}
