import { Button } from "../../components/ui/Button";
/** Initial layout contract; API wiring follows the first skeleton review. */
export function ChangePriorityEditorSkeleton() {
  return <section className="change-priority-editor" data-testid="change-priority-editor" aria-label="优先级编辑区">
    <label>交付优先级 <select // ds-ok: 原生选择语义与键盘可达性，项目暂无共享Select，使用卡片token。
      data-testid="change-priority-level" defaultValue="P2">
      {['P0', 'P1', 'P2', 'P3'].map(level => <option key={level}>{level}</option>)}
    </select></label>
    <p role="status">维护窗口就绪后可保存，提交后等待处理结果。</p>
    <div className="change-priority-actions">
      <Button type="button" data-testid="change-priority-save">保存</Button>
      <Button type="button" data-testid="change-priority-cancel">取消</Button>
    </div>
  </section>;
}

import { useEffect, useRef, useState } from 'react';
import { governanceRequest, scopedUrl, waitApplication, GovernanceError, type Project, type Application } from '../../components/workbench/governanceApi';
import type { ChangePriorityUpdate } from '../../api/generated/governance';
import '../../styles/change-priority.css';

export function ChangePriorityEditor({ id, priority, version, project, onSaved }: {
  id: string; priority?: string; version: string; project: Project; onSaved: () => Promise<unknown>;
}) {
  const [open, setOpen] = useState(false), [value, setValue] = useState(priority || '');
  const [currentVersion, setVersion] = useState(version), [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(''), [conflict, setConflict] = useState(false);
  const container = useRef<HTMLDivElement>(null), controller = useRef<AbortController>();
  const attempt = useRef(0), inFlight = useRef(false);
  useEffect(() => () => { attempt.current++; controller.current?.abort(); }, [id, project.space_id, project.repository_id]);
  const close = () => { attempt.current++; controller.current?.abort(); inFlight.current = false; setBusy(false); setOpen(false); container.current?.querySelector<HTMLButtonElement>('[data-testid="change-priority-edit"]')?.focus(); };
  async function reload() {
    const identity = ++attempt.current;
    const abort = new AbortController(); controller.current = abort;
    setBusy(true);
    try {
      const doc = await governanceRequest<{ content: string; version: string }>(scopedUrl('/api/v1/requirement-center/changes/' + encodeURIComponent(id) + '/documents/trace.md', project), {signal: abort.signal});
      if (identity !== attempt.current) return;
      setVersion(doc.version); setValue(''); setConflict(false); setMessage('已重载，请重新选择优先级。');
    } catch (error) { if (identity === attempt.current) setMessage(error instanceof Error ? error.message : '重载失败'); }
    finally { if (identity === attempt.current) setBusy(false); }
  }
  async function save() {
    if (inFlight.current || conflict || !value) return;
    inFlight.current = true; setBusy(true); setMessage('保存中，请等待处理结果。');
    const identity = ++attempt.current; const abort = new AbortController(); controller.current = abort;
    try {
      const payload: ChangePriorityUpdate = { priority: value as ChangePriorityUpdate['priority'], expected_version: currentVersion, idempotency_key: crypto.randomUUID() };
      const event = crypto.randomUUID();
      const operation = await governanceRequest<Application>(scopedUrl('/api/v1/requirement-center/changes/' + encodeURIComponent(id) + '/priority', project), {
        method: 'PUT', signal: abort.signal, body: JSON.stringify(payload),
        headers: {'X-Behavior-Event-ID': event, 'X-Behavior-Trace-ID': event},
      });
      const result = await waitApplication(operation.id, abort.signal);
      if (identity !== attempt.current) return;
      if (result.state !== 'applied') throw new GovernanceError(result.state === 'conflict' ? '版本已变化，请重载后重新选择。' : '保存未完成，请刷新核对后重试。', result.state === 'conflict' ? 409 : 503);
      await onSaved();
      if (identity === attempt.current) close();
    } catch (error) {
      if (identity !== attempt.current) return;
      setConflict(error instanceof GovernanceError && error.status === 409);
      setMessage(error instanceof Error ? error.message : '保存失败，选择已保留。');
    } finally { if (identity === attempt.current) { inFlight.current = false; setBusy(false); } }
  }
  return <div ref={container} onKeyDown={event => { if (event.key === 'Escape' && open) { event.stopPropagation(); close(); } }}>
    <Button type="button" data-testid="change-priority-edit" onClick={() => {
      setValue(priority || ''); setVersion(version); setMessage(''); setConflict(false); setOpen(true);
    }}>设置优先级</Button>
    {open && <section className="change-priority-editor" data-testid="change-priority-editor" aria-label="优先级编辑区">
      <label>交付优先级 <select // ds-ok: 原生选择语义与键盘可达性，项目暂无共享Select，使用卡片token。
        autoFocus data-testid="change-priority-level" value={value} disabled={busy || conflict} onChange={event => setValue(event.target.value)}>
        <option value="">请选择优先级</option>{['P0','P1','P2','P3'].map(level => <option key={level}>{level}</option>)}
      </select></label>
      <p role="status">{message || '保存后更新卡片。暂不可保存时，请稍后重试。'}</p>
      {busy && <p>关闭编辑区不会撤销已提交的保存，请稍后刷新核对。</p>}
      <div className="change-priority-actions">
        <Button type="button" data-testid="change-priority-save" disabled={busy || conflict || !value} onClick={() => void save()}>{busy ? '保存中…' : '保存'}</Button>
        {conflict && <Button type="button" data-testid="change-priority-reload" disabled={busy} onClick={() => void reload()}>重载最新值</Button>}
        <Button type="button" data-testid="change-priority-cancel" onClick={close}>{busy ? '关闭' : '取消'}</Button>
      </div>
    </section>}
  </div>;
}
