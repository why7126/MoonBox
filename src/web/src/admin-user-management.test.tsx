import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
// @ts-expect-error Vitest runs this assertion in Node, while the web tsconfig intentionally omits Node globals.
import { readFileSync } from "node:fs";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { AdminUserManagementPage } from "./pages/admin/AdminUserManagementPage";

const users = [
  {
    id: "user_superadmin",
    username: "superadmin",
    nickname: "平台超级管理员",
    avatar_url: null,
    role: "后台管理员",
    status: "正常",
    status_before_freeze: null,
    workspace_count: 0,
    last_login_at: "2026-08-06 07:30:00",
    is_system_superadmin: true,
    session_invalidated_at: null,
    created_at: "2026-07-01 00:00:00",
    updated_at: "2026-08-06 07:30:00",
  },
  {
    id: "user_chenmo",
    username: "chenmo",
    nickname: "陈默",
    avatar_url: null,
    role: "后台管理员",
    status: "正常",
    status_before_freeze: null,
    workspace_count: 3,
    last_login_at: "2026-08-06 18:42:13",
    is_system_superadmin: false,
    session_invalidated_at: null,
    created_at: "2026-07-18 09:24:36",
    updated_at: "2026-08-06 18:42:13",
  },
  {
    id: "user_linyu",
    username: "linyu",
    nickname: "林宇",
    avatar_url: null,
    role: "前台用户",
    status: "已冻结",
    status_before_freeze: "待激活",
    workspace_count: 2,
    last_login_at: "2026-08-06 17:05:48",
    is_system_superadmin: false,
    session_invalidated_at: "2026-08-06 17:06:00",
    created_at: "2026-07-22 14:11:07",
    updated_at: "2026-08-06 17:06:00",
  },
  {
    id: "user_zhaoqi",
    username: "zhaoqi",
    nickname: "赵琪",
    avatar_url: null,
    role: "前台用户",
    status: "待激活",
    status_before_freeze: null,
    workspace_count: 1,
    last_login_at: null,
    is_system_superadmin: false,
    session_invalidated_at: null,
    created_at: "2026-08-05 11:08:22",
    updated_at: "2026-08-05 11:08:22",
  },
  {
    id: "user_deleted",
    username: "olduser",
    nickname: "旧用户",
    avatar_url: null,
    role: "前台用户",
    status: "已删除",
    status_before_freeze: null,
    workspace_count: 0,
    last_login_at: null,
    is_system_superadmin: false,
    session_invalidated_at: null,
    created_at: "2026-08-01 10:00:00",
    updated_at: "2026-08-08 10:00:00",
  },
] as const;

function setAdminSession() {
  window.localStorage.setItem("moonbox.admin.session", JSON.stringify({ access_token: "admin-token", expires_at: "2026-08-08 23:59:59", user: { id: "admin", username: "admin", role: "后台管理员", status: "正常", is_system_superadmin: true } }));
}

function jsonResponse(data: unknown, ok = true) {
  return {
    ok,
    json: async () => data,
  } as Response;
}

function mockUserApi(overrides: Partial<Record<string, Response>> = {}) {
  return vi.spyOn(window, "fetch").mockImplementation(async (input, init) => {
    const url = String(input);
    const method = init?.method || "GET";
    const override = overrides[`${method} ${url}`] || overrides[url];
    if (override) return override;
    if (url.includes("/api/v1/admin/users/avatar/avatar.png")) {
      return { ok: true, blob: async () => new Blob(["avatar"], { type: "image/png" }) } as Response;
    }
    if (url.includes("/api/v1/admin/users/avatar") && method === "POST") {
      return jsonResponse({ data: { url: "/api/v1/admin/users/avatar/avatar.png", status: "done" } });
    }
    if (url.includes("/api/v1/admin/users") && method === "GET") {
      const params = new URL(url, window.location.origin).searchParams;
      const role = params.get("role");
      const status = params.get("status");
      const q = params.get("q")?.toLowerCase();
      const pageSize = Number(params.get("page_size") || "10");
      const page = Number(params.get("page") || "1");
      const filtered = users.filter((user) => {
        const matchesRole = !role || user.role === role;
        const matchesStatus = status ? user.status === status : user.status !== "已删除";
        const matchesQuery = !q || user.username.includes(q) || (user.nickname || "").toLowerCase().includes(q);
        return matchesRole && matchesStatus && matchesQuery;
      });
      return jsonResponse({ data: { items: filtered.slice((page - 1) * pageSize, page * pageSize), total: filtered.length, page, page_size: pageSize } });
    }
    if (url.includes("/api/v1/admin/users") && method === "POST") {
      if (url.includes("/reset-password")) {
        return jsonResponse({ data: { temporary_password: "Mb-ResetOnceOnly2026", message: "临时密码仅展示一次。" } });
      }
      return jsonResponse({ data: { user: { ...users[1], username: "liyue", nickname: "李玥", id: "user_liyue", status: "待激活", status_before_freeze: null }, temporary_password: "Mb-TestOnceOnly2026", message: "临时密码仅展示一次。" } });
    }
    if (url.includes("/api/v1/admin/users") && (method === "PUT" || method === "DELETE")) {
      return jsonResponse({ data: users[1] });
    }
    return jsonResponse({ data: users[1] });
  });
}

beforeEach(() => {
  setAdminSession();
  mockUserApi();
});

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  vi.restoreAllMocks();
});

describe("AdminUserManagementPage", () => {
  const navIconMarkup = (buttonName: string) => {
    const button = screen.getByRole("button", { name: buttonName });
    return button.querySelector("svg")?.innerHTML ?? "";
  };

  it("renders protected superadmin and user list controls", async () => {
    render(<AdminUserManagementPage />);

    expect(screen.getByRole("heading", { name: "用户管理" })).toBeTruthy();
    expect((screen.getByAltText("MoonBox 产品图标") as HTMLImageElement).getAttribute("src")).toBe("/brand/moonbox/moonbox-app-icon-256.png");
    expect(screen.getByRole("button", { name: "收起侧边栏" })).toBeTruthy();
    expect(screen.getByRole("button", { name: /admin/i })).toBeTruthy();
    expect(await screen.findByText("superadmin")).toBeTruthy();
    expect(screen.getByText("系统内置")).toBeTruthy();
    expect(screen.getByText("不可操作")).toBeTruthy();
    expect(screen.getByLabelText("用户列表分页")).toBeTruthy();
    expect(screen.getByLabelText("搜索用户")).toBeTruthy();
    expect(screen.getByLabelText("角色筛选")).toBeTruthy();
    expect(screen.getByLabelText("状态筛选")).toBeTruthy();
    expect(Array.from(screen.getByLabelText("状态筛选").querySelectorAll("option")).map((item) => item.textContent)).toEqual(["全部状态", "待激活", "正常", "已冻结"]);
    expect(screen.queryByText("输入或筛选后自动查询")).toBeNull();
    expect(screen.getByText("统一管理平台用户、角色生命周期")).toBeTruthy();
    expect(screen.getByRole("button", { name: "新增用户" }).className).toContain("admin-btn admin-primary");
  });

  it("keeps prototype shell interactions for sidebar and user menu", () => {
    const { container } = render(<AdminUserManagementPage />);

    expect(container.querySelectorAll(".admin-sidebar nav .admin-ico").length).toBe(6);
    expect(navIconMarkup("首页")).not.toBe("");
    expect(navIconMarkup("空间管理")).not.toBe("");
    expect(navIconMarkup("用户管理")).not.toBe("");
    expect(navIconMarkup("首页")).not.toBe(navIconMarkup("空间管理"));
    expect(navIconMarkup("空间管理")).not.toBe(navIconMarkup("用户管理"));

    fireEvent.click(screen.getByRole("button", { name: "收起侧边栏" }));
    expect(screen.getByRole("button", { name: "展开侧边栏" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: /admin/i }));
    expect(screen.getByRole("menuitem", { name: /个人资料/ })).toBeTruthy();
    const themeSwitch = screen.getByRole("switch", { name: "切换明暗主题" });
    expect(themeSwitch.textContent).toContain("界面主题");
    expect(themeSwitch.getAttribute("aria-checked")).toBe("false");
    fireEvent.click(themeSwitch);
    expect(themeSwitch.getAttribute("aria-checked")).toBe("true");
    expect(container.querySelector(".admin-shell.light")).toBeTruthy();
    expect((container.querySelector(".admin-shell") as HTMLElement).getAttribute("data-theme")).toBe("light");
    expect(screen.getByRole("status").textContent).toContain("已切换为亮色主题");
    expect(container.querySelectorAll(".admin-user-menu .admin-menu-icon").length).toBe(4);
    expect(container.querySelectorAll(".admin-user-menu > button").length).toBe(4);
    expect(container.querySelector(".admin-theme-row .admin-theme-switch")).toBeTruthy();
    expect(container.querySelector(".admin-theme-row button")).toBeNull();
  });

  it("matches prototype user table columns, pagination and operation density", async () => {
    const { container } = render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");

    const headers = Array.from(container.querySelectorAll(".admin-account-table th")).map((item) => item.textContent);
    expect(headers).toEqual(["用户", "空间数", "角色", "状态", "冻结前状态", "最近登录时间", "创建时间", "操作"]);
    const firstRowCells = Array.from(container.querySelectorAll(".admin-account-table tbody tr:first-child td"));
    expect(firstRowCells.map((item) => item.textContent)).toEqual(["平台superadmin系统内置平台超级管理员", "0", "后台管理员", "正常", "—", "2026-08-06 07:30:00", "2026-07-01 00:00:00", "不可操作"]);
    expect(firstRowCells[0]?.querySelector("strong")?.textContent).toBe("superadmin");
    expect(firstRowCells[0]?.querySelector(".admin-user-name-line")?.textContent).toBe("superadmin系统内置");
    expect(container.querySelector(".admin-col-login")).toBeTruthy();
    expect(container.querySelector(".admin-col-created")).toBeTruthy();
    expect(container.querySelectorAll(".admin-date-cell").length).toBeGreaterThan(0);
    expect(container.querySelector(".admin-operation-set")).toBeTruthy();
    expect(container.querySelector(".admin-pagination-total")?.textContent).toBe("共 4 个用户");
    expect(container.querySelector(".admin-pagination-actions")).toBeTruthy();
    expect(container.querySelector(".admin-page-size-label")?.textContent).toBe("每页显示");
    expect(Array.from(screen.getByLabelText("每页显示条数").querySelectorAll("option")).map((item) => item.textContent)).toEqual(["10 条", "20 条", "50 条", "100 条"]);
  });

  it("uses reusable CRUD list template slots for user management", async () => {
    const { container } = render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");

    expect(container.querySelector(".admin-page-head h1")?.textContent).toBe("用户管理");
    expect(container.querySelector(".admin-head-actions .admin-btn.admin-primary")?.textContent).toBe("新增用户");
    expect(container.querySelectorAll(".admin-filter-control")).toHaveLength(3);
    expect(container.querySelector(".admin-table-wrap .admin-account-table")).toBeTruthy();
    expect(container.querySelector(".admin-pagination .admin-pagination-total")?.textContent).toBe("共 4 个用户");
  });

  it("locks prototype table density and readable text rules", () => {
    const css = readFileSync("src/styles/globals.css", "utf8");

    expect(css).toContain("min-width: 1350px");
    expect(css).toContain("table-layout: fixed");
    expect(css).toContain(".admin-col-actions");
    expect(css).toContain(".admin-col-before-freeze");
    expect(css).toContain("width: 220px");
    expect(css).toContain(".admin-date-cell");
    expect(css).toContain("white-space: nowrap");
    expect(css).toContain(".admin-user-name-line");
    expect(css).toContain(".admin-user-cell strong");
    expect(css).toContain("font-size: var(--admin-text-body)");
    expect(css).toContain("font-size: var(--admin-text-md)");
    expect(css).toContain("opacity: 1");
  });

  it("uses admin typography tokens across shell, menus, table, modal and toast", () => {
    const css = readFileSync("src/styles/globals.css", "utf8");
    const adminShellBlock = css.match(/\.admin-shell\s*\{[^}]+\}/)?.[0] || "";
    const tableCellBlock = css.match(/\.admin-table th,\s*\.admin-table td\s*\{[^}]+\}/)?.[0] || "";
    const modalTitleBlock = css.match(/\.admin-user-modal h2,\s*\.admin-confirm-modal h2,\s*\.admin-password-modal h2\s*\{[^}]+\}/)?.[0] || "";
    const toastBlock = css.match(/\.admin-toast\s*\{[^}]+\}/)?.[0] || "";

    expect(adminShellBlock).toContain("--admin-font-body: \"Noto Sans SC\", system-ui, sans-serif");
    expect(adminShellBlock).toContain("--admin-font-heading: \"Noto Serif SC\", serif");
    expect(adminShellBlock).toContain("--admin-font-accent: \"EB Garamond\", serif");
    expect(adminShellBlock).toContain("--admin-text-body: 13px");
    expect(adminShellBlock).toContain("font-family: var(--admin-font-body)");
    expect(tableCellBlock).toContain("font-size: var(--admin-text-body)");
    expect(tableCellBlock).toContain("font-weight: var(--admin-weight-regular)");
    expect(modalTitleBlock).toContain("font-family: var(--admin-font-heading)");
    expect(modalTitleBlock).toContain("font-size: var(--admin-text-title)");
    expect(toastBlock).toContain("font-family: var(--admin-font-body)");
    expect(toastBlock).toContain("font-size: var(--admin-text-body)");
    expect(css).toContain(".admin-sidebar button");
    expect(css).toContain(".admin-user-menu > button");
    expect(css).toContain(".admin-form-hint");
    expect(css).toContain(".admin-form-error");
  });

  it("uses prototype theme variables for primary admin button colors", () => {
    const css = readFileSync("src/styles/globals.css", "utf8");
    const primaryBlock = css.match(/\.admin-primary,\s*\.admin-content \.admin-primary,\s*\.admin-user-modal \.admin-primary,\s*\.admin-confirm-modal \.admin-primary,\s*\.admin-password-modal \.admin-primary\s*\{[^}]+\}/)?.[0] || "";

    expect(css).toContain("--admin-gold: #CBA35C");
    expect(css).toContain("--admin-gold: #B8863E");
    expect(primaryBlock).toContain(".admin-content .admin-primary");
    expect(primaryBlock).toContain("border-color: var(--admin-gold)");
    expect(primaryBlock).toContain("background: var(--admin-gold)");
    expect(primaryBlock).toContain("color: var(--admin-primary-text)");
    expect(primaryBlock).not.toContain("#CBA35C");
    expect(primaryBlock).not.toContain("#080A16");
  });

  it("filters by role and status without window.confirm", async () => {
    const confirmSpy = vi.spyOn(window, "confirm");
    const fetchSpy = vi.mocked(window.fetch);
    render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");

    fireEvent.change(screen.getByLabelText("角色筛选"), { target: { value: "前台用户" } });
    fireEvent.change(screen.getByLabelText("状态筛选"), { target: { value: "已冻结" } });
    fireEvent.change(screen.getByLabelText("每页显示条数"), { target: { value: "50" } });

    expect(await screen.findByText("linyu")).toBeTruthy();
    await waitFor(() => expect(screen.queryByText("chenmo")).toBeNull());
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/users?"), expect.objectContaining({ method: "GET" })));
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("role=%E5%89%8D%E5%8F%B0%E7%94%A8%E6%88%B7"))).toBe(true);
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("status=%E5%B7%B2%E5%86%BB%E7%BB%93"))).toBe(true);
    expect(fetchSpy.mock.calls.some(([url]) => String(url).includes("page_size=50"))).toBe(true);
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it("hides deleted users by default and does not offer deleted status filtering", async () => {
    render(<AdminUserManagementPage />);

    await screen.findByText("superadmin");
    expect(screen.queryByText("olduser")).toBeNull();
    expect(screen.getByLabelText("用户列表分页").textContent).toContain("共 4 个用户");
    expect(Array.from(screen.getByLabelText("状态筛选").querySelectorAll("option")).map((item) => item.textContent)).not.toContain("已删除");
  });

  it("creates and edits users with avatar upload state machine", async () => {
    const createObjectUrlSpy = vi.fn(() => "blob:avatar-preview");
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectUrlSpy });
    const fetchSpy = vi.mocked(window.fetch);
    window.localStorage.setItem("moonbox.admin.session", JSON.stringify({ access_token: "admin-token", expires_at: "2026-08-08 23:59:59", user: { id: "admin", username: "admin", role: "后台管理员", status: "正常", is_system_superadmin: true } }));
    render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");

    fireEvent.click(screen.getByRole("button", { name: "新增用户" }));
    const dialog = screen.getByRole("form", { name: "新增用户" });
    expect(dialog.querySelectorAll(".admin-form-row label.required span")).toHaveLength(2);
    expect(dialog.querySelector(".admin-avatar-picker .admin-avatar.large")).toBeTruthy();
    expect(dialog.querySelector(".admin-drawer-actions")).toBeTruthy();
    expect(screen.getByText("系统唯一，4-32 位；仅允许字母、数字，且必须以字母开头。创建后不可修改。")).toBeTruthy();
    expect(screen.queryByText("用户名需以字母开头，且为 4-32 位字母或数字。")).toBeNull();
    expect(screen.getByText("支持 JPG、PNG，建议 1:1")).toBeTruthy();
    expect(Array.from(dialog.querySelector(".admin-avatar-copy")?.children || []).map((item) => item.tagName)).toEqual(["SMALL", "BUTTON"]);
    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "1bad" } });
    expect(screen.getByText("请输入 4-32 位字母或数字，且以字母开头。").className).toBe("admin-form-error");
    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "liyue" } });
    fireEvent.change(screen.getByLabelText("昵称"), { target: { value: "李玥" } });
    expect(screen.getByRole("button", { name: "上传或更换头像" }).textContent).toBe("上传");
    fireEvent.change(screen.getByLabelText("选择头像文件"), { target: { files: [new File(["avatar"], "avatar.png", { type: "image/png" })] } });
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/users/avatar"), expect.objectContaining({ method: "POST", headers: { authorization: "Bearer admin-token" } })));
    await waitFor(() => expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/users/avatar/avatar.png"), expect.objectContaining({ headers: { authorization: "Bearer admin-token" } })));
    expect(createObjectUrlSpy).toHaveBeenCalled();
    await waitFor(() => expect(screen.getByRole("button", { name: "上传或更换头像" }).textContent).toBe("更换"));
    expect((screen.getByAltText("头像预览") as HTMLImageElement).getAttribute("src")).toBe("blob:avatar-preview");
    fireEvent.submit(dialog);

    expect(await screen.findByRole("region", { name: "临时密码" })).toBeTruthy();
    expect(screen.getByText("用户创建成功")).toBeTruthy();
    expect(screen.getByText("Mb-TestOnceOnly2026")).toBeTruthy();
    expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining("/api/v1/admin/users"), expect.objectContaining({ method: "POST" }));
  });

  it("copies one-time temporary password from modal and clears it on close", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
    render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");

    fireEvent.click(screen.getByRole("button", { name: "新增用户" }));
    const dialog = screen.getByRole("form", { name: "新增用户" });
    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "liyue" } });
    fireEvent.submit(dialog);

    expect(await screen.findByRole("region", { name: "临时密码" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "复制" }));
    await waitFor(() => expect(writeText).toHaveBeenCalledWith("Mb-TestOnceOnly2026"));
    expect(screen.getByRole("button", { name: "已复制" })).toBeTruthy();
    expect(screen.getByRole("status").textContent).toContain("临时密码已复制");

    expect(screen.getByText("关闭后将无法再次查看该密码，请确认已妥善保存。系统不会在前端持久化保存临时密码。")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "关闭" }));
    expect(screen.queryByText("Mb-TestOnceOnly2026")).toBeNull();
    expect(window.localStorage.getItem("Mb-TestOnceOnly2026")).toBeNull();
  });

  it("shows backend avatar upload error details", async () => {
    const fetchSpy = vi.mocked(window.fetch);
    window.localStorage.setItem("moonbox.admin.session", JSON.stringify({ access_token: "admin-token", expires_at: "2026-08-08 23:59:59", user: { id: "admin", username: "admin", role: "后台管理员", status: "正常", is_system_superadmin: true } }));
    render(<AdminUserManagementPage />);
    await screen.findByText("superadmin");
    fetchSpy.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "仅支持 JPG、PNG、WEBP 头像。" }),
    } as Response);

    fireEvent.click(screen.getByRole("button", { name: "新增用户" }));
    fireEvent.change(screen.getByLabelText("选择头像文件"), { target: { files: [new File(["avatar"], "avatar.gif", { type: "image/gif" })] } });

    await waitFor(() => expect(screen.getByText("仅支持 JPG、PNG、WEBP 头像。")).toBeTruthy());
    expect(screen.getByText("仅支持 JPG、PNG、WEBP 头像。").className).toBe("admin-form-error");
    expect(screen.getByText("支持 JPG、PNG，建议 1:1")).toBeTruthy();
  });

  it("locks prototype user modal sizing and label hierarchy", () => {
    const css = readFileSync("src/styles/globals.css", "utf8");

    expect(css).toContain("width: min(560px, calc(100vw - 40px))");
    expect(css).toContain("padding: 22px");
    expect(css).toContain("display: inline-flex");
    expect(css).toContain("content: \"*\"");
    expect(css).toContain(".admin-user-modal input");
    expect(css).toContain("height: 40px");
    expect(css).toContain(".admin-avatar-picker button");
    expect(css).toContain("height: 28px");
    expect(css).toContain(".admin-avatar-copy");
    expect(css).toContain("justify-items: start");
    expect(css).toContain("width: fit-content");
    expect(css).toContain("padding: 0 10px");
    expect(css).toContain(".admin-avatar-file");
    expect(css).toContain(".admin-user-modal footer button");
    expect(css).toContain(".admin-confirm-modal footer button");
    expect(css).toContain(".admin-password-modal footer button");
    expect(css).toContain("min-width: 72px");
    expect(css).toContain(".admin-form-error");
  });

  it("uses DS confirm modal for freeze and states 10 second invalidation", async () => {
    render(<AdminUserManagementPage />);

    const row = (await screen.findByText("chenmo")).closest("tr") as HTMLTableRowElement;
    fireEvent.click(row.querySelector("button:nth-of-type(3)") as HTMLButtonElement);

    expect(screen.getByRole("region", { name: "冻结用户" })).toBeTruthy();
    expect(screen.getByText(/10 秒内失效/)).toBeTruthy();
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "短" } });
    expect(screen.getByText("操作原因至少需要 4 个字。").className).toBe("admin-form-error");
    expect(screen.getByText("请填写至少 4 个字，便于审计追踪。")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "安全异常处理" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));

    await waitFor(() => expect(screen.getByRole("status").textContent).toContain("10 秒内会话失效"));
  });

  it("shows reset password result in copy modal instead of toast password text", async () => {
    render(<AdminUserManagementPage />);

    const row = (await screen.findByText("chenmo")).closest("tr") as HTMLTableRowElement;
    fireEvent.click(row.querySelector("button:nth-of-type(2)") as HTMLButtonElement);
    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "用户申请人工重置" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));

    expect(await screen.findByRole("region", { name: "临时密码" })).toBeTruthy();
    expect(screen.getByText("密码重置成功")).toBeTruthy();
    expect(screen.getByText("Mb-ResetOnceOnly2026")).toBeTruthy();
    expect(screen.getByText("该临时密码可用于后台管理员账号首次登录激活或正常登录；前台用户、已冻结或已删除账号无法登录后台。")).toBeTruthy();
    expect(screen.queryByRole("status")?.textContent || "").not.toContain("Mb-ResetOnceOnly2026");
  });

  it("shows frozen-before status and unfreeze restore target without layout-moving toast", async () => {
    render(<AdminUserManagementPage />);

    const row = (await screen.findByText("linyu")).closest("tr") as HTMLTableRowElement;
    expect(row.querySelector('[data-testid="admin-user-status-before-freeze"]')?.textContent).toBe("待激活");

    fireEvent.click(row.querySelector('[data-testid="admin-user-unfreeze-action"]') as HTMLButtonElement);

    expect(screen.getByTestId("admin-user-unfreeze-modal")).toBeTruthy();
    expect(screen.getByTestId("admin-user-unfreeze-restore-target").textContent).toContain("待激活");
    expect(screen.getByText("解冻后恢复为待激活，不会替用户完成首次激活。")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("操作原因"), { target: { value: "安全风险解除" } });
    fireEvent.click(screen.getByRole("button", { name: "确认" }));

    await waitFor(() => expect(screen.getByRole("status").textContent).toContain("恢复为待激活"));
  });
});
