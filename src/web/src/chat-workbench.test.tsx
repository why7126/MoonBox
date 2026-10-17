import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ChatStatus, type ChatAvailability } from "./components/chat/ChatStatus";
import { ChatWorkbenchPage } from "./pages/catalog/ChatWorkbenchPage";

beforeEach(() => {
  vi.stubGlobal("scrollTo", vi.fn());
  vi.stubGlobal("matchMedia", vi.fn(() => ({ matches: true })));
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  window.localStorage.clear();
  window.history.replaceState(null, "", "/");
  document.documentElement.removeAttribute("style");
  document.body.removeAttribute("style");
  document.getElementById("root")?.remove();
});

describe("Chat Skeleton boundary", () => {
  it("does not start network requests or pretend execution is available", () => {
    const fetch = vi.fn(); vi.stubGlobal("fetch", fetch);
    render(<ChatWorkbenchPage />);
    for (const id of ["chat-send", "chat-new-session", "chat-stop-current"]) {
      expect((screen.getByTestId(id) as HTMLButtonElement).disabled).toBe(true);
      fireEvent.click(screen.getByTestId(id));
    }
    expect((screen.getByTestId("chat-prompt") as HTMLTextAreaElement).disabled).toBe(false);
    expect(fetch).not.toHaveBeenCalled();
  });
  it("keeps only the panel control in the session header", () => {
    render(<ChatWorkbenchPage />);
    expect(screen.queryByTestId("chat-theme-toggle")).toBeNull();
    expect(screen.queryByTestId("project-binding")).toBeNull();
    expect(screen.getByTestId("chat-panel-toggle").closest(".chat-session-bar")).not.toBeNull();
    expect(screen.getByRole("tab", { name: "对话" }).closest(".chat-subbar")).not.toBeNull();
    expect(screen.getByTestId("chat-relations-bar").closest(".chat-subbar")).not.toBeNull();
    fireEvent.click(screen.getByTestId("chat-panel-toggle"));
    expect(screen.getByTestId("chat-execution-panel").hasAttribute("hidden")).toBe(false);
    expect(screen.queryByText("仅展示实际执行产生的事件与文件变更")).toBeNull();
    fireEvent.click(screen.getByTestId("chat-panel-toggle"));
    expect(screen.getByTestId("chat-execution-panel").hasAttribute("hidden")).toBe(true);
  });
  it("keeps the trace tab content on the same width rail as the composer", async () => {
    // @ts-expect-error Vitest runs this assertion in Node; app build does not import node:fs.
    const { readFileSync } = await import("node:fs");
    const css = readFileSync("src/styles/chat-workbench.css", "utf8");
    expect(css).toContain(".chat-main > .chat-composer");
    expect(css).toMatch(/\.chat-main > \.chat-composer\s*\{[\s\S]*width:\s*min\(100% - 48px,\s*1120px\);[\s\S]*max-width:\s*1120px;/);
    expect(css).toMatch(/\.chat-main > \.chat-execution-panel \.trace-wrap,\n\.chat-trajectory\.trace-wrap\s*\{[\s\S]*width:\s*min\(100% - 48px,\s*1120px\);[\s\S]*max-width:\s*1120px;[\s\S]*padding:\s*4px 0 40px;/);
    expect(css).toMatch(/@media\(max-width: 820px\)\s*\{[\s\S]*\.chat-main > \.chat-execution-panel \.trace-wrap,\n  \.chat-trajectory\.trace-wrap\s*\{[\s\S]*width:\s*calc\(100% - 24px\);[\s\S]*padding:\s*4px 0 28px;/);
  });
  it("syncs the dark workbench background to the browser root and restores it on unmount", () => {
    const root = document.createElement("div");
    root.id = "root";
    root.style.backgroundColor = "rgb(1, 2, 3)";
    document.body.appendChild(root);
    document.documentElement.style.backgroundColor = "rgb(4, 5, 6)";
    document.body.style.backgroundColor = "rgb(7, 8, 9)";

    const { unmount } = render(<ChatWorkbenchPage />);

    expect(document.documentElement.style.backgroundColor).toBe("rgb(10, 13, 20)");
    expect(document.body.style.backgroundColor).toBe("rgb(10, 13, 20)");
    expect(root.style.backgroundColor).toBe("rgb(10, 13, 20)");

    unmount();

    expect(document.documentElement.style.backgroundColor).toBe("rgb(4, 5, 6)");
    expect(document.body.style.backgroundColor).toBe("rgb(7, 8, 9)");
    expect(root.style.backgroundColor).toBe("rgb(1, 2, 3)");
  });
  it("retains the login guard on direct Chat navigation", () => {
    window.history.replaceState(null, "", "/chat");
    render(<App />);
    expect(screen.queryByTestId("chat-shell")).toBeNull();
    expect(window.location.pathname).toBe("/login");
  });
  it("redirects to login when refreshing Chat with an expired server session", async () => {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester", started_at: "2026-09-30T00:00:00Z" }));
    window.history.replaceState(null, "", "/chat");
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      if (String(input) === "/api/v1/chat/spaces") {
        return new Response(JSON.stringify({ code: 1001, message: "认证或权限校验失败", data: null }), { status: 401, headers: { "Content-Type": "application/json" } });
      }
      return new Response(JSON.stringify({ code: 0, data: {} }), { headers: { "Content-Type": "application/json" } });
    }));

    render(<App />);

    await waitFor(() => expect(window.location.pathname).toBe("/login"));
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(screen.queryByTestId("chat-shell")).toBeNull();
  });
  it("redirects expired local Chat sessions before starting protected requests", () => {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester", expires_at: "2000-01-01T00:00:00.000Z" }));
    window.history.replaceState(null, "", "/chat");
    const fetch = vi.fn();
    vi.stubGlobal("fetch", fetch);

    render(<App />);

    expect(window.location.pathname).toBe("/login");
    expect(window.localStorage.getItem("moonbox.session")).toBeNull();
    expect(fetch).not.toHaveBeenCalled();
  });
  it("restores history without governance panels and only polls backend automatic applications", async () => {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester", started_at: "2026-09-29T10:00:00Z" }));
    window.history.replaceState(null, "", "/chat?space_id=space&conversation_id=conversation");
    const candidate = { id: "candidate", object_id: "BUG-0024-capture", state: "pending", revision: 2, manifest_hash: "b".repeat(64), files: [{ path: "issues/bugs/plan/BUG-0024-capture/bug.md", diff: "- old\n+ new" }], application: { id: "operation", state: "pending", phase: "queued" } };
    const conversation = { id: "conversation", space_id: "space", repository_id: "repo", title: "BUG-0024-capture · 生成 Bug", archived: false, pinned: false, active_turn_id: null, created_at: "2026-09-29T10:00:00Z", updated_at: "2026-09-29T10:00:00Z" };
    const workspace = { workspace_id: "space", name: "验证空间", slug: "space", organization_name: "MoonBox", description: "", timezone: "Asia/Shanghai", member_count: 1, role: "拥有者", readonly: false };
    const fetch = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const data = (value: unknown, status = 200) => new Response(JSON.stringify({ code: 0, data: value }), { status, headers: { "Content-Type": "application/json" } });
      if (url === "/api/v1/chat/spaces") return data([{ id: "space", name: "验证空间" }]);
      if (url.includes("/api/v1/chat/capabilities")) return data({ execution_ready: true, reason: "", repositories: [{ id: "repo", space_id: "space" }], execution: { policy_version: "test", agents: [], models: [], reasoning: [], defaults: { agent: "codex", model: "gpt-6-astra", reasoning: "low" } } });
      if (url.includes("/api/v1/chat/conversations?")) return data({ items: [conversation], total: 1 });
      if (url === "/api/v1/chat/conversations/conversation") return data(conversation);
      if (url.includes("/api/v1/chat/conversations/conversation/turns")) return data({ items: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/messages")) return data({ items: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/relations")) return data({ primary: { id: "BUG-0024-capture", title: "登录失效刷新未跳转", kind: "BUG" }, references: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/objects")) return data({ items: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/governance-candidates")) return data({ items: [candidate] });
      if (url.includes("/api/v1/chat/governance-applications/operation")) return data({ id: "operation", state: "applied", phase: "verified" });
      if (url === "/api/v1/requirement-center/projects") return data({ current_user: { name: "tester" }, workspaces: [workspace], selected_workspace_id: "space", projects: [{ space_id: "space", repository_id: "repo", status: "connected", readonly: false }] });
      return data({});
    });
    vi.stubGlobal("fetch", fetch);
    render(<ChatWorkbenchPage />);
    await waitFor(() => expect(fetch.mock.calls.some(([url]) => String(url).includes("/governance-applications/operation"))).toBe(true));
    expect(fetch.mock.calls.some(([url, init]) => String(url).includes("/governance-candidates/candidate/applications") && init?.method === "POST")).toBe(false);
    for (const text of ["待应用成果", "查看成果", "审阅治理成果", "确认应用"]) {
      expect(screen.queryByText(text)).toBeNull();
    }
  });
  it("keeps completed conversation content visible when turn polling has a network interruption", async () => {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester", started_at: "2026-09-30T00:00:00Z" }));
    window.history.replaceState(null, "", "/chat?space_id=space&conversation_id=conversation");
    const conversation = { id: "conversation", space_id: "space", repository_id: "repo", title: "REQ-0027 · 生成需求", archived: false, pinned: false, active_turn_id: null, created_at: "2026-09-30T00:00:00Z", updated_at: "2026-09-30T00:00:00Z" };
    const workspace = { workspace_id: "space", name: "验证空间", slug: "space", organization_name: "MoonBox", description: "", timezone: "Asia/Shanghai", member_count: 1, role: "拥有者", readonly: false };
    vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      const data = (value: unknown) => new Response(JSON.stringify({ code: 0, data: value }), { headers: { "Content-Type": "application/json" } });
      if (url === "/api/v1/chat/spaces") return data([{ id: "space", name: "验证空间" }]);
      if (url.includes("/api/v1/chat/capabilities")) return data({ execution_ready: true, reason: "", repositories: [{ id: "repo", space_id: "space" }], execution: { policy_version: "test", agents: [], models: [], reasoning: [], defaults: { agent: "codex", model: "gpt-6-astra", reasoning: "low" } } });
      if (url.includes("/api/v1/chat/conversations?")) return data({ items: [conversation], total: 1 });
      if (url === "/api/v1/chat/conversations/conversation") return data(conversation);
      if (url.includes("/api/v1/chat/conversations/conversation/turns")) throw new TypeError("NetworkError when attempting to fetch resource.");
      if (url.includes("/api/v1/chat/conversations/conversation/messages")) return data({ items: [{ id: "m1", turn_id: null, role: "assistant", content: "已生成 [REQ-0027 PRD](requirement.md)，状态为 draft。", created_at: "2026-09-30T00:01:00Z", materials: [] }] });
      if (url.includes("/api/v1/chat/conversations/conversation/relations")) return data({ primary: { id: "REQ-0027", title: "命令链实现", kind: "REQ" }, references: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/objects")) return data({ items: [] });
      if (url.includes("/api/v1/chat/conversations/conversation/governance-candidates")) return data({ items: [] });
      if (url === "/api/v1/requirement-center/projects") return data({ current_user: { name: "tester" }, workspaces: [workspace], selected_workspace_id: "space", projects: [{ space_id: "space", repository_id: "repo", status: "connected", readonly: false }] });
      return data({});
    }));
    render(<ChatWorkbenchPage />);
    const conversationRegion = screen.getByTestId("chat-conversation");
    await waitFor(() => expect(conversationRegion.textContent).toContain("已生成"));
    expect(conversationRegion.textContent).toContain("REQ-0027 PRD");
    expect(conversationRegion.textContent).not.toContain("NetworkError when attempting to fetch resource");
    expect(conversationRegion.textContent).not.toContain("重新连接");
    expect(screen.getByTestId("chat-composer").textContent).not.toContain("NetworkError when attempting to fetch resource");
  });
  it.each<ChatAvailability>(["loading", "unavailable", "error", "unknown"])("represents %s without a fabricated terminal state", (availability) => {
    render(<ChatStatus availability={availability} />);
    expect(screen.getByTestId("chat-status").getAttribute("data-state")).toBe(availability);
    expect(screen.queryByText("执行完成")).toBeNull();
  });
});
