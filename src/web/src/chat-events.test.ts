import { afterEach, expect, it, vi } from "vitest";
import { chatRequest } from "./components/chat/chatApi";
import { readChatEvents } from "./components/chat/chatEvents";
afterEach(() => { vi.unstubAllGlobals(); localStorage.clear(); });
it.each([
  [403, 2501, "space denied", "无权访问当前空间或会话，请切换空间"],
  [403, 2509, "object denied", "关联对象不可访问，请检查对象状态或权限"],
  [503, 2509, "关联对象文档尚未就绪，请稍后重试", "关联对象文档尚未就绪，请稍后重试"],
])("distinguishes permission and object availability: %s/%s", async (status, code, message, expected) => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ code, message }), { status: Number(status) })));
  await expect(chatRequest("/conversations/synthetic/relations")).rejects.toThrow(String(expected));
});
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
it("normalizes chat network failures instead of leaking browser-native messages", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("NetworkError when attempting to fetch resource."); }));
  await expect(chatRequest("/spaces")).rejects.toThrow("工作台连接暂时中断，请检查服务状态后重试");
  await expect(readChatEvents("turn", 0)).rejects.toThrow("执行轨迹连接暂时中断，请稍后重试");
});
it("keeps navigation aborts as aborts for callers to ignore", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-test-token" }));
  vi.stubGlobal("fetch", vi.fn(async () => { throw new DOMException("Aborted", "AbortError"); }));
  await expect(chatRequest("/spaces")).rejects.toMatchObject({ name: "AbortError" });
  await expect(readChatEvents("turn", 0)).rejects.toMatchObject({ name: "AbortError" });
});
