import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { TurnActivity } from "./components/chat/TurnActivity";
beforeEach(()=>localStorage.setItem("moonbox.session",JSON.stringify({username:"synthetic",access_token:"synthetic"})));
afterEach(()=>{cleanup();vi.unstubAllGlobals();localStorage.clear();});
it.each(["container_toolchain_unavailable","workspace_unapplied_changes","workspace_fact_source_stale","governance_validation_failed","workspace_prepare_failed"])("shows a terminal preparation reason for %s",async(error_code)=>{
 vi.stubGlobal("fetch",vi.fn(async(url:string)=>url.includes("/events")?new Response("",{headers:{"Content-Type":"text/event-stream"}}):new Response(JSON.stringify({code:0,data:{id:"t",status:"failed",error_code}}))));
 render(<TurnActivity turnId="t" onTrace={()=>{}}/>);
 expect(await screen.findByText("执行前阻断")).toBeTruthy();
 expect(screen.getByRole("status").textContent).toBeTruthy();
 if(error_code==="container_toolchain_unavailable")expect(screen.getByRole("status").textContent).toContain("工具链不完整或版本不匹配");
 expect(screen.queryByText("正在等待执行结果…")).toBeNull();
});
it("does not describe unknown as awaiting execution",async()=>{
 vi.stubGlobal("fetch",vi.fn(async(url:string)=>url.includes("/events")?new Response("",{headers:{"Content-Type":"text/event-stream"}}):new Response(JSON.stringify({code:0,data:{id:"t",status:"unknown"}}))));
 render(<TurnActivity turnId="t" onTrace={()=>{}}/>);
 expect(await screen.findByText(/结果待确认/)).toBeTruthy();
 expect(screen.queryByText("正在等待执行结果…")).toBeNull();
});
