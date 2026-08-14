import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { saveAdminSession } from "./pages/admin/adminAuth";

const sessionPayload = {
  data: {
    access_token: "test-token",
    expires_at: "2026-08-08 02:00:00",
    user: {
      id: "user_superadmin",
      username: "superadmin",
      role: "后台管理员",
      status: "正常",
      is_system_superadmin: true,
    },
  },
};

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/admin");
  vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000");
  vi.stubGlobal("scrollTo", vi.fn());
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
  window.localStorage.clear();
  window.history.replaceState(null, "", "/");
});

describe("admin authentication gate", () => {
  it("shows unified MoonBox login before protected admin routes", () => {
    render(<App />);

    expect(window.location.pathname).toBe("/login");
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(screen.queryByRole("form", { name: "管理后台登录" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "用户管理" })).toBeNull();
  });

  it("keeps legacy #admin-users entry compatible", () => {
    window.history.replaceState(null, "", "/#admin-users");

    render(<App />);

    expect(window.location.pathname).toBe("/login");
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(screen.queryByRole("form", { name: "管理后台登录" })).toBeNull();
  });

  it("uses the unified login form for admin authentication", () => {
    render(<App />);

    const password = screen.getByLabelText("密码") as HTMLInputElement;
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(password.type).toBe("password");
    expect(screen.getByRole("button", { name: "登录并开启宝盒" })).toBeTruthy();
  });

  it("logs in through the unified page and enters the requirement center", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => sessionPayload })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            issues: [],
            workspaces: [],
            current_user: { name: "superadmin", avatar_initial: "S", can_access_admin: true, permissions: ["requirement:read", "admin:access"] },
            selected_workspace_id: "",
            stats: { total: 0, requirements: 0, bugs: 0, blocked: 0, drift: 0 },
          },
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "superadmin" } });
    fireEvent.change(screen.getByLabelText("密码"), { target: { value: "example-test-password" } });
    fireEvent.click(screen.getByRole("button", { name: "登录并开启宝盒" }));

    await waitFor(() => expect(window.location.pathname).toBe("/requirements"));
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/auth/login",
      expect.objectContaining({ method: "POST" }),
    );
    expect(window.localStorage.getItem("moonbox.session")).toContain("test-token");
    expect(window.localStorage.getItem("moonbox.session")).toContain("superadmin");
  });

  it("lets frontend users enter the requirement center without creating an admin session", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          data: {
            access_token: "front-token",
            expires_at: "2026-08-08 02:00:00",
            user: {
              id: "user_front",
              username: "frontuser",
              role: "前台用户",
              status: "正常",
              is_system_superadmin: false,
            },
          },
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            issues: [],
            workspaces: [],
            current_user: { name: "frontuser", avatar_initial: "F", can_access_admin: false, permissions: ["requirement:read"] },
            selected_workspace_id: "",
            stats: { total: 0, requirements: 0, bugs: 0, blocked: 0, drift: 0 },
          },
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "frontuser" } });
    fireEvent.change(screen.getByLabelText("密码"), { target: { value: "Mb-FrontUser2026!" } });
    fireEvent.click(screen.getByRole("button", { name: "登录并开启宝盒" }));

    await waitFor(() => expect(window.location.pathname).toBe("/requirements"));
    expect(window.localStorage.getItem("moonbox.session")).toContain("front-token");
    fireEvent.click(screen.getByRole("button", { name: /frontuser/ }));
    expect(screen.queryByRole("menuitem", { name: "进入后台" })).toBeNull();
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "/api/v1/requirement-center/context",
      expect.objectContaining({
        headers: expect.objectContaining({ authorization: "Bearer front-token" }),
      }),
    );
  });

  it("uses the refreshed admin session when entering admin from the requirement center", async () => {
    window.history.replaceState(null, "", "/requirements");
    window.localStorage.setItem("moonbox.session", JSON.stringify({ username: "superadmin", started_at: "2026-08-11T00:00:00.000Z" }));
    window.localStorage.setItem("moonbox.session", JSON.stringify(sessionPayload.data));
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          data: {
            issues: [],
            workspaces: [{ organization_name: "MoonBox", workspace_id: "moonbox", name: "MoonBox", slug: "moonbox", description: "", timezone: "Asia/Shanghai", member_count: 1, role: "拥有者" }],
            current_user: { name: "superadmin", avatar_initial: "S", can_access_admin: true, permissions: ["requirement:read", "admin:access"] },
            selected_workspace_id: "moonbox",
            stats: { total: 0, requirements: 0, bugs: 0, blocked: 0, drift: 0 },
          },
        }),
      })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ data: { items: [], total: 0, page: 1, page_size: 10 } }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await waitFor(() => expect(screen.getByRole("button", { name: /superadmin/ })).toBeTruthy());

    saveAdminSession({ ...sessionPayload.data, user: { ...sessionPayload.data.user, nickname: "前台已更新" } });
    fireEvent.click(screen.getByRole("button", { name: /superadmin/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: "进入后台" }));

    await waitFor(() => expect(window.location.pathname).toBe("/admin"));
    expect(screen.getByRole("button", { name: /前台已更新/ })).toBeTruthy();
  });

  it("shows backend login failure detail", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: "账号不可用或无后台权限。" }),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "linyu" } });
    fireEvent.change(screen.getByLabelText("密码"), { target: { value: "Mb-ResetOnceOnly2026" } });
    fireEvent.click(screen.getByRole("button", { name: "登录并开启宝盒" }));

    expect(await screen.findByText("账号不可用或无后台权限。")).toBeTruthy();
  });

  it("changes password from the admin user menu and clears the session", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => ({ data: { items: [], total: 0, page: 1, page_size: 10 } }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ data: { status: "done", message: "密码已更新，请重新登录。" } }) });
    vi.stubGlobal("fetch", fetchMock);
    window.localStorage.setItem("moonbox.session", JSON.stringify(sessionPayload.data));

    render(<App />);

    await waitFor(() => expect(screen.getByRole("heading", { name: "用户管理" })).toBeTruthy());
    fireEvent.click(screen.getByRole("button", { name: /superadmin/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: /修改密码/ }));

    expect(screen.getByRole("form", { name: "修改密码" })).toBeTruthy();
    const submit = screen.getByRole("button", { name: "更新密码" });
    expect(submit).toHaveProperty("disabled", true);

    fireEvent.change(screen.getByLabelText("当前密码"), { target: { value: "example-test-password" } });
    fireEvent.change(screen.getByLabelText("新密码"), { target: { value: "Mb-NewSecure2026!" } });
    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "Mb-NewSecure2026?" } });
    expect(screen.getByLabelText("当前密码")).toHaveProperty("type", "password");
    fireEvent.click(screen.getByRole("button", { name: "显示当前密码" }));
    expect(screen.getByLabelText("当前密码")).toHaveProperty("type", "text");
    fireEvent.click(screen.getByRole("button", { name: "隐藏当前密码" }));
    expect(screen.getByLabelText("当前密码")).toHaveProperty("type", "password");
    fireEvent.click(screen.getByRole("button", { name: "显示新密码" }));
    fireEvent.click(screen.getByRole("button", { name: "显示确认新密码" }));
    expect(screen.getByLabelText("新密码")).toHaveProperty("type", "text");
    expect(screen.getByLabelText("确认新密码")).toHaveProperty("type", "text");
    fireEvent.click(submit);
    expect(await screen.findByText("两次输入的新密码不一致。")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("确认新密码"), { target: { value: "Mb-NewSecure2026!" } });
    fireEvent.click(screen.getByRole("button", { name: "更新密码" }));

    await waitFor(() => expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy());
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/auth/change-password",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({ authorization: "Bearer test-token" }),
      }),
    );
    expect(JSON.parse(fetchMock.mock.calls[1][1]?.body as string)).toEqual({
      current_password: "example-test-password",
      new_password: "Mb-NewSecure2026!",
      confirm_password: "Mb-NewSecure2026!",
    });
  });
});
