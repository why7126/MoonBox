import { sharedChatRead } from "./sharedChatRead";
import {directVerificationReasons} from './directVerificationReasons';
import { Button } from '../ui/Button';
import './recovery-operation.css';

/** Layout-only gate: no simulated backend success or write action. */
export function RecoveryOperationSkeleton() {
  return <section className="recovery-operation" data-testid="recovery-panel" aria-label="治理操作恢复" aria-busy="true">
    <header><span>治理操作详情</span><strong data-testid="recovery-business-state">等待读取可信状态</strong></header>
    <p className="recovery-muted">原执行结果与业务进度分别显示</p>
    <ol data-testid="recovery-stage-list">{['准备', '生成', '校验', '应用', '回读', '完成'].map(label => <li key={label}>{label}</li>)}</ol>
    <div className="recovery-summary"><p data-testid="recovery-reason">状态说明与阻断原因</p><p data-testid="recovery-limits" className="recovery-muted">恢复期限与剩余尝试次数将在核验后显示</p></div>
    <div className="recovery-actions"><Button variant="ghost" disabled data-testid="recovery-refresh">刷新状态</Button><Button variant="ghost" disabled className="recovery-primary" data-testid="recovery-resume">继续剩余步骤</Button><Button variant="ghost" disabled data-testid="recovery-evidence">查看证据</Button></div>
    <p data-testid="recovery-feedback" role="status" aria-live="polite" className="recovery-muted">骨架预览 · 尚未接入 API</p>
    <div data-testid="recovery-dialog-slot" hidden />
    <div data-testid="recovery-draft" hidden />
  </section>;
}

import { useCallback, useEffect, useRef, useState } from 'react';
import { ChatDialog } from './ChatDialog';
import { governanceRequest } from '../workbench/governanceApi';

import type { RecoveryOperationResponse } from '../../api/generated/governance';
export type RecoveryOperation = RecoveryOperationResponse;

const stages = ['prepare', 'generation', 'validation', 'apply', 'readback', 'complete'];
const labels = ['准备', '生成', '校验', '应用', '回读', '完成'];
const reasons: Record<string, string> = {
  recovery_expired: '恢复期限已到，请明确重新生成。', artifact_unavailable: '原成果暂不可用，无法安全续接。',
  artifact_changed: '原成果已变化，请核对证据。', retention_unconfigured: '保留策略尚未配置，暂不能承诺恢复期限。',
  permission_revoked: '当前没有写入权限。', binding_changed: '项目绑定已变化，恢复已暂停。',
  schema_incompatible: '运行服务版本不兼容，请联系管理员。', controller_unavailable: '受控写入服务暂未就绪。',
  executor_occupancy_unknown: '正在核验执行占用或处理已领取的恢复。', terminal_unknown: '原执行是否结束尚不可确认。',
  object_operation_changed: '该对象已有后续操作，不能覆盖。', recovery_verification_failed: '恢复核验未通过，原成果已保留。',
  manual_attempt_exhausted: '本次操作的手动尝试已使用，请查看证据并核对处置。',
  recovery_capability_unavailable: '恢复服务能力或心跳未就绪，本轮尚未开始生成。',
  recovery_operation_incomplete: '启动记录不完整，本轮尚未开始生成。',
};
export function RecoveryOperationPanel({ operationId, onDraft, onCompleted, draftText="", collapsed=false, writesDisabled=false, onOperation, onReadError, refreshKey="" }: {
  refreshKey?:string;
  draftText?:string; collapsed?:boolean; writesDisabled?:boolean; onOperation?:(op:RecoveryOperation|null)=>void; onReadError?:(error:boolean)=>void;
  operationId: string; onDraft: (text: string) => void; onCompleted?: () => void;
}) {
  const [operation, setOperation] = useState<RecoveryOperation | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [dialog, setDialog] = useState<'resume' | 'evidence' | 'differences' | 'draft' | null>(null);
  const [feedback, setFeedback] = useState('');
  const [confirmation, setConfirmation] = useState<RecoveryOperation | null>(null);
  const observer=useRef(onOperation);observer.current=onOperation;const errorObserver=useRef(onReadError);errorObserver.current=onReadError;
  const completing = useRef(onCompleted); completing.current = onCompleted;
  const requestKey = useRef<{version: number; key: string} | null>(null);
  const alive = useRef(true);
  const identity = useRef(operationId); identity.current = operationId;
  const writeLock = useRef(false);
  const latest=useRef<RecoveryOperation|null>(null);
  const readSequence = useRef(0);
  const pollBudget = useRef(0);
  const refresh = useCallback(async (signal?: AbortSignal) => {
    const sequence = ++readSequence.current;
    setLoading(true);
    try {
      const value = await sharedChatRead(`recovery:${operationId}`, inner => governanceRequest<RecoveryOperation>(`/api/v1/chat/governance-operations/${encodeURIComponent(operationId)}`, {signal: inner}), signal);
      if (signal?.aborted || !alive.current || sequence !== readSequence.current) return;
      if(latest.current && value.version < latest.current.version)return;
      latest.current=value; setOperation(value); observer.current?.(value); errorObserver.current?.(false); setError('');
    } catch (e) {
      if (!signal?.aborted && alive.current && sequence === readSequence.current) { errorObserver.current?.(true); if(e instanceof Error && 'status' in e && [401,403,404].includes(Number(e.status))){setOperation(null);latest.current=null;observer.current?.(null);setDialog(null);}
      setError(e instanceof Error ? e.message : '读取失败，请刷新重试'); }
    } finally { if (!signal?.aborted && alive.current && sequence === readSequence.current) setLoading(false); }
  }, [operationId]);
  useEffect(() => {
    alive.current = true; latest.current=null; setError('');setFeedback(''); setOperation(null); setDialog(null); setConfirmation(null); setSubmitting(false); writeLock.current=false; requestKey.current = null;
    return () => { alive.current = false; ++readSequence.current; };
  }, [refresh]);
  useEffect(() => {
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let running = false, recheckPending = false;
    const poll = async () => {
      if (running || controller.signal.aborted || document.hidden || pollBudget.current >= 20) return;
      running = true; ++pollBudget.current;
      try { await refresh(controller.signal); }
      finally {
        running = false;
        if (!controller.signal.aborted && !document.hidden && pollBudget.current < 20 && (recheckPending || latest.current?.state !== 'completed')) timer = setTimeout(poll, recheckPending ? 0 : 3000);
        recheckPending = false;
      }
    };
    const recheck = () => { clearTimeout(timer); if(document.hidden)return; pollBudget.current=0; if (running) recheckPending = true; else void poll(); };
    recheck();
    document.addEventListener('visibilitychange',recheck);
    window.addEventListener('governance-operation-verified',recheck);
    return () => {controller.abort();clearTimeout(timer);document.removeEventListener('visibilitychange',recheck);window.removeEventListener('governance-operation-verified',recheck);};
  },[refresh,refreshKey]);
  const completed = operation?.state === 'completed';
  useEffect(() => { if (completed) completing.current?.(); }, [completed]);
  const staleConfirmation = dialog === 'resume' && confirmation?.version !== operation?.version;
  const resume = async () => {
    if (writesDisabled || !operation || !confirmation || writeLock.current || submitting || staleConfirmation || error || !operation.allowed_actions.includes('resume')) return;
    if (requestKey.current?.version !== confirmation.version) requestKey.current = {version: confirmation.version, key: crypto.randomUUID()};
    writeLock.current=true; const requestedId=operationId; setSubmitting(true); setError('');
    try {
      await governanceRequest(`/api/v1/chat/governance-operations/${encodeURIComponent(operationId)}/recoveries`, {
        method: 'POST', body: JSON.stringify({expected_version: confirmation.version, idempotency_key: requestKey.current.key, confirmed: true}),
      });
      if (!alive.current || identity.current!==requestedId) return;
      setDialog(null); setFeedback('已提交续接请求，等待事实源核验。'); pollBudget.current=0; await refresh();
    } catch (e) { if (alive.current && identity.current===requestedId) { setError(e instanceof Error ? e.message : '续接请求未确认，请刷新'); await refresh(); } }
    finally { if (alive.current && identity.current===requestedId) {writeLock.current=false;setSubmitting(false);} }
  };
  const allowed = (action: string) => !error && !loading && (!(writesDisabled && ['resume','regenerate'].includes(action))) && operation?.allowed_actions.includes(action);
  const fillDraft=()=>{onDraft(`/${operation!.action} ${operation!.object_id}`);setDialog(null);setFeedback('已填入原会话草稿，发送后才重新生成。');};
  const verify=async()=>{
    if(writeLock.current || submitting || error || loading || !operation?.verification_actions?.includes('verify'))return;
    writeLock.current=true;const requestedId=operationId;setSubmitting(true);
    try {await governanceRequest(`/api/v1/chat/governance-operations/${encodeURIComponent(operationId)}/verifications`,{method:'POST'});
      if(!alive.current || identity.current!==requestedId)return;
      await refresh();window.dispatchEvent(new Event('governance-operation-verified'));
    } catch {if(alive.current && identity.current===requestedId){setError('核验未完成，保留上次事实，请刷新后重试');errorObserver.current?.(true);}}
    finally {if(alive.current && identity.current===requestedId){writeLock.current=false;setSubmitting(false);}}
  };
  return <section className={`recovery-operation ${collapsed ? "is-collapsed" : ""}`} data-testid="recovery-panel" aria-label="治理操作恢复">
    <div hidden={collapsed}><header><span>{operation?.object_id || '治理操作详情'}</span><strong data-testid="recovery-business-state">{completed ? '业务已完成' : submitting ? '提交中' : operation ? `业务阶段：${labels[stages.indexOf(operation.stage)] || '待核验'}` : '状态暂不可用'}</strong></header>
    <p className="recovery-muted">原执行：{operation?.execution_terminal === 'stopped' ? '已停止' : operation?.execution_terminal === 'failed' ? '失败' : operation?.execution_terminal === 'completed' ? '已结束' : '待核验'}</p>
    <ol data-testid="recovery-stage-list">{labels.map((label, i) => <li key={label} aria-current={operation?.stage === stages[i] ? 'step' : undefined}>{label}</li>)}</ol>
    <div className="recovery-summary"><p data-testid="recovery-reason">{operation?.reason_code ? reasons[operation.reason_code] || '当前操作需要核对，请查看证据或刷新状态。' : completed ? '原成果已应用并核验。' : '可用动作由后端核验结果决定。'}</p>
    <p hidden={completed} className="recovery-muted" data-testid="recovery-limits">自动重试 {operation?.auto_retry_count ?? '—'}/3 · 手动尝试 {operation?.manual_count ?? '—'} · 截止 {operation?.recovery_expires_at ? new Date(operation.recovery_expires_at).toLocaleString() : '待确认'}</p></div>
    </div><div className="recovery-actions" hidden={collapsed && completed && !operation?.verification_reason}><Button variant="ghost" data-testid="recovery-refresh" disabled={loading || submitting} onClick={() => void refresh()}>刷新状态</Button>
      {allowed('resume') && <Button variant="ghost" data-testid="recovery-resume" className="recovery-primary" disabled={submitting} onClick={() => { setConfirmation(operation); setDialog('resume'); }}>继续剩余步骤</Button>}
      {allowed('evidence') && <Button variant="ghost" data-testid="recovery-evidence" onClick={() => setDialog('evidence')}>查看证据</Button>}
      {allowed('regenerate') && <Button variant="ghost" data-testid="recovery-regenerate" onClick={() => draftText.trim()?setDialog('draft'):fillDraft()}>重新生成草稿</Button>}{operation?.verification_actions?.includes('verify')&&!error&&<Button variant="ghost" data-testid="operation-verify" disabled={submitting||loading} onClick={()=>void verify()}>重新核验</Button>}
      {!!operation?.verification_differences?.length&&<Button variant="ghost" data-testid="operation-differences" onClick={()=>setDialog('differences')}>查看差异</Button>}</div>
    {operation?.verification_reason&&<p data-testid="operation-verification-reason">{verificationReason(operation.verification_reason)} · 最近核验：{operation.last_checked_at?new Date(operation.last_checked_at).toLocaleString():'尚未确认'}</p>}
    <p role="status" aria-live="polite" data-testid="recovery-feedback">{error || feedback}</p>
    {dialog==='draft'&&<ChatDialog title="替换当前草稿" testId="operation-draft-dialog" onClose={()=>setDialog(null)} footer={<><Button onClick={()=>setDialog(null)}>取消</Button><Button onClick={fillDraft}>确认替换</Button></>}><p>当前草稿非空，替换后仍需手动发送。</p></ChatDialog>}
    {dialog==='differences'&&<ChatDialog title="相关变化" testId="operation-differences-dialog" onClose={()=>setDialog(null)}><p>操作：{operationId}</p>{operation?.verification_differences?.map(text=><p key={text}>{text}</p>)}</ChatDialog>}
    {dialog === 'resume' && operation && <ChatDialog title="继续剩余步骤" testId="recovery-resume-dialog" busy={submitting} onClose={() => setDialog(null)} footer={<><Button variant="ghost" disabled={submitting} onClick={() => setDialog(null)}>取消</Button><Button variant="ghost" data-testid="recovery-confirm" disabled={writesDisabled || submitting || staleConfirmation || !!error || !allowed('resume')} onClick={() => void resume()}>{submitting ? '提交中…' : '确认续接'}</Button></>}><p>{operation.object_id}</p><p>当前阶段：{labels[stages.indexOf(operation.stage)] || '待核验'}。将复用已保存成果，从当前可信阶段续接校验、应用与回读。原执行终态保持不变，不重新调用模型。</p><p role="status">{staleConfirmation ? '状态已变化，请关闭后重新确认。' : error}</p></ChatDialog>}
    {dialog === 'evidence' && operation && <ChatDialog title="操作证据" testId="recovery-evidence-dialog" onClose={() => setDialog(null)} footer={<Button variant="ghost" onClick={() => setDialog(null)}>关闭</Button>}><p>操作：{operation.id}</p><p>成果：{operation.candidate_id || '尚未确认'}</p><p>应用：{operation.application_id || '尚未应用'}</p><p>状态版本：{operation.version}</p><p>这里仅展示脱敏标识，原文按项目权限查看。</p></ChatDialog>}
  </section>;
}

export function verificationReason(reason?:string|null) {return directVerificationReasons[reason||''] || ({dependency_conflict:'相关文件已变化，下一步暂不可执行',proof_missing:'完成证明缺失',permission_revoked:'当前无权限',permission_denied:'当前无权限',executor_occupancy_unknown:'执行占用待确认',stale_operation:'该操作已非当前操作',proof_invalid:'完成证明无法核验'} as Record<string,string>)[reason||'']||'执行结果待核对';}
