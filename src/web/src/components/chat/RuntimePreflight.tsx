import {useEffect, useRef, useState} from 'react';
import type {RuntimePreflightRead} from '../../api/generated/chat';
import {governanceRequest} from '../workbench/governanceApi';
import {Button} from '../ui/Button';
import './acceptance-operation.css';
import './runtime-preflight.css';

const labels: Record<string,string> = {python:'Python 测试',frontend:'项目验证依赖',browser:'项目验证浏览器',worker:'验证服务',isolated_acceptance:'隔离验收'};
const statuses: Record<string,string> = {ready:'探针就绪',configured:'已配置，待实际运行验证',preparable:'需要准备依赖',unavailable:'尚未就绪'};
const reasons: Record<string,string> = {python_test_runtime_unavailable:'Python 测试依赖或线程探针未通过',browser_probe_failed:'浏览器启动探针未通过',verification_toolchain_mismatch:'验证服务运行版本不匹配',browser_probe_cleanup_unconfirmed:'浏览器探针资源回收待确认',python_probe_cleanup_unconfirmed:'Python 探针资源回收待确认',container_runtime_unavailable:'容器运行服务不可用',acceptance_template_unavailable:'尚未配置批准的验收模板',project_dependencies_unverified:'项目依赖尚未验证',verification_worker_unavailable:'未检测到在线验证服务',runtime_probe_required:'配置不代表实际测试通过',package_manifest_invalid:'请核对项目测试子目录',target_unreachable:'授权测试目标不可达',runner_image_unpinned:'验证镜像尚未固定',node_version_unpinned:'Node 运行版本尚未固定'};

export function RuntimePreflight({conversationId}: {conversationId:string}) {
 const [result,setResult]=useState<RuntimePreflightRead|null>(null);
 const [error,setError]=useState(false),[busy,setBusy]=useState(true),[revision,setRevision]=useState(0);
 const active=useRef(conversationId);active.current=conversationId;
 useEffect(()=>{
  const controller=new AbortController();setBusy(true);setError(false);setResult(null);
  governanceRequest<RuntimePreflightRead>(`/api/v1/chat/conversations/${encodeURIComponent(conversationId)}/verification-preflight`,{signal:controller.signal})
   .then(value=>{if(!controller.signal.aborted&&active.current===conversationId)setResult(value);})
   .catch(()=>{if(!controller.signal.aborted)setError(true);})
   .finally(()=>{if(!controller.signal.aborted)setBusy(false);});
  return()=>controller.abort();
 },[conversationId,revision]);
 return <article className="acceptance-operation runtime-preflight" data-testid="runtime-preflight" aria-busy={busy}>
  <div className="acceptance-heading"><strong>验收环境检查</strong><Button variant="ghost" data-testid="runtime-preflight-refresh" disabled={busy} onClick={()=>setRevision(v=>v+1)}>{busy?'检查中…':'重新检查'}</Button></div>
  <p className="acceptance-muted">项目验证与隔离验收分别检查。缺失能力仅影响相关检查。</p>
  {error&&<p role="alert">暂时无法检查验收环境，请重试。未取得新的就绪结论。</p>}
  {result&&<ul>{result.checks.map(check=><li key={check.name}>{labels[check.name]||'验证能力'}：{statuses[check.status]||'待核验'}{check.reason_code&&<> · {reasons[check.reason_code]||'请核对项目验证配置'}</>}</li>)}</ul>}
  <small>这不是验收通过结论；已有任务进度会保留。</small>
 </article>;
}
