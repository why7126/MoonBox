// Dev-only visual fixture: never bundled by the production index entry.
import React from "react";
import { createRoot } from "react-dom/client";
import { RequirementCenterPage } from "../src/pages/catalog/RequirementCenterPage";
import { ChatWorkbenchPage } from "../src/pages/catalog/ChatWorkbenchPage";
import "../src/styles/globals.css";
import "../src/styles/tokens.generated.css";
localStorage.setItem("moonbox.session",JSON.stringify({username:"视觉测试",access_token:"synthetic-test-token"}));
const row={id:"synthetic",space_id:"space",repository_id:"sandbox",title:"对话与轨迹验收",archived:false,pinned:false,active_turn_id:null,created_at:"2026-09-11T00:00:00Z",updated_at:"2026-09-11T00:00:00Z"};
const events=[{type:"execution.state",payload:{status:"running"}},{type:"execution.output",payload:{text:"正在读取项目文件。",item_id:"a"}},{type:"execution.tool",payload:{item_id:"tool",executor_turn_id:"run",type:"commandExecution",phase:"started",detail_version:1,arguments:{command:"printf hello",cwd:"[工作区]"}}},{type:"execution.tool",payload:{item_id:"tool",executor_turn_id:"run",type:"commandExecution",phase:"completed",detail_version:1,status:"completed",result:"hello",exit_code:0,duration_ms:50,timing_source:"executor"}},{type:"execution.state",payload:{status:"completed"}}].map((e,i)=>({...e,sequence:i+1}));
window.fetch=async(input)=>{
 const url=new URL(String(input),location.origin);let data:unknown;
 if(url.pathname.endsWith('/requirement-center/projects'))data={projects:[{space_id:'space',repository_id:'sandbox',status:'connected',readonly:false}],currentUser:{name:"视觉测试",avatarInitial:"测",canAccessAdmin:false,permissions:[]},workspaces:[{workspaceId:"space",name:"验收空间",role:"成员",memberCount:1}],selectedWorkspaceId:"space"};
 else if(url.pathname.endsWith('/governance-candidates'))data={items:[]};
 else if(url.pathname.endsWith('/spaces'))data=[{id:"space",name:"验收空间"}];
 else if(url.pathname.endsWith('/capabilities'))data={execution_ready:true,reason:"执行服务已就绪",repositories:[{id:"sandbox",space_id:"space"}]};
 else if(url.pathname.endsWith('/relations'))data={primary:null,references:[]};
 else if(url.pathname.endsWith('/events'))return new Response(events.filter(e=>e.sequence>Number(url.searchParams.get('after')||0)).map(e=>`id: ${e.sequence}\nevent: ${e.type}\ndata: ${JSON.stringify(e.payload)}\n\n`).join(''),{headers:{'Content-Type':'text/event-stream'}});
 else if(url.pathname.endsWith('/diff'))data={available:true,files:[],cumulative_files:[]};
 else if(url.pathname.endsWith('/context'))data=[];
 else if(url.pathname.endsWith('/turns/turn'))data={id:'turn',conversation_id:row.id,status:'completed',created_at:row.created_at};
 else if(url.pathname.endsWith('/turns'))data={items:[{id:"turn",conversation_id:row.id,status:"completed",created_at:row.created_at}]};
 else if(url.pathname.endsWith('/messages'))data={items:[{id:"u",turn_id:"turn",role:"user",content:"检查项目并汇总结果",created_at:row.created_at},{id:"z",turn_id:"turn",role:"assistant",content:"已完成检查。\n\n| 项目 | 结果 |\n| --- | --- |\n| 文件检查 | 通过 |\n| 代码修改 | 无 |",created_at:row.created_at}]};
 else if(url.pathname.endsWith('/synthetic'))data=row;
 else data={items:[row],total:1,page:1,page_size:20};
 return new Response(JSON.stringify({code:0,data}),{headers:{'Content-Type':'application/json'}});
};
const candidate={id:"preview",object_id:"REQ-0099 · 本地验证需求",state:new URLSearchParams(location.search).get("state") || "pending",manifest_hash:"preview",revision:"1",files:[{path:"issues/requirements/plan/REQ-0099-local-check/requirement.md",diff:"+ # 本地验证需求\n+ 状态：draft\n+ 需求中心与 Chat 读取同一个项目"},{path:"issues/requirements/plan/REQ-0099-local-check/trace.md",diff:"- status: captured\n+ status: draft"},{path:"issues/requirements/_registry.yaml",diff:"- status: captured\n+ status: draft"},{path:"issues/requirements/CHANGELOG.md",diff:"+ REQ-0099 · 需求文档已生成"}]};
createRoot(document.getElementById('root')!).render(new URLSearchParams(location.search).get('page')==='requirements'?<RequirementCenterPage/>:<ChatWorkbenchPage skeletonCandidate={candidate}/>);
