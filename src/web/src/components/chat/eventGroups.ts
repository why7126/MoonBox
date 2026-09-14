import type { ChatEvent } from "./chatEvents";
export type EventGroup = ChatEvent & { endSequence: number };
const fields = (event: ChatEvent): Record<string, unknown> => event.payload && typeof event.payload === "object" ? event.payload as Record<string, unknown> : {};
/** Group display only: persisted events and replay cursors remain unchanged. */
export function groupChatEvents(events: ChatEvent[]): EventGroup[] {
  const groups: EventGroup[] = [];
  for (const event of [...new Map(events.map(e => [e.sequence, e])).values()].sort((a, b) => a.sequence - b.sequence)) {
    const last = groups[groups.length - 1], next = fields(event);
    const previous = last ? fields(last) : {};
    if (last && event.type === "execution.output" && last.type === event.type && event.sequence === last.endSequence + 1
      && previous.item_id === next.item_id && previous.executor_turn_id === next.executor_turn_id) {
      last.payload = { ...previous, text: String(previous.text ?? "") + String(next.text ?? "") };
      last.endSequence = event.sequence;
    } else groups.push({ ...event, payload: { ...next }, endSequence: event.sequence });
  }
  return groups;
}
