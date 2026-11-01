// Synthetic authorized API responses, shared by browser preview and regressions.
const source = {id:'REQ-0048-chat-isolated-acceptance-orchestration',type:'requirement',title:'Chat 隔离验收环境编排与原操作续接',status:'in_sprint',document_entries:[
  {name:'requirement.md',type:'markdown',url:'/api/v1/requirement-center/issues/REQ-0048-chat-isolated-acceptance-orchestration/documents/requirement.md'},
  {name:'acceptance.md',type:'markdown',url:'/api/v1/requirement-center/issues/REQ-0048-chat-isolated-acceptance-orchestration/documents/acceptance.md'},
]};
export const deliveryFixture = {
  repository_id:'preview',snapshot_revision:'delivery-preview-v1',selected_workspace_id:'preview',
  current_user:{name:'演示用户',avatar_initial:'演',can_access_admin:false,permissions:['requirement:read']},
  workspaces:[{workspace_id:'preview',name:'交付卡片验证',slug:'preview',organization_name:'合成测试',description:'无真实数据',timezone:'Asia/Shanghai',member_count:1,role:'管理员',status:'ACTIVE'}],
  projects:[{space_id:'preview',repository_id:'preview',status:'connected',readonly:false}],
  sprint_option_details:[{sprint_id:'sprint-016',lifecycle_stage:'change',status:'planning',label:'sprint-016',status_label:'规划中'},{sprint_id:'sprint-015',lifecycle_stage:'archive',status:'archived',label:'sprint-015',status_label:'已完成'}],
  current_iteration_capacity:[],sprint_options:['sprint-015','sprint-016'],sprint_metrics:{total_count:1,completed_count:0},
  stats:{total:3,requirements:1,bugs:0,standalone_changes:1,blocked:0,drift:0},
  issues:[
    {id:'add-chat-validation-orchestration',sprint_id:'sprint-016',stage:'development',title:'Chat 隔离验收环境编排与原操作续接',sources:[source]},
    {id:'add-isolated-candidate-validation',sprint_id:'sprint-015',stage:'done',title:'固定候选隔离验收',sources:[source]},
    {id:'guard-delivery-reference',sprint_id:'sprint-016',stage:'acceptance',title:'独立交付引用保护',sources:[]},
  ].map(row=>({...row,type:'change',card_kind:'delivery',target_change_id:row.id,object_id:row.id,source_issues:row.sources,
    checks_deferred: undefined as boolean | undefined, acceptance_blocked_reason: undefined as string | undefined,
    owner:'产品团队',source:'active',priority:'P1',updated_at:'26/10/31 17:00',task_progress:[1,2],manual_acceptance_progress:row.stage==='acceptance'?[0,2]:null,
    documents:['proposal.md','tasks.md','trace.md','sprint.md'],document_entries:['proposal.md','tasks.md','trace.md','sprint.md'].map(name=>({name,type:'markdown',url:`/api/v1/requirement-center/changes/${row.id}/documents/${name}`,capability:{readable:true,human_editable:false,task_toggle_only:false,ai_mutable:false,reason:'合成只读样本'}})),
    action:{label:row.stage==='development'?'查看进度':'完成 / 归档',command:`查看进度 ${row.id}`,disabled_reason:row.stage==='acceptance'?'验收尚未通过':null},
    completion_hint:row.stage==='done'?'子交付已完成；来源仍有未交付范围':null,
  })),
};
export function previewResponse(input: RequestInfo | URL) {
  const url = String(input);
  if(url.includes('/projects') || url.includes('/context')) return deliveryFixture;
  if(url.includes('/documents/')) {
    const id = url.split('/documents/')[0].split('/').pop();
    return {content:`# ${id}\n\n## 研发任务\n- [x] 1.1 已完成样本\n- [ ] 1.2 待完成样本\n\n仅为合成只读验证，不执行真实命令。`,version:'a'.repeat(64),editable:false,capability:{readable:true,human_editable:false,task_toggle_only:false}};
  }
  return {items:[]};
}
