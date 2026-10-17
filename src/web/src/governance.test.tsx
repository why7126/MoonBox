import { RequirementCenterPage } from "./pages/catalog/RequirementCenterPage";
import { fireEvent, render, screen, waitFor, cleanup } from "@testing-library/react";
import { beforeEach, afterEach, describe, it, expect, vi } from "vitest";
import { GovernanceResult, activeGovernanceCandidate, type GovernanceCandidate } from "./components/chat/GovernanceResult";
import { governanceRequest, scopedUrl } from "./components/workbench/governanceApi";
const candidate: GovernanceCandidate = { id: "candidate", object_id: "REQ-9098-validation", state: "pending", revision: 1, manifest_hash: "a".repeat(64), files: [{path:"issues/requirements/plan/REQ-9098-validation/requirement.md",diff:"- captured\n+ draft"}] };
beforeEach(() => {
  sessionStorage.clear();
  HTMLDialogElement.prototype.showModal = function() { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function() { this.removeAttribute("open"); };
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
describe("受控治理成果", () => {
  it("评审拒绝显示具体原因且重验不恢复成果面板", () => {
    const notice=vi.fn(), applied=vi.fn();
    const view=render(<GovernanceResult candidate={{...candidate,state:"rejected",error_code:"review_outcome_conflict"}} onNotice={notice} onApplied={applied}/>);
    expect(notice).toHaveBeenCalledWith("评审成果未应用：评审文档 status 与 result 结论冲突。原成果已保留。");
    expect(applied).not.toHaveBeenCalled();
    expect(view.container.innerHTML).toBe("");
    view.rerender(<GovernanceResult candidate={{...candidate,state:"rejected",error_code:"review_acceptance_scope"}} onNotice={notice} onApplied={applied}/>);
    expect(notice).toHaveBeenCalledWith("评审成果未应用：验收文档存在超出评审范围的修改。原成果已保留。");
    expect(view.container.innerHTML).toBe("");
  });
  it("评审执行完成仍等待应用，只有事实源成功才通知同步完成", async () => {
    let resolve: (value: unknown) => void = () => {};
    const fetch=vi.fn(()=>new Promise(r=>{resolve=r;}));vi.stubGlobal("fetch",fetch);
    const notice=vi.fn(), applied=vi.fn();
    const view=render(<GovernanceResult candidate={{...candidate,action:"req-review",application:{id:"review-operation",state:"pending",phase:"queued"}}} onNotice={notice} onApplied={applied}/>);
    expect(applied).not.toHaveBeenCalled();
    expect(notice).toHaveBeenCalledWith("模型执行已结束，治理成果正在自动应用，尚未确认事实源同步完成。");
    expect(notice).not.toHaveBeenCalledWith("治理成果已写入事实源，文档和状态已同步。");
    resolve({ok:true,json:async()=>({data:{id:"review-operation",state:"applied",phase:"verified"}})});
    await waitFor(()=>expect(applied).toHaveBeenCalled());
    expect(notice).toHaveBeenCalledWith("治理成果已写入事实源，文档和状态已同步。");
    expect(view.container.innerHTML).toBe("");
  });
  it("零差异仅通知无需更新，历史旧失败不覆盖最新结果", async () => {
    const latest={...candidate,id:"latest",state:"unchanged",files:[]};
    const old={...candidate,id:"old",state:"rejected",error_code:"governance_validation_failed"};
    expect(activeGovernanceCandidate([latest,old])).toBe(latest);
    const fetch=vi.fn();vi.stubGlobal("fetch",fetch);
    const notice=vi.fn();
    const view=render(<GovernanceResult candidate={activeGovernanceCandidate([latest,old])} onNotice={notice}/>);
    await waitFor(()=>expect(notice).toHaveBeenCalledWith("已核验，事实源一致，无需更新。"));
    expect(notice).toHaveBeenCalledTimes(1);
    expect(fetch).not.toHaveBeenCalled();
    expect(view.container.innerHTML).toBe("");
  });
  it("治理请求网络失败时不裸露浏览器原生 NetworkError", async () => {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("NetworkError when attempting to fetch resource."); }));
    await expect(governanceRequest("/api/v1/requirement-center/projects")).rejects.toThrow("项目连接暂不可用，请稍后重试");
    localStorage.clear();
  });

  it("所有状态都不渲染 Chat 对话区治理成果面板", () => {
    render(<GovernanceResult candidate={{ id: "prepared", object_id: "BUG-0024-capture", state: "prepared", revision: 1, manifest_hash: "b".repeat(64), files: [] }} />);
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByTestId("governance-result-preview")).toBeNull();
    expect(screen.queryByText("待应用成果")).toBeNull();
    expect(screen.queryByText(/查看成果/)).toBeNull();
    expect(screen.queryByRole("dialog", { name: "审阅治理成果" })).toBeNull();
  });

  it("合格候选不由前端申请应用，只等待后端 controller", async () => {
    const fetch=vi.fn();vi.stubGlobal("fetch",fetch);
    const notice=vi.fn();
    render(<GovernanceResult candidate={candidate} onNotice={notice}/>);
    await waitFor(()=>expect(notice).toHaveBeenCalledWith("治理结果已交由后端自动应用，需求中心将随事实源刷新。"));
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByTestId("governance-result-preview")).toBeNull();
    expect(screen.queryByText("待应用成果")).toBeNull();
    expect(screen.queryByText(/查看成果/)).toBeNull();
    expect(screen.queryByRole("dialog", { name: "审阅治理成果" })).toBeNull();
    expect(screen.queryByTestId("governance-maintenance-confirm")).toBeNull();
    expect(screen.queryByTestId("governance-apply-confirm")).toBeNull();
  });
  it("刷新后轮询后端已创建的自动应用操作", async () => {
    const fetch=vi.fn(async () => ({ok:true,json:async()=>({data:{id:"operation",state:"applied",phase:"done"}})}));vi.stubGlobal("fetch",fetch);
    render(<GovernanceResult candidate={{...candidate,application:{id:"operation",state:"pending",phase:"queued"}}}/>);
    await waitFor(()=>expect(fetch).toHaveBeenCalledTimes(1));
    const calls = fetch.mock.calls as unknown as [string, RequestInit?][];
    expect(String(calls[0][0])).toContain("/api/v1/chat/governance-applications/operation");
    expect(calls[0][1]?.method).toBeUndefined();
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByTestId("governance-result-preview")).toBeNull();
    expect(screen.queryByText("待应用成果")).toBeNull();
    expect(screen.queryByText(/查看成果/)).toBeNull();
    expect(screen.queryByRole("dialog", { name: "审阅治理成果" })).toBeNull();
    expect(screen.queryByTestId("governance-maintenance-confirm")).toBeNull();
    expect(screen.queryByTestId("governance-apply-confirm")).toBeNull();
  });
  it("prepared 空候选不自动应用也不渲染面板", async () => {
    const fetch=vi.fn();vi.stubGlobal("fetch",fetch);
    render(<GovernanceResult candidate={{ id: "prepared", object_id: "BUG-0024-capture", state: "prepared", revision: 1, manifest_hash: "b".repeat(64), files: [] }}/>);
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(fetch).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByText("待应用成果")).toBeNull();
    expect(screen.queryByText(/查看成果/)).toBeNull();
  });
  it("后端应用失败后只发送轻量提示且不展示审阅面板", async () => {
    const fetch=vi.fn(async()=>({ok:true,json:async()=>({data:{id:"operation",state:"failed",phase:"apply",error_code:"external_change"}})}));
    vi.stubGlobal("fetch",fetch);
    const notice=vi.fn();
    render(<GovernanceResult candidate={{...candidate,application:{id:"operation",state:"pending",phase:"queued"}}} onNotice={notice}/>);
    await waitFor(()=>expect(notice).toHaveBeenCalledWith("治理结果应用失败，请查看轨迹后重试。"));
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByTestId("governance-result-preview")).toBeNull();
    expect(screen.queryByRole("dialog", { name: "审阅治理成果" })).toBeNull();
    expect((fetch.mock.calls as unknown as [string, RequestInit?][]).filter(([, init]) => init?.method === "POST")).toHaveLength(0);
  });
  it("状态同步失败只提示待恢复，不报告事实源完成", async () => {
    const fetch=vi.fn(async()=>({ok:true,json:async()=>({data:{id:"operation",state:"recovery_blocked",phase:"verification_failed",error_code:"workflow_sync_failed"}})}));
    vi.stubGlobal("fetch",fetch);
    const notice=vi.fn(), applied=vi.fn();
    render(<GovernanceResult candidate={{...candidate,application:{id:"operation",state:"pending",phase:"queued"}}} onNotice={notice} onApplied={applied}/>);
    await waitFor(()=>expect(notice).toHaveBeenCalledWith("文件已写入，状态同步失败，待恢复"));
    expect(applied).not.toHaveBeenCalled();
  });
  it.each(["conflict","recovery_blocked","failed"])("刷新后恢复 %s 状态且不重新申请",async state=>{
    sessionStorage.setItem("moonbox.governance.operation:candidate","existing");
    const fetch=vi.fn(async()=>({ok:true,json:async()=>({data:{id:"existing",state}})}));vi.stubGlobal("fetch",fetch);
    render(<GovernanceResult candidate={candidate}/>);
    expect(screen.queryByTestId("governance-apply-confirm")).toBeNull();
    expect(screen.queryByLabelText("治理成果")).toBeNull();
    expect(screen.queryByRole("dialog", { name: "审阅治理成果" })).toBeNull();
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
