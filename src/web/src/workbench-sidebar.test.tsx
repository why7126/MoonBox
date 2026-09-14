import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { WorkbenchSidebar } from "./components/workbench/WorkbenchSidebar";
import { useWorkbenchTheme } from "./components/workbench/useWorkbenchTheme";
import type { Workspace } from "./components/workbench/workbenchAccount";

const space: Workspace = { workspaceId: "s1", name: "验收空间", slug: "test", organizationName: "测试", description: "", timezone: "UTC", memberCount: 2, role: "拥有者" };
const readonlySpace = { ...space, workspaceId: "s2", name: "只读空间", readonly: true };
const onWorkspaceChange = vi.fn();
function Shell({ page = "chat", admin = false, readonly = false, busy = false }: { page?: "chat" | "requirements"; admin?: boolean; readonly?: boolean; busy?: boolean }) {
  const [theme] = useWorkbenchTheme();
  return <main className={`requirement-center theme-${theme}`} data-testid="shell" data-theme={theme}>
    <WorkbenchSidebar activePage={page} activeUser={{ name: "验收用户", avatarInitial: "验收", canAccessAdmin: admin, permissions: [] }} workspace={readonly ? readonlySpace : space} availableWorkspaces={[space, readonlySpace]} isLoadingContext={false} contextError="" onWorkspaceChange={onWorkspaceChange} onUserChange={vi.fn()} onRefresh={vi.fn()} spaceSwitchDisabled={busy} />
    <div data-testid="outside" onMouseDown={event => event.stopPropagation()}>正文</div>
  </main>;
}
beforeEach(() => { localStorage.clear(); onWorkspaceChange.mockClear(); vi.stubGlobal("matchMedia", vi.fn(() => ({ matches: false }))); });
afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });
const openMenu = () => fireEvent.click(screen.getByRole("button", { name: /用户菜单/ }));
it.each(["chat", "requirements"] as const)("%s retains account actions, correct route and collapsed menu access", page => {
  render(<Shell page={page} />);
  const navigation = screen.getByRole("navigation", { name: "前台导航" });
  expect(within(navigation).getAllByRole("button")).toHaveLength(8);
  expect(within(navigation).getByRole("button", { name: page === "chat" ? "Chat 工作台" : "需求中心" }).getAttribute("aria-current")).toBe("page");
  fireEvent.click(screen.getByRole("button", { name: "收起侧边栏" })); openMenu();
  expect(screen.getByRole("menuitem", { name: "个人资料" })).toBeTruthy();
  expect(screen.queryByRole("menuitem", { name: "进入后台" })).toBeNull();
  fireEvent.keyDown(document, { key: "Escape" });
  expect(screen.queryByRole("menu")).toBeNull();
  expect(document.activeElement).toBe(screen.getByRole("button", { name: /用户菜单/ }));
});
it("uses server permissions for admin and readonly space settings", () => {
  const view = render(<Shell admin />); openMenu();
  expect(screen.getByRole("menuitem", { name: "进入后台" })).toBeTruthy();
  expect(screen.getByRole("menuitem", { name: "设置空间" })).toBeTruthy();
  view.rerender(<Shell readonly />);
  expect(screen.queryByRole("menuitem", { name: "进入后台" })).toBeNull();
  expect(screen.queryByRole("menuitem", { name: "设置空间" })).toBeNull();
});
it("persists theme across page mounts and reacts to storage updates", () => {
  const view = render(<Shell />); openMenu();
  fireEvent.click(screen.getByRole("switch", { name: "切换明暗主题" }));
  expect(screen.getByTestId("shell").dataset.theme).toBe("light");
  view.unmount(); render(<Shell page="requirements" />);
  expect(screen.getByTestId("shell").dataset.theme).toBe("light");
  localStorage.setItem("moonbox.ui.preferences", JSON.stringify({ theme: "dark" }));
  fireEvent(window, new Event("storage"));
  expect(screen.getByTestId("shell").dataset.theme).toBe("dark");
});
it("closes outside even when page handlers stop propagation; inside stays open", () => {
  render(<Shell />); openMenu();
  fireEvent.mouseDown(screen.getByRole("group", { name: "账号" }));
  expect(screen.getByRole("menu")).toBeTruthy();
  fireEvent.mouseDown(screen.getByTestId("outside")); expect(screen.queryByRole("menu")).toBeNull();
});
it("switches only listed spaces and preserves readonly metadata", () => {
  render(<Shell />); openMenu(); fireEvent.click(screen.getByRole("menuitem", { name: /切换空间/ }));
  fireEvent.click(screen.getByTestId("space-option-s2"));
  expect(onWorkspaceChange).toHaveBeenCalledWith(readonlySpace);
  expect(JSON.parse(localStorage.getItem("moonbox.workspace") || "null").workspaceId).toBe("s2");
  expect(screen.queryByRole("menu")).toBeNull();
});
it("prevents space changes during a Chat mutation", () => {
  render(<Shell busy />); openMenu(); fireEvent.click(screen.getByRole("menuitem", { name: /切换空间/ }));
  fireEvent.click(screen.getByTestId("space-option-s2")); expect(onWorkspaceChange).not.toHaveBeenCalled();
});
it("opens and cancels the shared profile and create-space dialogs without writes", () => {
  const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
  render(<Shell />); openMenu(); fireEvent.click(screen.getByRole("menuitem", { name: "个人资料" }));
  expect(screen.getByRole("form", { name: "个人资料" })).toBeTruthy();
  fireEvent.keyDown(document, { key: "Escape" }); openMenu();
  fireEvent.click(screen.getByRole("menuitem", { name: /切换空间/ }));
  fireEvent.click(screen.getByTestId("space-create-or-join-entry"));
  expect(screen.getByRole("dialog", { name: "创建空间" })).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "取消" }));
  expect(screen.queryByRole("dialog")).toBeNull(); expect(fetch).not.toHaveBeenCalled();
});
