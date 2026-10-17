import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { chatRequest, ChatApiError } from "./components/chat/chatApi";
import { readValidFrontendSession } from "./pages/home/frontendSession";

beforeEach(() => {
  window.localStorage.clear();
  window.history.replaceState(null, "", "/chat");
});

afterEach(() => {
  vi.unstubAllGlobals();
  window.localStorage.clear();
  window.history.replaceState(null, "", "/");
});

it("clears the frontend session and redirects to login when Chat API returns 401", async () => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ code: 1001, message: "认证或权限校验失败", data: null }), { status: 401, headers: { "Content-Type": "application/json" } })));

  await expect(chatRequest("/spaces")).rejects.toMatchObject({ status: 401 });

  expect(window.localStorage.getItem("moonbox.session")).toBeNull();
  expect(window.location.pathname).toBe("/login");
});

it("keeps the session when Chat API returns 403", async () => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ code: 1003, message: "无权访问", data: null }), { status: 403, headers: { "Content-Type": "application/json" } })));

  await expect(chatRequest("/spaces")).rejects.toMatchObject({ status: 403 });

  expect(window.localStorage.getItem("moonbox.session")).toContain("synthetic");
  expect(window.location.pathname).toBe("/chat");
});

it("keeps the session when Chat API has a network interruption", async () => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester" }));
  vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("NetworkError when attempting to fetch resource."); }));

  await expect(chatRequest("/spaces")).rejects.toBeInstanceOf(ChatApiError);

  expect(window.localStorage.getItem("moonbox.session")).toContain("synthetic");
  expect(window.location.pathname).toBe("/chat");
});

it("drops expired frontend sessions before protected routes render", () => {
  window.localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic", username: "tester", expires_at: "2000-01-01T00:00:00.000Z" }));

  expect(readValidFrontendSession()).toBeNull();
  expect(window.localStorage.getItem("moonbox.session")).toBeNull();
});
