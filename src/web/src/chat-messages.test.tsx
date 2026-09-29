import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { ConversationMessages } from "./components/chat/ConversationMessages";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks(); localStorage.clear(); });

function stubObjectUrls() {
  let index = 0;
  Object.defineProperty(URL, "createObjectURL", { configurable: true, value: vi.fn(() => `blob:chat-material-${++index}`) });
  Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: vi.fn() });
}

const messagesPayload = {
  code: 0,
  data: {
    items: [
      {
        id: "m1",
        turn_id: "t1",
        role: "user",
        content: "卡片的用户信息有问题\n\n第二段说明：继续保持块级阅读层。\n\n图片引用：图片.png · image/png · 54059 bytes\nSkill 引用： explore",
        created_at: "2026-09-18T10:34:05Z",
        effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "high" },
        materials: [
          { kind: "image", ref_id: "img", name: "图片.png", mime_type: "image/png", size_bytes: 108544, metadata: {} },
          { kind: "skill", ref_id: "skill", name: "explore", metadata: { injection_scope: "context_reference_only" } },
        ],
      },
      {
        id: "m2",
        turn_id: "t2",
        role: "assistant",
        content: "我看到了你的反馈。\n\n当前判断：根因未确认，需要补充页面名称。\n\n未修改代码或创建 Issue。",
        created_at: "2026-09-18T10:35:05Z",
        materials: [
          { kind: "image", ref_id: "img", name: "图片.png", mime_type: "image/png", size_bytes: 108544, metadata: { preview_url: "/api/v1/chat/materials/img/content" } },
          { kind: "skill", ref_id: "skill", name: "explore", metadata: { injection_scope: "context_reference_only" } },
        ],
      },
    ],
  },
};

function stubMessagesFetch() {
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.includes("/events")) return new Response([
      'id: 1',
      'event: execution.usage',
      'data: {"total_tokens":321,"duration_ms":1500,"reasoning_duration_ms":832}',
      '',
      '',
    ].join("\n"), { headers: { "Content-Type": "text/event-stream" } });
    if (url.includes("/materials/img/content")) return new Response(new Blob(["image"], { type: "image/png" }));
    if (url.includes("/turns/t2")) return new Response(JSON.stringify({ code: 0, data: { id: "t2", status: "completed", created_at: "2026-09-18T10:35:00Z", updated_at: "2026-09-18T10:35:02Z" } }));
    return new Response(JSON.stringify(messagesPayload));
  }));
}

it("renders user attachments above the bubble and skill chips inside the message flow", async () => {
  stubObjectUrls();
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  stubMessagesFetch();
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  await screen.findByText("卡片的用户信息有问题");
  const userMessage = screen.getByText("卡片的用户信息有问题").closest(".chat-message-user");
  expect(userMessage).not.toBeNull();
  await waitFor(() => expect(userMessage?.querySelector(".chat-message-bubble")?.textContent).toContain("Explore"));
  expect(userMessage?.closest(".turn-user")).not.toBeNull();
  expect(userMessage?.querySelector(".chat-turn-content")).not.toBeNull();
  expect(userMessage?.querySelector(".chat-message-attachments")?.textContent).toContain("PNG");
  expect(userMessage?.querySelector(".chat-message-bubble")?.textContent).toContain("卡片的用户信息有问题");
  const inlineFlow = userMessage?.querySelector("[data-testid='chat-user-inline-flow']");
  expect(inlineFlow).not.toBeNull();
  expect(inlineFlow?.querySelector(".chat-message-skills")?.textContent).toBe("Explore");
  expect(inlineFlow?.querySelector(".chat-user-inline-text")?.textContent).toBe("卡片的用户信息有问题");
  expect(inlineFlow?.textContent).toBe("Explore卡片的用户信息有问题");
  expect(userMessage?.querySelector(".chat-markdown")?.textContent).toContain("第二段说明：继续保持块级阅读层。");
  expect(userMessage?.querySelector(".chat-message-bubble")?.textContent).not.toContain("Skill 引用");
  expect(userMessage?.querySelector(".chat-message-bubble")?.textContent).not.toContain("图片引用");
  await waitFor(() => expect(userMessage?.querySelector(".chat-message-attachment img")?.getAttribute("src")).toMatch(/^blob:chat-material-/));
  fireEvent.click(userMessage!.querySelector("button[aria-label='查看附件 图片.png']")!);
  expect(await screen.findByRole("dialog", { name: "查看附件 图片.png" })).not.toBeNull();
  await waitFor(() => expect(screen.getByRole("img", { name: "图片.png" }).getAttribute("src")).toMatch(/^blob:chat-material-/));
  const materialCalls = vi.mocked(fetch).mock.calls.filter(([url]) => String(url).includes("/materials/img/content"));
  expect(materialCalls.length).toBeGreaterThanOrEqual(2);
  expect(new Headers(materialCalls[0][1]?.headers).get("Authorization")).toBe("Bearer synthetic");
  fireEvent.click(screen.getByText("关闭"));
  await waitFor(() => expect(URL.revokeObjectURL).toHaveBeenCalled());
  expect(userMessage?.querySelector(".chat-message-skill .lucide-sparkles")).not.toBeNull();
  expect(userMessage?.querySelector(".chat-message-skills")?.textContent).toBe("Explore");
  const meta = userMessage?.querySelector(".chat-message-meta");
  expect(meta?.querySelector(".chat-message-model")?.textContent).toBe("Codex · GPT-6 Astra · High");
  expect(meta?.textContent).not.toContain("查看本轮轨迹");
  expect(meta?.querySelector("button[aria-label='复制消息'] svg")).not.toBeNull();
});

it("renders assistant messages with avatar, assistant column, body and meta", async () => {
  stubObjectUrls();
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  stubMessagesFetch();
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  await screen.findByText("我看到了你的反馈。");
  const assistant = screen.getByText("我看到了你的反馈。").closest(".turn-assistant");
  expect(assistant).not.toBeNull();
  expect(assistant?.querySelector(".chat-assistant-avatar")).not.toBeNull();
  expect(assistant?.querySelector(".chat-assistant-col")).not.toBeNull();
  expect(assistant?.querySelector(".chat-message-bubble")?.textContent).toContain("我看到了你的反馈。");
  expect(assistant?.querySelector(".chat-message-bubble")?.textContent).not.toContain("Explore");
  expect(assistant?.querySelector(".chat-message-attachments")).toBeNull();
  expect(assistant?.querySelector(".chat-turn-activity")).not.toBeNull();
  expect(assistant?.querySelector(".chat-assistant-col")?.firstElementChild?.className).toContain("chat-turn-activity");
  const highlights = Array.from(assistant?.querySelectorAll(".chat-important-highlight") || []).map((node) => node.textContent);
  expect(highlights).toEqual(["根因未确认", "未修改代码或创建 Issue"]);
  expect(highlights).not.toContain("需要补充页面名称");
  expect(highlights).not.toContain("我看到了你的反馈。");
  const meta = assistant?.querySelector(".chat-assistant-meta");
  expect(meta?.querySelector("button[aria-label='复制消息'] svg")).not.toBeNull();
  expect(meta?.firstElementChild?.getAttribute("aria-label")).toBe("复制消息");
  expect(meta?.querySelector("button[aria-label='使用的 Skill：Explore'] .lucide-sparkles")).not.toBeNull();
  expect(meta?.textContent).not.toContain("查看本轮轨迹");
  await waitFor(() => expect(meta?.textContent).toContain("Token 321"));
  expect(meta?.textContent).toContain("思考 832 毫秒");
  expect(meta?.textContent).toContain("耗时 2秒");
});

it("copies visible user and assistant message text", async () => {
  stubObjectUrls();
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  stubMessagesFetch();
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  await screen.findByText("卡片的用户信息有问题");
  const user = screen.getByText("卡片的用户信息有问题").closest(".chat-message-user");
  fireEvent.click(user!.querySelector("button[aria-label='复制消息']")!);
  await waitFor(() => expect(writeText).toHaveBeenCalledWith("卡片的用户信息有问题\n\n第二段说明：继续保持块级阅读层。"));
  expect(user?.querySelector("button[aria-label='已复制'] .lucide-check")).not.toBeNull();
  await screen.findByText("我看到了你的反馈。");
  const assistant = screen.getByText("我看到了你的反馈。").closest(".turn-assistant");
  fireEvent.click(assistant!.querySelector("button[aria-label='复制消息']")!);
  await waitFor(() => expect(writeText).toHaveBeenCalledWith("我看到了你的反馈。\n\n当前判断：根因未确认，需要补充页面名称。\n\n未修改代码或创建 Issue。"));
  await screen.findAllByLabelText("已复制");
  expect(assistant?.querySelector("button[aria-label='已复制'] .lucide-check")).not.toBeNull();
});

it("falls back to execCommand and reports copy failures", async () => {
  stubObjectUrls();
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  stubMessagesFetch();
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: undefined });
  const exec = vi.fn().mockReturnValueOnce(true).mockReturnValueOnce(false);
  Object.defineProperty(document, "execCommand", { configurable: true, value: exec });
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  await screen.findByText("卡片的用户信息有问题");
  fireEvent.click(screen.getAllByLabelText("复制消息")[0]);
  await screen.findByLabelText("已复制");
  fireEvent.click(screen.getAllByLabelText("复制消息")[0]);
  await screen.findByLabelText("复制失败");
  expect(screen.getByLabelText("复制失败").querySelector(".lucide-circle-alert")).not.toBeNull();
  expect(exec).toHaveBeenCalledWith("copy");
});
