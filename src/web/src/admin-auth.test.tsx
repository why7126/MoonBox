import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

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
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
  window.localStorage.clear();
  window.history.replaceState(null, "", "/");
});

describe("admin authentication gate", () => {
  it("shows admin login before protected routes", () => {
    render(<App />);

    expect(screen.getByRole("form", { name: "管理后台登录" })).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "用户管理" })).toBeNull();
  });

  it("keeps legacy #admin-users entry compatible", () => {
    window.history.replaceState(null, "", "/#admin-users");

    render(<App />);

    expect(screen.getByRole("form", { name: "管理后台登录" })).toBeTruthy();
  });

  it("toggles password visibility in the admin login form", () => {
    render(<App />);

    const password = screen.getByLabelText("密码") as HTMLInputElement;
    expect(password.type).toBe("password");

    fireEvent.click(screen.getByRole("button", { name: "显示密码" }));
    expect(password.type).toBe("text");

    fireEvent.click(screen.getByRole("button", { name: "隐藏密码" }));
    expect(password.type).toBe("password");
  });

  it("logs in and logs out of the admin area", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => sessionPayload })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ data: { items: [], total: 0, page: 1, page_size: 10 } }) })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ data: { status: "done" } }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("用户名"), { target: { value: "superadmin" } });
    fireEvent.change(screen.getByLabelText("密码"), { target: { value: "example-test-password" } });
    fireEvent.click(screen.getByRole("button", { name: "登录管理后台" }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "用户管理" })).toBeTruthy());
    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      "http://localhost:8000/api/v1/admin/auth/login",
      expect.objectContaining({ method: "POST" }),
    );
    expect(window.localStorage.getItem("moonbox.admin.session")).toContain("test-token");

    fireEvent.click(screen.getByRole("button", { name: /superadmin/ }));
    fireEvent.click(screen.getByRole("menuitem", { name: /退出登录/ }));
    await waitFor(() => expect(screen.getByRole("form", { name: "管理后台登录" })).toBeTruthy());
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/admin/auth/logout",
      expect.objectContaining({ method: "POST" }),
    );
    expect(window.localStorage.getItem("moonbox.admin.session")).toBeNull();
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
    fireEvent.click(screen.getByRole("button", { name: "登录管理后台" }));

    expect(await screen.findByText("账号不可用或无后台权限。")).toBeTruthy();
  });
});
