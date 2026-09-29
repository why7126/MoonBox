import { useChatWorkbench } from "./components/chat/useChatWorkbench";
import { act, renderHook, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ChatWorkbenchPage } from "./pages/catalog/ChatWorkbenchPage";
import { ChatDialog } from "./components/chat/ChatDialog";
const seed = { id: "conversation", space_id: "space", repository_id: "repo", title: "会话一", archived: false, pinned: false, active_turn_id: null, created_at: "2026-09-08T00:00:00Z", updated_at: "2026-09-08T00:00:00Z" };
let rows = [seed], rejectRename = false;
beforeEach(() => {
  window.history.replaceState(null, "", "/chat");
  rows = [{ ...seed }]; rejectRename = false;
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  vi.stubGlobal("matchMedia", vi.fn(() => ({ matches: true })));
  vi.stubGlobal("fetch", vi.fn(async (url: string, options: RequestInit = {}) => {
    const path = new URL(url, "http://localhost");
    let data: unknown = null, status = 200;
    if (path.pathname.endsWith("/spaces")) data = [{ id: "space", name: "测试空间" }];
    else if (path.pathname.endsWith("/capabilities")) data = { execution_ready: false, reason: "执行尚未就绪", repositories: [{ id: "repo", space_id: "space" }] };
    else if (path.pathname === "/api/v1/chat/conversations/conversation" && !options.method) data = rows[0];
    else if (options.method === "PATCH") {
      if (rejectRename) status = 409;
      else { rows[0] = { ...rows[0], ...JSON.parse(String(options.body)) }; data = rows[0]; }
    } else if (options.method === "POST") { rows.push({ ...seed, id: "new", title: "新会话" }); data = rows[1]; }
    else if (options.method === "DELETE") rows = [];
    else if ((path.pathname.endsWith("/turns") || path.pathname.endsWith("/messages"))) data = { items: [] };
    else { const items = rows.filter(r => String(r.archived) === path.searchParams.get("archived") && r.title.includes(path.searchParams.get("q") || "")); data = { items, total: items.length, page: 1, page_size: 20 }; }
    return { ok: status === 200, status, json: async () => ({ code: status === 200 ? 0 : 2504, data, message: "保存失败，请重试" }) };
  }));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });
it("opens an editable local draft without a modal or creation request", async () => {
  render(<ChatWorkbenchPage />);
  await waitFor(() => expect((screen.getByTestId("chat-new-session") as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByTestId("chat-new-session"));
  expect(screen.queryByTestId("chat-new-dialog")).toBeNull();
  expect((screen.getByTestId("chat-prompt") as HTMLTextAreaElement).disabled).toBe(false);
  expect(vi.mocked(fetch).mock.calls.some(([, opts]) => opts?.method === "POST")).toBe(false);
  expect((screen.getByTestId("chat-send") as HTMLButtonElement).disabled).toBe(true);
  const calls = vi.mocked(fetch).mock.calls;
  expect(calls.some(([url, opts]) => String(url).endsWith("/turns") && opts?.method === "POST")).toBe(false);
  expect(calls.every(([, opts]) => new Headers(opts?.headers).get("Authorization") === "Bearer synthetic-test-token")).toBe(true);
});
it("keeps the rename draft on server failure and permits retry", async () => {
  render(<ChatWorkbenchPage />);
  await waitFor(() => expect((screen.getByTestId("chat-history-trigger") as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByTestId("chat-history-trigger"));
  fireEvent.click(await screen.findByTestId("chat-rename-trigger"));
  fireEvent.change(screen.getByLabelText("会话标题"), { target: { value: "修改后的标题" } });
  rejectRename = true; fireEvent.click(screen.getByTestId("chat-modal-submit"));
  await waitFor(() => expect((screen.getByTestId("chat-modal-submit") as HTMLButtonElement).disabled).toBe(false));
  expect((screen.getByLabelText("会话标题") as HTMLInputElement).value).toBe("修改后的标题");
  rejectRename = false; fireEvent.click(screen.getByTestId("chat-modal-submit"));
  await waitFor(() => expect(screen.queryByTestId("chat-rename-dialog")).toBeNull());
  expect(rows[0].title).toBe("修改后的标题");
});
it("archives and restores through the history filter", async () => {
  render(<ChatWorkbenchPage />);
  await waitFor(() => expect((screen.getByTestId("chat-history-trigger") as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByTestId("chat-history-trigger"));
  fireEvent.click(await screen.findByTestId("chat-archive"));
  await waitFor(() => expect(rows[0].archived).toBe(true));
  fireEvent.change(screen.getByLabelText("历史状态"), { target: { value: "true" } });
  fireEvent.click(await screen.findByTestId("chat-restore"));
  await waitFor(() => expect(rows[0].archived).toBe(false));
});
it("closes on outside capture even when bubbling is stopped", () => {
  const close = vi.fn();
  render(<><button onPointerDown={e => e.stopPropagation()}>外部</button><ChatDialog title="测试" testId="test-dialog" onClose={close} busy={false} footer={null}><button>内部</button></ChatDialog></>);
  fireEvent.pointerDown(screen.getByText("内部")); expect(close).not.toHaveBeenCalled();
  fireEvent.pointerDown(screen.getByText("外部")); expect(close).toHaveBeenCalledOnce();
});

it("restores a bookmarked conversation only after authorized API lookup", async () => {
  window.history.replaceState(null, "", "/chat?space_id=space&conversation_id=conversation");
  render(<ChatWorkbenchPage />);
  await waitFor(() => expect(screen.getByTestId("chat-title-edit").textContent).toContain("会话一"));
  expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url) === "/api/v1/chat/conversations/conversation")).toBe(true);
});

it("releases the composer when the server confirms no active turn", async () => {
  const { result } = renderHook(() => useChatWorkbench());
  await waitFor(() => expect(result.current.space).toBe("space"));
  act(() => result.current.setSelected({ ...seed, active_turn_id: "running-turn" }));
  await waitFor(() => expect(result.current.selected?.active_turn_id).toBeNull(), { timeout: 3000 });
});
it('keeps drafts and repository capabilities scoped to each space',async()=>{
 const original=vi.mocked(fetch).getMockImplementation()!;
 vi.stubGlobal('fetch',vi.fn(async(input,options)=>{
  const url=new URL(String(input),'http://localhost');let data;
  if(url.pathname.endsWith('/requirement-center/projects'))data={currentUser:{name:'测试',avatarInitial:'测',canAccessAdmin:false,permissions:[]},workspaces:[{workspaceId:'space',name:'空间A',role:'成员',memberCount:1},{workspaceId:'space-b',name:'空间B',role:'成员',memberCount:1}],selectedWorkspaceId:'space'};
  else if(url.pathname.endsWith('/spaces'))data=[{id:'space',name:'空间A'},{id:'space-b',name:'空间B'}];
  else if(url.pathname.endsWith('/capabilities')){const id=url.searchParams.get('space_id');data={execution_ready:true,reason:'',repositories:[{id:id==='space'?'repo-a':'repo-b',space_id:id}]};}
  else return original(input,options);
  return new Response(JSON.stringify({code:0,data}));
 }));
 render(<ChatWorkbenchPage/>);
 await waitFor(()=>expect(screen.getByTestId('chat-composer').getAttribute('data-repository')).toBe('repo-a'));
 expect(screen.queryByLabelText('会话仓库')).toBeNull();
 fireEvent.change(screen.getByTestId('chat-prompt'),{target:{value:'A的草稿'}});
 fireEvent.click(screen.getByRole('button',{name:/用户菜单/}));
 fireEvent.click(screen.getByRole('menuitem',{name:/切换空间/}));
 fireEvent.click(await screen.findByTestId('space-option-space-b'));
 await waitFor(()=>expect(screen.getByTestId('chat-composer').getAttribute('data-repository')).toBe('repo-b'));
 expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).value).toBe('');
 fireEvent.click(screen.getByRole('button',{name:/用户菜单/}));
 fireEvent.click(screen.getByRole('menuitem',{name:/切换空间/}));
 fireEvent.click(await screen.findByTestId('space-option-space'));
 await waitFor(()=>expect(screen.getByTestId('chat-composer').getAttribute('data-repository')).toBe('repo-a'));
 expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).value).toBe('A的草稿');
 expect(vi.mocked(fetch).mock.calls.some(([,opts])=>opts?.method==='POST')).toBe(false);
});
it('edits the selected title and switches sessions only through history',async()=>{
 window.history.replaceState(null,'','/chat?space_id=space&conversation_id=conversation');
 render(<ChatWorkbenchPage/>);
 await waitFor(()=>expect((screen.getByTestId('chat-title-edit') as HTMLButtonElement).disabled).toBe(false));
 expect(screen.queryByTestId('chat-session-picker')).toBeNull();expect(screen.queryByText('个人会话')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-title-edit'));
 expect(screen.getByTestId('chat-rename-dialog')).toBeTruthy();
 fireEvent.change(screen.getByLabelText('会话标题'),{target:{value:'   '}});
 expect((screen.getByTestId('chat-modal-submit') as HTMLButtonElement).disabled).toBe(true);
 fireEvent.change(screen.getByLabelText('会话标题'),{target:{value:'编辑后的名称'}});
 fireEvent.click(screen.getByTestId('chat-modal-submit'));
 await waitFor(()=>expect(screen.getByTestId('chat-title-edit').textContent).toContain('编辑后的名称'));
 fireEvent.click(screen.getByTestId('chat-history-trigger'));
 expect(await screen.findByText('会话仅本人可查看，同时遵循空间、仓库与关联对象权限。')).toBeTruthy();
 expect(await screen.findByText('编辑后的名称')).toBeTruthy();
 await waitFor(()=>expect(document.querySelector('.chat-history-row')).not.toBeNull());
 expect(document.querySelector('.chat-history-group')).not.toBeNull();
 expect(screen.getAllByText('编辑后的名称').some(node => !!node.closest('.chat-history-row'))).toBe(true);
});
it('does not create a conversation just to rename an unsent draft',async()=>{
 render(<ChatWorkbenchPage/>);
 expect((screen.getByTestId('chat-title-edit') as HTMLButtonElement).disabled).toBe(true);
 expect(screen.getByTestId('chat-title-edit').textContent).toContain('新会话');
 fireEvent.click(screen.getByTestId('chat-title-edit'));
 expect(screen.queryByTestId('chat-rename-dialog')).toBeNull();
 expect(vi.mocked(fetch).mock.calls.some(([,opts])=>opts?.method==='POST')).toBe(false);
});
