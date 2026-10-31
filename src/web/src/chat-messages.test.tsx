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
    if (url.includes("/questions")) return new Response(JSON.stringify({ code: 0, data: { items: [] } }));
    if (url.includes("/events")) return new Response([
      'id: 1',
      'event: execution.usage',
      'data: {"total_tokens":321,"duration_ms":1500,"reasoning_duration_ms":832}',
      '',
      '',
    ].join("\n"), { headers: { "Content-Type": "text/event-stream" } });
    if (url.includes("/materials/img/content")) return new Response(new Blob(["image"], { type: "image/png" }));
    if (url.includes("/turns/t2")) return new Response(JSON.stringify({ code: 0, data: { id: "t2", status: "completed", usage: { total_tokens: 321, duration_ms: 1500, reasoning_duration_ms: 832 }, created_at: "2026-09-18T10:35:00Z", updated_at: "2026-09-18T10:35:02Z" } }));
    return new Response(JSON.stringify(messagesPayload));
  }));
}

function stubRunningAssistantFetch() {
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.includes("/questions")) return new Response(JSON.stringify({ code: 0, data: { items: [] } }));
    if (url.includes("/events")) return new Response([
      'id: 1',
      'event: execution.output',
      'data: {"text":"dry-run 在创建临时锁前失败，原因是当前环境没有可写的临时目录。我会改用现有注册表文件的只读文件锁运行同步逻辑，避免新增第五个文件，并继续检查写入范围。"}',
      '',
      '',
    ].join("\n"), { headers: { "Content-Type": "text/event-stream" } });
    if (url.includes("/turns/t2")) return new Response(JSON.stringify({ code: 0, data: { id: "t2", status: "running", created_at: "2026-09-30T00:02:00Z", updated_at: "2026-09-30T00:02:10Z" } }));
    return new Response(JSON.stringify({
      code: 0,
      data: {
        items: [{
          id: "m-running",
          turn_id: "t2",
          role: "assistant",
          content: "",
          created_at: "2026-09-30T00:02:00Z",
          materials: [],
        }],
      },
    }));
  }));
}

it("keeps assistant messages full-width while preserving user bubble limits", async () => {
  // @ts-expect-error Vitest runs this assertion in Node, while the web tsconfig intentionally omits Node globals.
  const { readFileSync } = await import("node:fs");
  const css = readFileSync("src/styles/chat-workbench.css", "utf8");
  expect(css).toMatch(/\.chat-message-history\s*{[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).not.toMatch(/\.chat-message-history\s*{[^}]*max-width:\s*(?:780|820)px;/s);
  expect(css).toMatch(/\.chat-message-block\.turn-assistant\s*{[^}]*justify-items:\s*stretch;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-message\s*{[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-message\s*{[^}]*justify-self:\s*stretch;[^}]*box-sizing:\s*border-box;/s);
  expect(css).toMatch(/\.chat-assistant-col\s*{[^}]*flex:\s*1 1 auto;[^}]*width:\s*100%;[^}]*min-width:\s*0;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-message-bubble\s*{[^}]*align-self:\s*stretch;[^}]*display:\s*block;[^}]*box-sizing:\s*border-box;[^}]*width:\s*100%;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-markdown\s*{[^}]*display:\s*block;[^}]*box-sizing:\s*border-box;[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-turn-activity\s*{[^}]*align-self:\s*stretch;[^}]*box-sizing:\s*border-box;[^}]*display:\s*flex;[^}]*flex-direction:\s*column;[^}]*align-items:\s*stretch;[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.chat-message-block:not\(\.turn-assistant\)\s+\.chat-turn-activity\s*>\s*\*\s*{[^}]*max-width:\s*min\(720px,\s*72%\);/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-turn-activity\s*>\s*:not\(\.chat-tool-summary\)\s*{[^}]*box-sizing:\s*border-box;[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-turn-activity\s+\.chat-tool-summary\s*{[^}]*align-self:\s*flex-start;[^}]*justify-content:\s*flex-start;[^}]*width:\s*fit-content;[^}]*max-width:\s*100%;[^}]*background:\s*transparent;/s);
  expect(css).toMatch(/\.turn-assistant\s+\.chat-turn-activity\s+p\[role="status"\],[\s\S]*?\.turn-assistant\s+\.chat-turn-activity\s+p\[role="alert"\]\s*{[^}]*box-sizing:\s*border-box;[^}]*width:\s*100%;[^}]*max-width:\s*none;/s);
  expect(css).toMatch(/\.chat-message-user\s*{[^}]*width:\s*min\(760px,\s*88%\);[^}]*max-width:\s*88%;/s);
});

it("computes assistant visual block width from the rendered DOM", async () => {
  // @ts-expect-error Vitest runs this assertion in Node, while the web tsconfig intentionally omits Node globals.
  const { readFileSync } = await import("node:fs");
  const style = document.createElement("style");
  style.textContent = readFileSync("src/styles/chat-workbench.css", "utf8");
  document.head.appendChild(style);
  try {
    stubObjectUrls();
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
    stubMessagesFetch();
    render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
    await screen.findByText("我看到了你的反馈。");
    const history = screen.getByTestId("chat-message-history") as HTMLElement;
    const assistant = screen.getByText("我看到了你的反馈。").closest(".turn-assistant") as HTMLElement;
    const column = assistant.querySelector(".chat-assistant-col") as HTMLElement;
    const bubble = assistant.querySelector(".chat-message-bubble") as HTMLElement;
    const markdown = assistant.querySelector(".chat-markdown") as HTMLElement;
    expect(getComputedStyle(history).width).toBe("100%");
    expect(getComputedStyle(history).maxWidth).toBe("none");
    expect(getComputedStyle(assistant.querySelector(".chat-message") as HTMLElement).width).toBe("100%");
    expect(getComputedStyle(column).width).toBe("100%");
    expect(getComputedStyle(column).alignItems).toBe("stretch");
    expect(getComputedStyle(bubble).alignSelf).toBe("stretch");
    expect(getComputedStyle(bubble).display).toBe("block");
    expect(getComputedStyle(bubble).boxSizing).toBe("border-box");
    expect(getComputedStyle(bubble).width).toBe("100%");
    expect(getComputedStyle(markdown).display).toBe("block");
    expect(getComputedStyle(markdown).boxSizing).toBe("border-box");
    expect(getComputedStyle(markdown).width).toBe("100%");
    expect(getComputedStyle(markdown).maxWidth).toBe("none");
  } finally {
    style.remove();
  }
});

it("computes running assistant activity and status output as full-width", async () => {
  // @ts-expect-error Vitest runs this assertion in Node, while the web tsconfig intentionally omits Node globals.
  const { readFileSync } = await import("node:fs");
  const style = document.createElement("style");
  style.textContent = readFileSync("src/styles/chat-workbench.css", "utf8");
  document.head.appendChild(style);
  try {
    localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
    stubRunningAssistantFetch();
    render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
    const status = await screen.findByText(/dry-run 在创建临时锁前失败/);
    expect(status.getAttribute("aria-live")).toBe("off");
    const assistant = status.closest(".turn-assistant") as HTMLElement;
    const activity = status.closest(".chat-turn-activity") as HTMLElement;
    const summary = activity.querySelector(".chat-tool-summary") as HTMLElement;
    const message = assistant.querySelector(".chat-message") as HTMLElement;
    const column = assistant.querySelector(".chat-assistant-col") as HTMLElement;
    expect(getComputedStyle(message).width).toBe("100%");
    expect(getComputedStyle(column).width).toBe("100%");
    expect(getComputedStyle(activity).alignSelf).toBe("stretch");
    expect(getComputedStyle(activity).boxSizing).toBe("border-box");
    expect(getComputedStyle(activity).display).toBe("flex");
    expect(getComputedStyle(activity).flexDirection).toBe("column");
    expect(getComputedStyle(activity).alignItems).toBe("stretch");
    expect(getComputedStyle(activity).width).toBe("100%");
    expect(getComputedStyle(activity).maxWidth).toBe("none");
    expect(getComputedStyle(summary).alignSelf).toBe("flex-start");
    expect(getComputedStyle(summary).justifyContent).toBe("flex-start");
    expect(getComputedStyle(summary).width).toBe("fit-content");
    expect(getComputedStyle(summary).maxWidth).toBe("100%");
    expect(getComputedStyle(summary).backgroundColor).toBe("rgba(0, 0, 0, 0)");
    expect(getComputedStyle(status).boxSizing).toBe("border-box");
    expect(getComputedStyle(status).width).toBe("100%");
    expect(getComputedStyle(status).maxWidth).toBe("none");
    expect(getComputedStyle(status).overflowWrap).toBe("anywhere");
  } finally {
    style.remove();
  }
});

it("shows localized inline message errors instead of browser NetworkError", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("NetworkError when attempting to fetch resource."); }));
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  expect((await screen.findByRole("alert")).textContent).toContain("消息暂不可读，请稍后重试");
  expect(screen.queryByText(/NetworkError when attempting to fetch resource/)).toBeNull();
});

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
  await waitFor(() => expect(vi.mocked(fetch).mock.calls.some(([url]) => String(url).includes("/materials/img/content"))).toBe(true));
  fireEvent.click(userMessage!.querySelector("button[aria-label='查看附件 图片.png']")!);
  expect(await screen.findByRole("dialog", { name: "查看附件 图片.png" })).not.toBeNull();
  const materialCalls = vi.mocked(fetch).mock.calls.filter(([url]) => String(url).includes("/materials/img/content"));
  expect(materialCalls.length).toBeGreaterThanOrEqual(1);
  expect(new Headers(materialCalls[0][1]?.headers).get("Authorization")).toBe("Bearer synthetic");
  fireEvent.click(screen.getByText("关闭"));
  await waitFor(() => expect(screen.queryByRole("dialog", { name: "查看附件 图片.png" })).toBeNull());
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

it("hides governance execution context from visible user messages", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.defineProperty(navigator, "clipboard", { configurable: true, value: { writeText } });
  vi.stubGlobal("fetch", vi.fn(async (url: string) => url.includes("/questions")
    ? new Response(JSON.stringify({ code: 0, data: { items: [] } }))
    : new Response(JSON.stringify({
    code: 0,
    data: {
      items: [{
        id: "m-governance",
        turn_id: "t-governance",
        role: "user",
        content: "/bug-generate BUG-0024-capture\n所有生成Markdown必须有中文业务title与一致一级标题。\n本次仅生成目标 bug.md，同步前先检查 dry-run。",
        created_at: "2026-09-29T09:01:33Z",
        effective_config: { agent: "codex", model: "gpt-6-astra", reasoning: "low" },
        materials: [],
      }],
    },
  }))));
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()} />);
  await screen.findByText("/bug-generate BUG-0024-capture");
  expect(screen.queryByText(/所有生成Markdown/)).toBeNull();
  expect(screen.queryByText(/dry-run/)).toBeNull();
  const user = screen.getByText("/bug-generate BUG-0024-capture").closest(".chat-message-user");
  fireEvent.click(user!.querySelector("button[aria-label='复制消息']")!);
  await waitFor(() => expect(writeText).toHaveBeenCalledWith("/bug-generate BUG-0024-capture"));
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
