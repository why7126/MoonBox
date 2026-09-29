import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it } from "vitest";
import { traceNodes, TrajectoryView } from "./components/chat/TrajectoryView";
import type { ChatEvent } from "./components/chat/chatEvents";
afterEach(cleanup);
const events: ChatEvent[] = [
 {sequence:1,type:"execution.tool",payload:{item_id:"a",executor_turn_id:"t",phase:"started",arguments:{command:"echo hi"},detail_version:1}},
 {sequence:2,type:"execution.output",payload:{text:"进行检查"}},
 {sequence:3,type:"execution.tool",payload:{item_id:"a",executor_turn_id:"t",phase:"completed",status:"failed",result:"<img src=x>",exit_code:1,duration_ms:50}},
 {sequence:4,type:"execution.tool",payload:{item_id:"a",executor_turn_id:"other",phase:"started"}},
];
it("pairs interleaved tools by executor identity without mutating history", () => {
 const original=JSON.stringify(events), rows=traceNodes(events);
 expect(rows).toHaveLength(3);expect(rows[0].payload.arguments).toEqual({command:"echo hi"});expect(rows[0].payload.status).toBe("failed");expect(JSON.stringify(events)).toBe(original);
});
it("searches detail fields and renders output as inert text", () => {
 render(<TrajectoryView events={events}/>);
 expect(document.querySelector(".trace-wrap")).not.toBeNull();
 expect(document.querySelector(".scrub")).not.toBeNull();
 fireEvent.change(screen.getByLabelText("搜索轨迹"),{target:{value:"echo hi"}});
 expect(screen.getAllByRole("listitem")).toHaveLength(1);
 expect(screen.getAllByRole("listitem")[0].className).toContain("event-row");
 fireEvent.click(screen.getByLabelText("查看事件 1 详情"));
 fireEvent.click(screen.getByRole("tab",{name:"结果"}));
 expect(screen.getByText("<img src=x>")).toBeTruthy();expect(document.querySelector("img")).toBeNull();
 expect(screen.getByText("退出码：1")).toBeTruthy();
 fireEvent.click(screen.getByRole("tab",{name:"计时"}));expect(screen.getByText("耗时：50 ms")).toBeTruthy();
});
it("does not invent details for legacy events",()=>{
 render(<TrajectoryView events={[events[3]]}/>);fireEvent.click(screen.getByLabelText("查看事件 4 详情"));expect(screen.getByText("历史记录未采集工具详情。")).toBeTruthy();
 fireEvent.click(screen.getByRole("tab",{name:"参数"}));expect(screen.getByText("未采集参数")).toBeTruthy();
});
