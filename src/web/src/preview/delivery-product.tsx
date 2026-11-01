import {createRoot} from 'react-dom/client';
import {RequirementCenterPage} from '../pages/catalog/RequirementCenterPage';
import {deliveryFixture,previewResponse} from './delivery-fixture';
import '../styles/globals.css';
import '../styles/tokens.generated.css';
import {saveUiTheme} from '../pages/home/uiPreferences';
const parameters = new URLSearchParams(location.search);
if (parameters.has('theme')) saveUiTheme(parameters.get('theme') === 'light' ? 'light' : 'dark');
// Only this explicit development HTML entry uses synthetic data. No API writes.
window.fetch = async (input, init) => {
  if (init?.method && init.method !== 'GET') return new Response(JSON.stringify({code:2601,message:'合成只读预览不执行写入'}),{status:403});
  let data=previewResponse(input);
  if(['multi','acceptance'].includes(parameters.get('scenario') || '') && /\/(context|projects)/.test(String(input))){
    const sources=[deliveryFixture.issues[0].sources[0],{...deliveryFixture.issues[0].sources[0],id:'REQ-0055-shared-delivery',title:'共享交付来源'}];
    const acceptance=parameters.get('scenario')==='acceptance';
    const row=deliveryFixture.issues[0];
    data={...deliveryFixture,issues:[{...row,stage:acceptance?'acceptance':'ready-dev',source_issues:sources,sources,
      checks_deferred: acceptance ? !String(input).includes('object_id=') : undefined,
      acceptance_blocked_reason: acceptance ? (String(input).includes('object_id=') ? '仍有2项验收证据待补齐' : '验收待检查') : undefined,
      manual_acceptance_progress:acceptance?[0,2]:null,
      document_entries:acceptance?[...row.document_entries,{...row.document_entries[0],name:'acceptance.md',url:`/api/v1/requirement-center/changes/${row.id}/documents/acceptance.md`}]:row.document_entries,
      action:{label:acceptance?'完成 / 归档':'开始开发',command:'',disabled_reason:null}}]};
  }
  if (/\/(context|projects)/.test(String(input))) {
    const role=parameters.get('role') || 'admin';
    const fixture=data as typeof deliveryFixture;
    data={...fixture,workspaces:fixture.workspaces.map(w=>({...w,role:role==='viewer'?'查看者':role==='writer'?'编辑者':'管理员'})),
      projects:fixture.projects.map(p=>({...p,readonly:role==='viewer'})),
      issues:role==='restricted'?[]:fixture.issues.map(row=>({...row,can_send:role!=='viewer',execution_reason:role==='viewer'?'当前项目只读':undefined}))};
  }
  return new Response(JSON.stringify({data}),{headers:{'Content-Type':'application/json'}});
};
createRoot(document.getElementById('root')!).render(<RequirementCenterPage />);
