import { afterEach, expect, it, vi } from "vitest";
import { readChatEvents } from "./components/chat/chatEvents";
afterEach(() => { vi.unstubAllGlobals(); localStorage.clear(); });
it("uses bearer headers, discards old cursors and deduplicates out of order replay", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  const fetch = vi.fn(async () => new Response('id: 3\nevent: execution.output\ndata: {"text":"safe"}\n\nid: 2\nevent: execution.state\ndata: {"status":"running"}\n\nid: 3\nevent: execution.output\ndata: {"text":"safe"}\n\nid: 1\nevent: execution.state\ndata: {}\n\n', { headers: { "Content-Type": "text/event-stream" } }));
  vi.stubGlobal("fetch", fetch);
  expect((await readChatEvents("turn", 1)).map(e => e.sequence)).toEqual([2, 3]);
  const [url, options] = vi.mocked(globalThis.fetch).mock.calls[0];
  expect(String(url)).toBe("/api/v1/chat/turns/turn/events?after=1");
  expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer synthetic-test-token");
});
it("fails closed when permission has been revoked", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response("", { status: 403 })));
  await expect(readChatEvents("turn", 0)).rejects.toThrow("执行记录已不可访问");
});
