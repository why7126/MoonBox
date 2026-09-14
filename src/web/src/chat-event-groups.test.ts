import { expect, it } from "vitest";
import { groupChatEvents } from "./components/chat/eventGroups";
import type { ChatEvent } from "./components/chat/chatEvents";
const output = (sequence: number, text: string, item_id: string | null = "a"): ChatEvent => ({ sequence, type: "execution.output", payload: { text, item_id, executor_turn_id: "turn" } });
it("reassembles streaming batches without duplicating replays or mutating input", () => {
 const first = [output(1, "我"), output(2, "先")];
 expect(groupChatEvents(first)[0].payload).toMatchObject({text:"我先"});
 const merged = groupChatEvents([...first, output(2,"先"),output(3,"查看")]);
 expect(merged).toHaveLength(1); expect(merged[0]).toMatchObject({sequence:1,endSequence:3,payload:{text:"我先查看"}});
 expect(first[0].payload).toMatchObject({text:"我"});
});
it("preserves item, tool, state and missing-sequence boundaries", () => {
 const events = [output(1,"a"),output(2,"b","b"),{sequence:3,type:"execution.tool",payload:{}},output(4,"c","b"),{sequence:5,type:"execution.state",payload:{status:"completed"}},output(7,"d","b"),output(9,"e","b")];
 expect(groupChatEvents(events)).toHaveLength(7);
});
it("handles legacy identity-free output and empty streams", () => {
 expect(groupChatEvents([])).toEqual([]);
 expect(groupChatEvents([output(1,"a",null),output(2,"b",null)])[0].payload).toMatchObject({text:"ab"});
});
