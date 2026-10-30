import { useEffect, useRef, useState } from 'react';
import type { WorkspaceList } from '../../api/generated/workspaces';
import { governanceRequest, GovernanceError } from '../workbench/governanceApi';
import { ChatDialog } from '../chat/ChatDialog';
import { WorkspaceOverview, workspacePurpose, type WorkspaceOverviewState } from './WorkspaceOverview';

type Point = { id: string; sequence: number; state: string; protection_reasons: string[]; created_at: string; policy_version: string };
type Candidate = { id: string; state: string; change_id: string; source_commit: string; target_commit: string; candidate_commit?: string; fingerprint?: string; error_code?: string; validation?: {environment_key?:string; evidence_digest?:string; runtime_digest?:string; checks?:{database:string;version:string;checks_passed:number;browser:string}[]} };
type Preflight = { fingerprint: string; can_restore: boolean; items: {path: string; action: string}[] };
type Capability = {can_operate_sprint: boolean; can_prepare: boolean; can_confirm: boolean; reason_code?: string};
type Action = 'recover-directory' | 'merge-diff' | 'merge-status' | 'create' | 'cleanup' | 'restore' | 'protect' | 'confirm' | 'repair' | 'diff' | 'resume';
const labels: Record<Action, string> = {'recover-directory': '创建独立恢复目录', 'merge-diff': '查看候选差异', 'merge-status': '合入操作状态', create: '创建独立工作区', cleanup: '清理独立目录', restore: '撤销选定修改', protect: '保护恢复点', confirm: '确认成果合入', repair: '返回返修', diff: '查看恢复差异', resume: '续接恢复操作'};
const phase: Record<string, string> = {validated: '验证通过，待确认', validation_blocked: '组合验收未通过', prepared: '候选已建立', validating: '验证中', integrated: '已合入', invalidated: '已返回返修', ready: '可用', removing: '清理中', removed: '目录已清理', preparing: '准备中'};
const validationReason: Record<string, string> = {
  isolated_candidate_validation_unavailable: '尚未配置批准的隔离验收模板。',
  candidate_images_unavailable: '批准的运行镜像不可用，独立开发与合入入口暂未开放。',
  candidate_checks_failed: '候选检查未通过，请在原工作区修复后重新验证。',
  candidate_command_failed: '环境准备或候选检查失败，请核对验收证据。',
  candidate_cleanup_pending: '临时资源清理尚未确认，不能合入；重新核验会先检查现场。',
  candidate_interrupted: '上次验证已中断，现场已核对；可重新验证同一候选。',
  candidate_dependency_mismatch: '依赖锁与批准模板不一致，需要更新受控模板。',
  candidate_capacity_unavailable: '隔离验收容量已占用，请稍后重试。',
  candidate_mysql_version_unsupported: '数据库实际版本不符合 MySQL 8.4 模板。',
};
const actionName: Record<string, string> = {restore: '恢复原内容', delete: '移除本轮新增', conflict: '与后续修改冲突', unsupported: '仅保留元数据，不能直接恢复', unchanged: '本轮未修改', already_restored: '已是原内容'};
const base = '/api/v1/chat/workspaces';

export function WorkspacePanel({ spaceId, repositoryId, conversationId, initialWorkspaceId, onClose }: {
  spaceId: string; repositoryId: string; conversationId?: string; initialWorkspaceId?: string; onClose: () => void;
}) {
  const [state, setState] = useState<WorkspaceOverviewState>('loading');
  const [catalog, setCatalog] = useState<WorkspaceList | null>(null);
  const [selected, setSelected] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [refresh, setRefresh] = useState(0);
  const [points, setPoints] = useState<Point[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [capability, setCapability] = useState<Capability | null>(null);
  const [action, setAction] = useState<Action | null>(null);
  const [busy, setBusy] = useState(false);
  const [change, setChange] = useState('');
  const [before, setBefore] = useState('');
  const [after, setAfter] = useState('');
  const [paths, setPaths] = useState('');
  const [preflight, setPreflight] = useState<Preflight | null>(null);
  const [protectedPoint, setProtectedPoint] = useState(true);
  const [operationRows, setOperationRows] = useState<{id:string; state:string; governance_state?:string; error_code?:string}[]>([]);
  const [mergeRows, setMergeRows] = useState<{id:string; state:string; governance_state?:string; error_code?:string}[]>([]);
  const [recoveryFiles, setRecoveryFiles] = useState<{path:string;kind:string;restorable:boolean}[]>([]);
  const [filesLimited, setFilesLimited] = useState(false);
  const [mergeFiles, setMergeFiles] = useState<{path:string;added:number|null;removed:number|null}[]>([]);
  const [operationId, setOperationId] = useState('');
  const [candidateId, setCandidateId] = useState('');
  const requestId = useRef('');
  const epoch = useRef(0);
  const mounted = useRef(true);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; epoch.current++; }; }, []);
  const scope = {space_id: spaceId, repository_id: repositoryId};
  const workspace = catalog?.items.find(item => item.id === selected);
  const candidate = candidates.find(item => item.id === candidateId);
  const selectedPaths = paths.split('\n').map(path => path.trim()).filter(Boolean);
  const fail = (cause: unknown) => setError(cause instanceof Error ? cause.message : '操作暂时不可用，请刷新后重试。');
  const post = <T,>(path: string, payload: object) => governanceRequest<T>(base + path, {method: 'POST', body: JSON.stringify({...scope, ...payload})});
  useEffect(() => {
    const controller = new AbortController(); epoch.current++;
    setCatalog(null); setState('loading'); setError(''); setAction(null);
    const query = new URLSearchParams({space_id: spaceId, repository_id: repositoryId});
    void governanceRequest<WorkspaceList>(`${base}?${query}`, {signal: controller.signal}).then(data => {
      if (controller.signal.aborted) return;
      setCatalog(data); setSelected(current => data.items.some(item => item.id === current) ? current : data.items.find(item => item.id === initialWorkspaceId)?.id || data.items[0]?.id || ''); setState('ready');
    }).catch(cause => {
      if (controller.signal.aborted) return;
      setState(cause instanceof GovernanceError && cause.status === 403 ? 'forbidden' : cause instanceof GovernanceError && cause.status === 409 ? 'stale' : 'error'); fail(cause);
    });
    return () => controller.abort();
  }, [spaceId, repositoryId, refresh]);
  useEffect(() => {
    const controller = new AbortController(); epoch.current++;
    setOperationRows([]); setMergeRows([]); setOperationId(''); setPoints([]); setCandidates([]); setCapability(null); setPreflight(null); setBefore(''); setAfter(''); setCandidateId(''); setAction(null);
    if (!selected || state !== 'ready') return () => controller.abort();
    const query = new URLSearchParams({...scope, workspace_id: selected});
    void Promise.all([
      governanceRequest<{items: Point[]}>(`${base}/recovery-points?${query}`, {signal: controller.signal}),
      governanceRequest<{items: Candidate[]}>(`${base}/merge-candidates?${query}`, {signal: controller.signal}),
      governanceRequest<Capability>(`${base}/merge-capability?${query}`, {signal: controller.signal}),
      governanceRequest<{restores:typeof operationRows;merges:typeof mergeRows}>(`${base}/operations?${query}`, {signal:controller.signal}),
    ]).then(([recovery, merges, rights, operations]) => {
      if (controller.signal.aborted) return;
      setOperationRows(operations.restores || []); setMergeRows(operations.merges || []);
      setPoints(recovery.items); setCandidates(merges.items); setCapability(rights);
      const complete = recovery.items.filter(item => item.state === 'complete');
      const pair = complete.find(point => complete.some(other => other.id !== point.id && other.policy_version === point.policy_version));
      setAfter(pair?.id || complete[0]?.id || ''); setBefore(complete.find(point => point.id !== pair?.id && point.policy_version === pair?.policy_version)?.id || complete[0]?.id || ''); setCandidateId(merges.items[0]?.id || '');
    }).catch(cause => { if (!controller.signal.aborted) fail(cause); });
    return () => controller.abort();
  }, [spaceId, repositoryId, selected, state, refresh]);
  useEffect(() => {
    const controller = new AbortController();
    setRecoveryFiles([]); setFilesLimited(false);
    if (!['restore','diff'].includes(action || '') || !before || !after) return () => controller.abort();
    const ids = [...new Set([before,after])];
    void Promise.all(ids.map(point_id => governanceRequest<{items:typeof recoveryFiles;next_cursor?:string}>(
      `${base}/recovery-files?${new URLSearchParams({...scope,workspace_id:selected,point_id})}`, {signal:controller.signal})))
      .then(pages => {
        if (controller.signal.aborted) return;
        const files = new Map<string, typeof recoveryFiles[number]>();
        pages.forEach(page => page.items.forEach(file => files.set(file.path,file)));
        setRecoveryFiles([...files.values()].sort((a,b)=>a.path.localeCompare(b.path)));
        setFilesLimited(pages.some(page => !!page.next_cursor));
      }).catch(cause => {if (!controller.signal.aborted) fail(cause);});
    return () => controller.abort();
  }, [spaceId,repositoryId,selected,before,after,action]);
  async function execute(work: () => Promise<unknown>, success: string | ((result: unknown) => string), reload = true) {
    if (busy) return;
    const generation = epoch.current; setBusy(true); setError('');
    try {
      const result = await work();
      if (!mounted.current || generation !== epoch.current) return;
      setNotice(typeof success === 'function' ? success(result) : success); if (reload) { setAction(null); setRefresh(value => value + 1); }
    } catch (cause) { if (mounted.current && generation === epoch.current) fail(cause); }
    finally { if (mounted.current) setBusy(false); }
  }
  function open(value: Action) {
    requestId.current = crypto.randomUUID();
    setAction(value); setError(''); setPreflight(null); setMergeFiles([]);
    if (value === 'resume') setOperationId(operationRows.find(row => row.state !== 'completed')?.id || operationRows[0]?.id || '');
    if (value === 'merge-diff' && candidate) {
      const generation = epoch.current;
      const query = new URLSearchParams(scope);
      void governanceRequest<{items: typeof mergeFiles}>(`${base}/merge-candidates/${candidate.id}/files?${query}`).then(result => {if (mounted.current && generation === epoch.current) setMergeFiles(result.items);}).catch(cause => { if (mounted.current && generation === epoch.current) fail(cause); });
    }
  }
  const pointOptions = points.filter(item => item.state === 'complete').map(item => <option key={item.id} value={item.id}>恢复点 {item.sequence} · {new Date(item.created_at).toLocaleString()}</option>);
  function check() {
    const generation = epoch.current;
    return execute(async () => { const value = await post<Preflight>('/recovery-preflight', {workspace_id: selected, before_id: before, after_id: after, paths: selectedPaths}); if (mounted.current && generation === epoch.current) setPreflight(value); }, '已重新核对当前文件。', false);
  }
  async function submit() {
    if (action === 'create') return execute(() => post('/development', {change_id: change}), '开发工作区已就绪。');
    if (action === 'recover-directory') return execute(() => post('/recovery-directory', {workspace_id:selected, point_id:before, request_id:requestId.current}), result => Number((result as {unsupported_files?:number}).unsupported_files || 0) > 0 ? '独立目录已建立；部分文件仅有元数据，请核对恢复范围。' : '独立恢复目录已建立，原工作区保持不变。');
    if (action === 'cleanup' && workspace) return execute(() => post('/cleanup', {workspace_id: selected, expected_revision: workspace.revision}), '独立目录已清理，历史恢复记录保留。');
    if (action === 'protect') return execute(() => post('/recovery-protection', {workspace_id: selected, point_id: before, protected: protectedPoint}), protectedPoint ? '恢复点已保护。' : '已解除自己的人工保护。');
    if (action === 'restore' && preflight?.can_restore && conversationId) return execute(async () => {
      const value = await post<{id: string; state: string}>('/restore', {workspace_id: selected, conversation_id: conversationId, before_id: before, after_id: after, paths: selectedPaths, fingerprint: preflight.fingerprint, request_id: requestId.current});
      if (mounted.current) setOperationId(value.id);
    }, '选定文件恢复完成。');
    if (action === 'confirm' && candidate?.fingerprint) return execute(() => post(`/merge-candidates/${candidate.id}/confirm`, {fingerprint: candidate.fingerprint, request_id: requestId.current}), value => (value as {state:string}).state === 'completed' ? '成果已合入主线，未自动归档或发布。' : '确认已记录，合入已排队。');
    if (action === 'repair' && candidate) return execute(() => post(`/merge-candidates/${candidate.id}/repair`, {}), '候选已作废，可在原工作区继续返修。');
    if (action === 'resume') return execute(() => post(`/restore/${operationId}/resume`, {}), '恢复操作已续接。');
  }
  const writable = catalog?.can_register_main === true;
  const submitDisabled = busy || !writable || ['diff','merge-diff','merge-status'].includes(action || '') || (action === 'resume' && !operationId) || (action === 'create' && !change.trim()) ||
    (action === 'restore' && (!preflight?.can_restore || !conversationId)) || (action === 'confirm' && (!candidate?.fingerprint || !capability?.can_confirm));
  return <div className="moonbox-workspace-panel"><ChatDialog title="仓库工作区" testId="workspace-details-dialog" inactive={!!action} onClose={onClose}>
    <WorkspaceOverview state={state} items={catalog?.items || []} error={error} onReload={() => setRefresh(value => value + 1)}>
      {error && <p role="alert">{error}</p>}{notice && <p role="status">{notice}</p>}
      <section className="workspace-card" data-testid="workspace-summary"><h2>执行工作区</h2>
        <p className="workspace-muted">主工作区保存正式治理事实；切换查看不会改变当前会话的执行目录。</p>
        <label>查看工作区<select data-testid="workspace-picker" value={selected} disabled={busy || state !== 'ready'} onChange={event => setSelected(event.target.value)}><option value="">请选择</option>{catalog?.items.map(item => <option key={item.id} value={item.id}>{workspacePurpose[item.purpose] || '工作区'} · {item.change_id || item.id.slice(0, 8)}</option>)}</select></label>
        {workspace && <dl className="workspace-facts"><div><dt>目录</dt><dd>{phase[workspace.lifecycle] || workspace.lifecycle}</dd></div><div><dt>执行</dt><dd>{workspace.execution_state === 'occupied' ? '有操作占用' : '空闲'}</dd></div><div><dt>起始提交</dt><dd>{workspace.base_commit.slice(0, 12)}</dd></div></dl>}
        <div className="workspace-actions" data-testid="workspace-actions">
          {!catalog?.items.some(item => item.purpose === 'main') && <button disabled={!writable || busy} onClick={() => execute(() => post('/main', {}), '主工作区已登记。')}>登记主工作区</button>}
          <button data-testid="workspace-create" disabled={!catalog?.can_create_development || busy} onClick={() => open('create')}>创建独立工作区</button>
          <button disabled={!workspace || !writable || busy || workspace.lifecycle !== 'ready' || !['main','development'].includes(workspace.purpose)} onClick={() => execute(async () => { const row = await post<{id: string}>('/sessions', {workspace_id: selected, request_id: crypto.randomUUID(), predecessor_id: conversationId}); const url = new URL(window.location.href); url.searchParams.set('conversation_id', row.id); window.location.assign(url.toString()); }, '新会话已创建。')}>在此新建会话</button>
          <button data-testid="workspace-clean" disabled={!workspace || workspace.purpose === 'main' || !writable || busy} onClick={() => open('cleanup')}>清理工作区</button>
        </div>{!catalog?.can_create_development && <p className="workspace-muted">{validationReason[catalog?.reason_code || ''] || '当前不能创建独立开发工作区。'}</p>}
      </section>
      <div className="workspace-delivery-grid"><section className="workspace-card" data-testid="recovery-summary"><h2>恢复点</h2>
        <p>有文件变化才保留新版本；普通恢复点按保留数量轮转，受保护版本单独保留（默认保留最近 10 个普通版本）。</p>
        {points.length ? <ul>{points.slice(0, 4).map(point => <li key={point.id}>恢复点 {point.sequence} · {point.state === 'expired' ? '已轮转' : point.protection_reasons.length ? '受保护' : '可用'}</li>)}</ul> : <p className="workspace-muted">尚无文件恢复点。只读对话不会创建恢复点。</p>}
        <div className="workspace-actions" data-testid="recovery-actions"><button data-testid="recovery-diff" disabled={!points.length || busy} onClick={() => open('diff')}>查看差异</button><button data-testid="recovery-restore" disabled={!points.length || !writable || busy} onClick={() => open('restore')}>撤销选定修改</button><button disabled={!points.length || !writable || busy} onClick={() => open('protect')}>管理保护</button><button disabled={!points.length || !writable || busy} onClick={() => open('recover-directory')}>独立恢复目录</button><button disabled={!writable || busy} onClick={() => open('resume')}>续接恢复</button></div>
      </section><section className="workspace-card" data-testid="merge-summary"><h2>成果合入</h2>
        <p>验证组合版本后，由当前具有迭代操作权限的人确认。</p>
        <label>合入候选<select value={candidateId} onChange={event => setCandidateId(event.target.value)} disabled={busy}><option value="">暂无候选</option>{candidates.map(item => <option key={item.id} value={item.id}>{item.change_id} · {phase[item.state] || item.state}</option>)}</select></label>
        {candidate && <p>来源 {candidate.source_commit.slice(0, 8)} → 主线 {candidate.target_commit.slice(0, 8)}<br />{phase[candidate.state] || candidate.state}</p>}
        {candidate?.validation?.environment_key && <p className="workspace-muted">验收环境 {candidate.validation.environment_key.slice(0, 12)} · 证据 {candidate.validation.evidence_digest?.slice(0, 12)} · 运行镜像 {candidate.validation.runtime_digest?.slice(7, 19)}</p>}
        {candidate?.validation?.checks && <ul>{candidate.validation.checks.map(check => <li key={check.database}>{check.database === "mysql" ? "MySQL" : "SQLite"} {check.version} · {check.checks_passed} 项检查通过 · {check.browser} 浏览器通过</li>)}</ul>}
        {candidate?.error_code && <p role="status">{validationReason[candidate.error_code] || '候选验证尚未就绪，请重新核验或返回返修。'}</p>}
        {candidate && ['prepared','validation_blocked','validating'].includes(candidate.state) && <button disabled={busy || !capability?.can_operate_sprint} onClick={() => execute(() => post(`/merge-candidates/${candidate.id}/validate`, {}), '候选验证状态已更新。')}>重新核验候选</button>}
        <div className="workspace-actions" data-testid="merge-actions"><button disabled={!candidate || busy} onClick={() => open('merge-diff')}>查看候选差异</button><button disabled={!mergeRows.length || busy} onClick={() => open('merge-status')}>操作状态</button><button data-testid="merge-validate" disabled={!capability?.can_prepare || busy} onClick={() => execute(() => post('/merge-candidates', {workspace_id: selected, request_id: crypto.randomUUID()}), '候选状态已更新，请查看验证结果。')}>建立验证候选</button><button data-testid="merge-confirm" disabled={!capability?.can_confirm || candidate?.state !== 'validated' || busy} onClick={() => open('confirm')}>确认合入</button><button disabled={!candidate || !capability?.can_operate_sprint || busy || candidate.state === 'integrated'} onClick={() => open('repair')}>返回返修</button></div>
      </section></div>
    </WorkspaceOverview>
  </ChatDialog>{action && <ChatDialog title={labels[action]} testId={`workspace-${action}-dialog`} busy={busy} onClose={() => setAction(null)} footer={<><button disabled={busy} onClick={() => setAction(null)}>关闭</button>{!['diff','merge-diff','merge-status'].includes(action) && <button disabled={submitDisabled} onClick={submit}>{busy ? '处理中…' : labels[action]}</button>}</>}>
    {error && <p role="alert">{error}</p>}
    {action === 'create' && <label>独立交付 Change<input value={change} onChange={event => setChange(event.target.value)} placeholder="输入已纳入迭代的变更标识" /></label>}
    {action === 'cleanup' && <p>仅清理选定的独立目录。系统会拒绝有未合入修改、进行中操作或受保护引用的工作区。</p>}
    {['restore', 'diff', 'protect', 'recover-directory'].includes(action) && <label>原恢复点<select value={before} onChange={event => {setBefore(event.target.value); setPreflight(null); requestId.current = crypto.randomUUID();}}>{pointOptions}</select></label>}
    {['restore', 'diff'].includes(action) && <><label>修改结束恢复点<select value={after} onChange={event => {setAfter(event.target.value); setPreflight(null); requestId.current = crypto.randomUUID();}}>{points.filter(point => point.state === 'complete' && point.policy_version === points.find(item => item.id === before)?.policy_version).map(point => <option key={point.id} value={point.id}>恢复点 {point.sequence}</option>)}</select></label>{recoveryFiles.length > 0 && <fieldset className="workspace-file-selection"><legend>选择需要核对的文件</legend>{recoveryFiles.map(file => <label key={file.path}><input type="checkbox" checked={selectedPaths.includes(file.path)} disabled={busy || !file.restorable} onChange={event => {setPaths((event.target.checked ? [...selectedPaths,file.path] : selectedPaths.filter(path => path !== file.path)).join('\n'));setPreflight(null);requestId.current=crypto.randomUUID();}} />{file.path}{!file.restorable && '（仅元数据）'}</label>)}</fieldset>}{filesLimited && <p>文件较多，此处展示每个恢复点的前 100 项；其他文件可通过下方相对路径选定。</p>}<label>选定文件，每行一个相对路径<textarea rows={4} value={paths} onChange={event => {setPaths(event.target.value); setPreflight(null); requestId.current = crypto.randomUUID();}} /></label><button disabled={busy || !before || !after || !selectedPaths.length} onClick={check}>重新核对差异</button>{preflight && <ul data-testid="recovery-preflight-results">{preflight.items.map(item => <li key={item.path}>{item.path}：{actionName[item.action] || item.action}</li>)}</ul>}{action === 'restore' && !conversationId && <p>请先在此工作区创建会话，再发起恢复。</p>}</>}
    {action === 'confirm' && <p>将已验证候选 {candidate?.candidate_commit?.slice(0, 12)} 合入主线。提交时会重新检查迭代权限、源和目标版本；任一变化都会拒绝合入。</p>}
    {action === 'repair' && <p>作废当前候选并保留开发目录，后续修改需要重新验证和确认。</p>}
    {action === 'resume' && <label>恢复操作<select value={operationId} onChange={event => setOperationId(event.target.value)}><option value="">请选择操作</option>{operationRows.map(row => <option key={row.id} value={row.id}>{row.id.slice(0,8)} · {row.state === 'completed' ? '已完成' : row.state === 'blocked' ? '需重新核对' : '处理中'}</option>)}</select></label>}
    {action === 'protect' && <label>人工保护<select value={protectedPoint ? 'protect' : 'release'} onChange={event => setProtectedPoint(event.target.value === 'protect')}><option value="protect">保护此恢复点</option><option value="release">解除我添加的保护</option></select></label>}
    {action === 'recover-directory' && <p>在独立目录提取此恢复点，不覆盖当前文件，也不占用活动开发工作区名额。链接等不支持完整恢复的文件会保留能力说明。</p>}
    {action === 'merge-diff' && <><p>来源 {candidate?.source_commit.slice(0,12)} → 目标 {candidate?.target_commit.slice(0,12)}；组合版本 {candidate?.candidate_commit?.slice(0,12) || '未生成'}</p><p>显示前 100 项文件统计；完整验收范围以服务端候选记录为准。</p><ul>{mergeFiles.map(item => <li key={item.path}>{item.path} · 新增 {item.added ?? '二进制'} / 删除 {item.removed ?? '二进制'}</li>)}</ul></>}
    {action === 'merge-status' && <ul>{mergeRows.map(row => <li key={row.id}>{row.id.slice(0,8)} · {row.state === 'completed' ? (row.governance_state === 'completed' ? '已合入，治理记录已同步' : '已合入，治理记录待同步') : row.state === 'queued' ? '排队中' : '需核对'}{(row.state !== 'completed' || row.governance_state !== 'completed') && <button disabled={busy || !capability?.can_operate_sprint} onClick={() => execute(() => post(`/merge-operations/${row.id}/resume`, {}), '操作状态已重新核对。')}>重新核对并续接</button>}</li>)}</ul>}
  </ChatDialog>}</div>;
}
