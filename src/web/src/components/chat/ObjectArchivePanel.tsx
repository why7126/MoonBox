import { Button } from "../ui/Button";
import { useCallback, useEffect, useRef, useState } from 'react';
import type { ObjectArchiveView, ObjectArchiveOperation } from '../../api/generated/governance';
import { governanceRequest } from '../workbench/governanceApi';
import { chatRequest, type ConversationRead } from './chatApi';
import { ChatDialog } from './ChatDialog';
import './object-archive.css';

const verificationLabels: Record<string, string> = { passed:'当前复核通过', blocked:'当前文档需要处理', review:'需要证据复核', stale:'内容已变化，请刷新', pending:'尚未到收尾复核阶段' };
export function ObjectArchivePanel({ conversation, refreshKey = '', visible = true }: { conversation: ConversationRead | null; refreshKey?: string; visible?: boolean }) {
  const [view, setView] = useState<ObjectArchiveView | null>(null);
  const [loading, setLoading] = useState(false), [busy, setBusy] = useState(false);
  const [error, setError] = useState(''), [feedback, setFeedback] = useState('');
  const [confirmation, setConfirmation] = useState<ObjectArchiveOperation | null>(null);
  const state = useRef<{ controller: AbortController; running: boolean; queued: boolean } | null>(null);
  const writeLock = useRef(false), latest = useRef<ObjectArchiveView | null>(null);
  const identity = `${conversation?.id || ''}:${conversation?.space_id || ''}:${conversation?.repository_id || ''}`;
  const refresh = useCallback(async () => {
    const run = state.current;
    if (!run || run.controller.signal.aborted || !conversation) return;
    if (run.running) { run.queued = true; return; }
    run.running = true; setLoading(true);
    try {
      const relations = await chatRequest<{primary: {id:string} | null}>(`/conversations/${conversation.id}/relations`, {signal:run.controller.signal});
      const value = relations.primary ? await governanceRequest<ObjectArchiveView>(`/api/v1/chat/archive-operations?${new URLSearchParams({space_id:conversation.space_id,repository_id:conversation.repository_id,object_id:relations.primary.id})}`, {signal:run.controller.signal}) : null;
      if (state.current !== run || run.controller.signal.aborted) return;
      latest.current = value; setView(value); setError('');
      setConfirmation(previous => previous && value?.operations.some(op => op.operation_id === previous.operation_id && op.revision === previous.revision && op.allowed_actions.includes('resume')) ? previous : null);
    } catch (e) {
      if (state.current === run && !run.controller.signal.aborted) {
        latest.current = null; setView(null); setConfirmation(null);
        setError(e instanceof Error ? e.message : '归档状态暂不可用，请刷新');
      }
    } finally {
      run.running = false;
      if (state.current === run && !run.controller.signal.aborted) {
        setLoading(false);
        if (run.queued) { run.queued = false; void refresh(); }
      }
    }
  }, [identity]);
  useEffect(() => {
    const run = {controller:new AbortController(),running:false,queued:false}; state.current = run;
    latest.current=null; setView(null); setError(''); setFeedback(''); setConfirmation(null);
    if (visible) void refresh();
    return () => { run.controller.abort(); if (state.current === run) state.current=null; };
  }, [identity, refresh]);
  useEffect(() => {
    if (!visible) return;
    const timer = setTimeout(() => void refresh(), 150);
    const online = () => void refresh(); window.addEventListener('online', online); window.addEventListener('moonbox:object-relations-changed', online);
    return () => { clearTimeout(timer); window.removeEventListener('online', online); window.removeEventListener('moonbox:object-relations-changed', online); };
  }, [visible, refreshKey, refresh]);
  const resume = async () => {
    if (!confirmation || !conversation || writeLock.current) return;
    const current = latest.current?.operations.find(op => op.operation_id === confirmation.operation_id);
    if (!current || current.revision !== confirmation.revision || !current.allowed_actions.includes('resume')) return;
    const run = state.current; writeLock.current=true; setBusy(true); setFeedback('');
    try {
      await governanceRequest('/api/v1/chat/archive-operations/resume', {method:'POST',body:JSON.stringify({space_id:conversation.space_id,repository_id:conversation.repository_id,object_id:current.target_id,operation_id:current.operation_id,confirmed:true})});
      if (state.current === run) { setConfirmation(null); setFeedback('原操作已执行；以最新复核结果为准。'); }
    } catch (e) {
      if (state.current === run) setFeedback(e instanceof Error ? e.message : '续接未确认，请重新查询原操作');
    } finally {
      writeLock.current=false; if (state.current) setBusy(false); if (state.current === run) void refresh();
    }
  };
  if (!conversation || (!view && !error && !loading)) return null;
  return <section className="object-archive-panel" data-testid="object-archive-panel" aria-label="当前主对象归档状态">
    <header><div><strong>当前主对象归档状态</strong><p>当前对象视图 · 与所选轮次分别显示</p></div><Button variant="ghost" data-testid="object-archive-refresh" disabled={loading || busy} onClick={() => void refresh()}>刷新状态</Button></header>
    {loading && <p role="status">正在核验当前状态…</p>}
    {error && <p role="alert">{error}</p>}
    {view && <><p className="object-archive-location">{view.object_id}</p>
      {view.summary === 'not_started' && <p>尚无归档操作记录。</p>}
      {view.summary === 'needs_attention' && view.operations.length > 1 && <p>各项操作进度不同，请逐项核对。</p>}
      {view.operations.map(op => <article key={op.operation_id} data-testid="object-archive-operation">
        <strong className="object-archive-location">{op.target_id}</strong>
        <p>{op.stage === 'completed' ? '原操作已完成' : '原操作尚未完成'} · {verificationLabels[op.verification.status] || '状态待核验'}</p>
        {!!op.verification.findings.length && <details><summary>查看问题（{op.verification.findings.length}）</summary>{op.verification.findings.map((f,i) => <div key={i}><p className="object-archive-location">{f.relative_path}{f.line ? ` · 第 ${f.line} 行` : ''}</p><p>{f.message}{f.requires_review ? ' 需要证据复核。' : ''}</p></div>)}</details>}
        {op.denial_reason && <p>当前不能安全续接，请核对权限或执行占用后刷新。</p>}
        {op.allowed_actions.includes('resume') && <Button variant="ghost" data-testid="object-archive-resume" disabled={busy || loading} onClick={() => setConfirmation(op)}>继续原操作</Button>}
      </article>)}
      {!!view.not_started_targets?.length && view.summary !== 'not_started' && <p className="object-archive-location">尚无操作：{view.not_started_targets.join('、')}</p>}
    </>}
    {feedback && <p role="status">{feedback}</p>}
    {confirmation && <ChatDialog title="继续原归档操作" testId="object-archive-confirm" busy={busy} onClose={() => setConfirmation(null)} footer={<><Button variant="ghost" disabled={busy} onClick={() => setConfirmation(null)}>取消</Button><Button variant="ghost" data-testid="object-archive-confirm-submit" disabled={busy || loading} onClick={() => void resume()}>确认继续</Button></>}><p>将继续 {confirmation.target_id} 的原归档操作。系统会重新核对当前权限、文档和恢复条件；已有历史证据保留。</p>{feedback && <p role="alert">{feedback}</p>}</ChatDialog>}
  </section>;
}
