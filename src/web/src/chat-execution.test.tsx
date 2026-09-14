import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { ExecutionPanel } from "./components/chat/ExecutionPanel";
import type { ConversationRead } from "./components/chat/chatApi";
afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });
it("stops the active run while inspecting history and renders event text without HTML execution", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  const make = (id: string, status: string) => ({ id, conversation_id: "c", status, created_at: "2026-09-08T00:00:00Z" });
  vi.stubGlobal("fetch", vi.fn(async (url: string, options: RequestInit = {}) => {
    if (url.includes("/events")) return new Response('id: 1\nevent: execution.output\ndata: {"text":"<img src=x onerror=alert(1)>"}\n\n', { headers: { "Content-Type": "text/event-stream" } });
    let data: unknown;
    if (url.endsWith("/interrupt")) data = make("active", "stopping");
    else if (url.endsWith("/diff")) data = { available: true, files: [] };
    else data = { items: [make("active", "running"), make("historical", "completed")] };
    return new Response(JSON.stringify({ code: 0, data }), { headers: { "Content-Type": "application/json" } });
  }));
  render(<ExecutionPanel conversation={{ id: "c" } as ConversationRead} />);
  await waitFor(() => expect((screen.getByTestId("chat-turn-select") as HTMLSelectElement).disabled).toBe(false));
  fireEvent.change(screen.getByTestId("chat-turn-select"), { target: { value: "historical" } });
  await screen.findByText(/<img src=x onerror=alert/, { selector: ".chat-event-group pre" });
  expect(screen.getByTestId("chat-turn-status").textContent).toBe("所选轮次当前状态：已完成");
  expect(screen.getByTestId("chat-raw-events").hasAttribute("open")).toBe(false);
  expect(document.querySelector("img")).toBeNull();
  fireEvent.click(screen.getByTestId("chat-stop-current"));
  fireEvent.click(screen.getByTestId("chat-modal-submit"));
  await screen.findByText("停止中");
  const calls = vi.mocked(fetch).mock.calls;
  expect(calls.some(([url, opts]) => url === "/api/v1/chat/turns/active/interrupt" && opts?.method === "POST")).toBe(true);
  expect(calls.some(([url]) => url === "/api/v1/chat/turns/historical/interrupt")).toBe(false);
});
it("does not retarget an open stop confirmation to a newer run", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  let newer = false;
  const make = (id: string, status: string) => ({ id, conversation_id: "c", status, created_at: "2026-09-08T00:00:00Z" });
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.includes("/events")) return new Response(": empty\n\n", { headers: { "Content-Type": "text/event-stream" } });
    const data = url.endsWith("/turns") ? { items: newer ? [make("new", "running"), make("old", "completed")] : [make("old", "running")] } : url.endsWith("/context") ? [] : { available: false, files: [] };
    return new Response(JSON.stringify({ code: 0, data }));
  }));
  render(<ExecutionPanel conversation={{ id: "c" } as ConversationRead} />);
  await waitFor(() => expect((screen.getByTestId("chat-stop-current") as HTMLButtonElement).disabled).toBe(false));
  fireEvent.click(screen.getByTestId("chat-stop-current")); newer = true;
  await waitFor(() => expect(document.querySelector('option[value="new"]')).not.toBeNull(), { timeout: 4000 });
  expect((screen.getByTestId("chat-modal-submit") as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByTestId("chat-modal-submit"));
  expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).endsWith("/interrupt"))).toBe(false);
});
