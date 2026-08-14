import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { Homepage } from "./pages/home/Homepage";

const resetLocation = () => {
  window.history.replaceState(null, "", "/");
};

beforeEach(() => {
  resetLocation();
  vi.stubGlobal("scrollTo", vi.fn());
});

afterEach(() => {
  cleanup();
  resetLocation();
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Homepage", () => {
  it("renders the MoonBox homepage brand visual and content", () => {
    render(<Homepage />);

    expect(screen.getAllByAltText("MoonBox PM Harness")[0].getAttribute("src")).toBe(
      "/brand/moonbox/moonbox-nav-logo.png",
    );
    expect(screen.getByAltText("MoonBox 产品视觉").getAttribute("src")).toBe("/brand/moonbox/image.png");
    expect(screen.getByText("AI 原生软件工厂")).toBeTruthy();
    expect(screen.getByText("打开宝盒，拥有一家软件公司")).toBeTruthy();
    expect(screen.getByText("Agent 工作流")).toBeTruthy();
    expect(screen.getByText("产品知识库")).toBeTruthy();
    expect(screen.getByText("交付 Harness")).toBeTruthy();
  });

  it("opens the frontend login from both homepage CTAs", () => {
    render(<Homepage />);

    fireEvent.click(screen.getByRole("button", { name: "开启 MoonBox" }));

    expect(window.location.pathname).toBe("/login");
    expect(window.location.hash).toBe("");
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();

    resetLocation();
    cleanup();
    render(<Homepage />);
    fireEvent.click(screen.getByRole("button", { name: "打开第一个项目" }));

    expect(window.location.pathname).toBe("/login");
    expect(window.location.hash).toBe("");
    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(screen.queryByRole("form", { name: "管理后台登录" })).toBeNull();
  });

  it("supports direct /login entry and returning home", () => {
    window.history.replaceState(null, "", "/login");

    render(<Homepage />);

    expect(screen.getByRole("form", { name: "MoonBox login" })).toBeTruthy();
    expect(screen.getAllByAltText("MoonBox PM Harness")[1].getAttribute("src")).toBe(
      "/brand/moonbox/Logo1-20260728001940.png",
    );

    fireEvent.click(screen.getByRole("button", { name: /返回首页/ }));

    expect(window.location.pathname).toBe("/");
    expect(window.location.hash).toBe("");
    expect(screen.getByText("AI 原生软件工厂")).toBeTruthy();
  });

  it("toggles login password visibility without submitting or losing the value", () => {
    const requestAnimationFrameSpy = vi
      .spyOn(window, "requestAnimationFrame")
      .mockImplementation((callback: FrameRequestCallback) => {
        callback(0);
        return 0;
      });
    window.history.replaceState(null, "", "/login");

    render(<Homepage />);

    const password = screen.getByLabelText("密码") as HTMLInputElement;
    const form = screen.getByRole("form", { name: "MoonBox login" });
    const submitSpy = vi.fn((event: Event) => event.preventDefault());
    form.addEventListener("submit", submitSpy);

    fireEvent.change(password, { target: { value: "ExamplePass123!" } });

    const showButton = screen.getByRole("button", { name: "显示密码" });
    expect(showButton.getAttribute("type")).toBe("button");
    expect(showButton.getAttribute("aria-pressed")).toBe("false");
    expect(password.type).toBe("password");

    fireEvent.click(showButton);

    expect(submitSpy).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "隐藏密码" }).getAttribute("aria-pressed")).toBe("true");
    expect(password.type).toBe("text");
    expect(password.value).toBe("ExamplePass123!");
    expect(document.activeElement).toBe(password);

    fireEvent.click(screen.getByRole("button", { name: "隐藏密码" }));

    expect(submitSpy).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "显示密码" }).getAttribute("aria-pressed")).toBe("false");
    expect(password.type).toBe("password");
    expect(password.value).toBe("ExamplePass123!");
    expect(requestAnimationFrameSpy).toHaveBeenCalled();
  });

  it("opens the frontend requirement center after unified login submit", async () => {
    const fetchSpy = vi.spyOn(window, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        data: {
          access_token: "test-token",
          expires_at: "2026-08-11 00:00:00",
          user: {
            id: "user_superadmin",
            username: "founder",
            role: "后台管理员",
            status: "正常",
            is_system_superadmin: true,
          },
        },
      }),
    } as Response);
    window.history.replaceState(null, "", "/login");

    render(<Homepage />);

    const username = screen.getByLabelText("用户名") as HTMLInputElement;
    const password = screen.getByLabelText("密码") as HTMLInputElement;
    const form = screen.getByRole("form", { name: "MoonBox login" });

    expect(username.required).toBe(true);
    expect(password.required).toBe(true);
    expect(password.type).toBe("password");

    fireEvent.change(username, { target: { value: "founder" } });
    fireEvent.change(password, { target: { value: "MoonBox123!" } });
    fireEvent.submit(form);

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith(expect.stringContaining("/api/v1/auth/login"), expect.objectContaining({ method: "POST" }));
      expect(window.location.pathname).toBe("/requirements");
      expect(window.location.hash).toBe("");
      expect(window.localStorage.getItem("moonbox.session")).toContain("founder");
      expect(window.localStorage.getItem("moonbox.session")).toContain("test-token");
    });
  });
});
