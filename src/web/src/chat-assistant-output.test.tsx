import { afterEach, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
import { ConversationMessages } from "./components/chat/ConversationMessages";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });

it("renders saved partial body independently of the unknown terminal warning", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  vi.stubGlobal("fetch", vi.fn(async (url: string) => {
    if (url.includes("/events")) return new Response("", { headers: { "Content-Type": "text/event-stream" } });
    const data = url.includes("/turns/") ? {id:"t",status:"unknown"} : {items:[{
      id:"assistant-t",turn_id:"t",role:"assistant",content:"已保存的合成正文",created_at:"2026-10-08T10:00:00Z",
      output_partial:true,output_truncated:true,output_source:"events",
    }]};
    return new Response(JSON.stringify({code:0,data}));
  }));
  render(<ConversationMessages conversationId="c" onTrace={vi.fn()}/>);
  await screen.findByText("已保存的合成正文");
  expect((await screen.findByTestId("turn-status-feedback")).textContent).toContain("输出内容不完整");
  expect(screen.getAllByText("输出内容不完整")).toHaveLength(1);
  await screen.findByText(/不要重复发送命令/);
  expect(screen.queryByText("已完成",{exact:true})).toBeNull();
});

it("keeps a normal final answer free of partial-output warnings", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({code:0,data:{items:[{
    id:"m",turn_id:"t",role:"assistant",content:"合成最终答案",created_at:"2026-10-08T10:00:00Z",output_partial:false,
  }]}}))));
  render(<ConversationMessages conversationId="c"/>);
  await screen.findByText("合成最终答案");
  expect(screen.queryByTestId("chat-partial-output")).toBeNull();
});

it("collapses an assistant success claim when its governance candidate was rejected", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({code:0,data:{items:[{
    id:"m",turn_id:"rejected-turn",role:"assistant",content:"已推进待评审",created_at:"2026-10-08T10:00:00Z",output_partial:false,
  }]}}))));
  render(<ConversationMessages conversationId="c" rejectedGovernanceTurnIds={["rejected-turn"]}/>);
  const details=await screen.findByTestId("chat-rejected-governance-output");
  expect(details.hasAttribute("open")).toBe(false);
  expect(details.textContent).toContain("治理结果未通过校验");
  expect(details.textContent).toContain("已推进待评审");
});
