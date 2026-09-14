import { RequirementCenterPage } from "./pages/catalog/RequirementCenterPage";
import { fireEvent, render, screen, waitFor, cleanup } from "@testing-library/react";
import { beforeEach, afterEach, describe, it, expect, vi } from "vitest";
import { GovernanceResult, type GovernanceCandidate } from "./components/chat/GovernanceResult";
import { scopedUrl } from "./components/workbench/governanceApi";
const candidate: GovernanceCandidate = { id: "candidate", object_id: "REQ-9098-validation", state: "pending", revision: 1, manifest_hash: "a".repeat(64), files: [{path:"issues/requirements/plan/REQ-9098-validation/requirement.md",diff:"- captured\n+ draft"}] };
beforeEach(() => {
  sessionStorage.clear();
  HTMLDialogElement.prototype.showModal = function() { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function() { this.removeAttribute("open"); };
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
describe("受控治理成果", () => {
  it("打开完整差异不申请应用，明确维护确认后使用固定版本", async () => {
    const fetch=vi.fn(async () => ({ok:true,json:async()=>({data:{id:"operation",state:"applied"}})}));vi.stubGlobal("fetch",fetch);
    render(<GovernanceResult candidate={candidate}/>);
    fireEvent.click(screen.getByTestId("governance-result-preview"));
    expect(screen.getByText(/- captured/)).toBeTruthy();expect(fetch).not.toHaveBeenCalled();
    expect((screen.getByTestId("governance-apply-confirm") as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(screen.getByTestId("governance-maintenance-confirm"));fireEvent.click(screen.getByTestId("governance-apply-confirm"));
    await waitFor(()=>expect(screen.getByTestId("governance-application-state").textContent).toBe("已应用"));
    const first=fetch.mock.calls[0] as unknown as [string,RequestInit];
    expect(JSON.parse(first[1].body as string)).toMatchObject({expected_manifest_hash:candidate.manifest_hash,candidate_revision:1,maintenance_confirmed:true});
    expect((screen.getByTestId("governance-apply-confirm") as HTMLButtonElement).disabled).toBe(true);
  });
  it.each(["conflict","recovery_blocked","failed"])("刷新后恢复 %s 状态且不重新申请",async state=>{
    sessionStorage.setItem("moonbox.governance.operation:candidate","existing");
    const fetch=vi.fn(async()=>({ok:true,json:async()=>({data:{id:"existing",state}})}));vi.stubGlobal("fetch",fetch);
    render(<GovernanceResult candidate={candidate}/>);fireEvent.click(screen.getByTestId("governance-result-preview"));
    await waitFor(()=>expect((screen.getByTestId("governance-apply-confirm") as HTMLButtonElement).disabled).toBe(true));
    await waitFor(()=>expect(fetch).toHaveBeenCalled());
    expect(fetch.mock.calls.every(call=>!(call as unknown as [string,RequestInit])[1]?.method)).toBe(true);
  });
  it("任务后缀位于查询参数之前且不接受跨站文档地址",()=>{
    const scope={space_id:"s",repository_id:"r",readonly:false,status:"connected" as const};
    expect(scopedUrl("/api/v1/requirement-center/changes/a/documents/tasks.md?space_id=old",scope,"/tasks")).toBe("/api/v1/requirement-center/changes/a/documents/tasks.md/tasks?space_id=s&repository_id=r");
    expect(()=>scopedUrl("https://elsewhere.invalid/doc",scope)).toThrow();
  });
});

it("刷新发现新版本保留编辑草稿并暂停旧基准保存", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({access_token:"test",username:"tester"}));
  let revision="one";
  const documentUrl="/api/v1/requirement-center/issues/REQ-0099-validation/documents/capture.md";
  const context={current_user:{name:"tester"},workspaces:[{workspace_id:"space",name:"验证空间"}],selected_workspace_id:"space",stats:{total:1,requirements:1,bugs:0,blocked:0,drift:0},issues:[{id:"REQ-0099",type:"requirement",title:"草稿保护",stage:"capture",priority:"P2",owner:"产品",documents:["capture.md","trace.md"],document_entries:[{name:"capture.md",type:"markdown",editable:true,url:documentUrl}],updated_at:"now"}]};
  const fetch=vi.fn(async(input: RequestInfo | URL,init?:RequestInit)=>{
    const url=String(input);
    if(url.endsWith("/projects"))return {ok:true,json:async()=>({data:{...context,projects:[{space_id:"space",repository_id:"repo",status:"connected",readonly:false}]}})};
    if(url.includes("/context"))return {ok:true,json:async()=>({data:{...context,snapshot_revision:revision}})};
    if(init?.method==="PUT")return {ok:false,status:409,json:async()=>({detail:"文档版本冲突，草稿已保留"})};
    return {ok:true,json:async()=>({data:{content:revision==="one"?"# 初始文档":"# 外部新版本",version:(revision==="one"?"a":"b").repeat(64)}})};
  });vi.stubGlobal("fetch",fetch);
  render(<RequirementCenterPage/>);await screen.findByText("REQ-0099");
  expect(screen.queryByTestId("project-binding")).toBeNull();
  fireEvent.click(screen.getByRole("button", {name:"刷新需求中心"}));
  await waitFor(() => expect(fetch.mock.calls.filter(([input]) => String(input).includes("/context")).length).toBeGreaterThan(1));
  fireEvent.click(screen.getByRole("button",{name:/capture.md/}));await screen.findByRole("heading",{name:"初始文档"});
  fireEvent.click(screen.getByRole("button",{name:"编辑"}));fireEvent.change(screen.getByLabelText("编辑 capture.md"),{target:{value:"# 我的草稿"}});
  revision="two";fireEvent(window,new Event("focus"));
  await screen.findByText(/项目文档已有新版本/);
  expect((screen.getByLabelText("编辑 capture.md") as HTMLTextAreaElement).value).toBe("# 我的草稿");
  expect((screen.getAllByRole("button").find(button=>button.textContent?.trim()==="保存") as HTMLButtonElement).disabled).toBe(true);
  expect(fetch.mock.calls.some(([,init])=>init?.method==="PUT")).toBe(false);
  localStorage.clear();
});


it("同项目慢context合并焦点与可见刷新，卸载取消", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({access_token:"test",username:"tester"}));
  let signal: AbortSignal | undefined;
  const fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    if (String(input).endsWith("/projects")) return {ok:true,json:async()=>({data:{projects:[{space_id:"space",repository_id:"repo",status:"connected",readonly:false}],workspaces:[]}})};
    signal = init?.signal as AbortSignal;
    return new Promise(() => {});
  });
  vi.stubGlobal("fetch",fetch);
  const view = render(<RequirementCenterPage/>);
  await waitFor(()=>expect(signal).toBeTruthy());
  fireEvent(window,new Event("focus"));fireEvent(document,new Event("visibilitychange"));fireEvent(window,new Event("focus"));
  expect(fetch.mock.calls.filter(([input])=>String(input).includes("/context"))).toHaveLength(1);
  expect(signal?.aborted).toBe(false);
  view.unmount();expect(signal?.aborted).toBe(true);
  localStorage.clear();
});

it.each(["requirement", "bug"])("%s 启动0/N后从服务端刷新阶段", async (type) => {
  localStorage.setItem("moonbox.session", JSON.stringify({access_token:"test",username:"tester"}));
  let stage="ready-dev";let revision="before";
  vi.stubGlobal("fetch",vi.fn(async(input:RequestInfo|URL)=>({ok:true,json:async()=>({data:String(input).includes("/projects")?{projects:[{repository_id:"repo",workspace_id:"space",name:"验证项目"}],workspaces:[]}:{current_user:{name:"tester"},workspaces:[{workspace_id:"space",name:"验证空间"}],selected_workspace_id:"space",snapshot_revision:revision,stats:{total:1,requirements:1,bugs:0,blocked:0,drift:0},issues:[{id:"REQ-9091",type,title:"生命周期测试",stage,priority:"P2",owner:"产品",documents:[],tasks:{done:0,total:2},task_progress:[0,2],updated_at:"2026-09-12 00:00:00"}]}})})));
  const view=render(<RequirementCenterPage/>);await screen.findByText("生命周期测试");
  const card=()=>view.container.querySelector('[data-issue-id="REQ-9091"]')!;
  expect(card().closest('[data-stage]')?.getAttribute('data-stage')).toBe('ready-dev');
  stage="development";revision="started";fireEvent(window,new Event('focus'));
  await waitFor(()=>expect(card().closest('[data-stage]')?.getAttribute('data-stage')).toBe('development'));
  expect(card().textContent).toContain('0/2');expect(card().textContent).toContain('查看进度');
  stage="acceptance";revision="completed";fireEvent.click(screen.getByRole('button',{name:'刷新需求中心'}));
  await waitFor(()=>expect(card().closest('[data-stage]')?.getAttribute('data-stage')).toBe('acceptance'));
  localStorage.clear();
});
