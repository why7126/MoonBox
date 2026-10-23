// Isolated synthetic API responses; uses the production page and document drawer.
import React from 'react';
import {createRoot} from 'react-dom/client';
import {RequirementCenterPage} from '../src/pages/catalog/RequirementCenterPage';
import '../src/styles/globals.css';
import '../src/styles/tokens.generated.css';
const params=new URLSearchParams(location.search);
const mode=params.get('mode')||'success';
const theme=params.get('theme')||'dark';
localStorage.setItem('moonbox.session',JSON.stringify({username:'隔离验收',access_token:'synthetic-test'}));
localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));
const stages=['capture','planning','review-ready','approved','sprint-planning','ready-dev','development','acceptance','done'];
const base={snapshot_revision:'synthetic-v1',current_user:{name:'隔离验收'},workspaces:[{workspace_id:'sample',name:'合成验证项目',role:'拥有者'}],selected_workspace_id:'sample',sprint_option_details:[{sprint_id:'sprint-001',status:'planning',lifecycle_stage:'change'}],stats:{total:9,bugs:9,requirements:0,standalone_changes:0,blocked:0},issues:stages.map((stage,i)=>({id:`BUG-${9100+i}`,title:`${stage} 标签验证`,type:'bug',source:'review',severity:'medium',owner:'产品研发协作团队',stage,sprint_id:'sprint-001',root_cause_state:i%2?'pending':'confirmed',root_cause_reason:i===1?'conflict':null,estimated_person_days:[0,.5,1,3,3.01,5,8,10,13][i],estimate_status:'available',documents:['root-cause.md'],document_entries:[{name:'root-cause.md',type:'markdown',open_mode:'drawer',url:`/api/v1/requirement-center/issues/BUG-${9100+i}/documents/root-cause.md`,capability:{readable:true,human_editable:false}}]}))};
const original=window.fetch;
window.fetch=async (input,init)=>{
 const url=String(input);if(!url.includes('/api/v1/'))return original(input,init);
 const doc=url.includes('/documents/');
 if(doc && mode==='loading')return new Promise<Response>(()=>{});
 const fail=doc&&mode!=='success';
 const data=url.includes('/projects')?{...base,projects:[{space_id:'sample',repository_id:'repo',readonly:false,status:'connected'}]}:url.includes('/context')?base:doc?{name:'root-cause.md',content:'# 根因分析\n\n## 根因状态\nstatus: confirmed\n\n## 根因分析\n合成样本缓存未失效。',version:'sample'}:{ready:false};
 return new Response(JSON.stringify(fail?{code:mode==='denied'?403:404,message:mode==='denied'?'无权读取文档':'文档不存在',data:null}:{code:0,data}),{status:fail?(mode==='denied'?403:404):200,headers:{'content-type':'application/json'}});
};
createRoot(document.getElementById('root')!).render(<RequirementCenterPage/>);
