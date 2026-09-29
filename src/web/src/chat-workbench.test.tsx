import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";
import { ChatStatus, type ChatAvailability } from "./components/chat/ChatStatus";
import { ChatWorkbenchPage } from "./pages/catalog/ChatWorkbenchPage";

beforeEach(() => {
  vi.stubGlobal("scrollTo", vi.fn());
  vi.stubGlobal("matchMedia", vi.fn(() => ({ matches: true })));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); window.localStorage.clear(); window.history.replaceState(null, "", "/"); });

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
    const css = readFileSync("src/web/src/styles/chat-workbench.css", "utf8");
    expect(css).toContain(".chat-main > .chat-composer");
    expect(css).toMatch(/\.chat-main > \.chat-composer\s*\{[\s\S]*width:\s*min\(100% - 48px,\s*1120px\);[\s\S]*max-width:\s*1120px;/);
    expect(css).toMatch(/\.chat-main > \.chat-execution-panel \.trace-wrap,\n\.chat-trajectory\.trace-wrap\s*\{[\s\S]*width:\s*min\(100% - 48px,\s*1120px\);[\s\S]*max-width:\s*1120px;[\s\S]*padding:\s*4px 0 40px;/);
    expect(css).toMatch(/@media\(max-width: 820px\)\s*\{[\s\S]*\.chat-main > \.chat-execution-panel \.trace-wrap,\n  \.chat-trajectory\.trace-wrap\s*\{[\s\S]*width:\s*calc\(100% - 24px\);[\s\S]*padding:\s*4px 0 28px;/);
  });
  it("retains the login guard on direct Chat navigation", () => {
    window.history.replaceState(null, "", "/chat");
    render(<App />);
    expect(screen.queryByTestId("chat-shell")).toBeNull();
    expect(window.location.pathname).toBe("/login");
  });
  it.each<ChatAvailability>(["loading", "unavailable", "error", "unknown"])("represents %s without a fabricated terminal state", (availability) => {
    render(<ChatStatus availability={availability} />);
    expect(screen.getByTestId("chat-status").getAttribute("data-state")).toBe(availability);
    expect(screen.queryByText("执行完成")).toBeNull();
  });
});
