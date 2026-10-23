import { useEffect, useRef, useState } from "react";
import type { MessageRead } from "../../api/generated/chat";
import { ChatApiError, chatRequest, normalizeChatError } from "./chatApi";

// Optional fields allow a clear compatibility state during a rolling deployment.
export type OrderedMessage = Pick<MessageRead, "id" | "role" | "content" | "created_at"> &
  Partial<Pick<MessageRead, "turn_id" | "order_key" | "display_time" | "time_source" | "output_partial" | "output_truncated" | "output_source">>;
type Page<T> = { items: T[]; next_cursor?: string | null; has_more?: boolean };
const compare = (a: string, b: string) => a < b ? -1 : a > b ? 1 : 0;
export function compareMessages(a: OrderedMessage, b: OrderedMessage) {
  if (a.order_key && b.order_key) {
    const x = a.order_key, y = b.order_key;
    return compare(x.turn_created_at, y.turn_created_at) || compare(x.turn_id, y.turn_id) ||
      x.role_rank - y.role_rank || compare(x.message_id, y.message_id);
  }
  // Legacy servers do not supply enough information for the full contract.
  return compare(a.created_at, b.created_at) || compare(a.id, b.id);
}
export function messageTime(row: OrderedMessage) {
  if (row.time_source === "legacy_unknown") return "历史回复时间未确认";
  const value = row.display_time ?? row.created_at;
  return `${row.time_source === "output_event" ? "输出记录于 " : ""}${new Date(value).toLocaleString()}`;
}

export function useConversationMessages<T extends OrderedMessage>(conversationId: string, beforeOlder: () => (() => void)) {
  const [state, setState] = useState({ cid: conversationId, rows: [] as T[], more: true, loading: true, error: "", compatibility: false });
  const olderRequested = useRef(false);
  const wake = useRef(() => {});
  const beforeOlderRef = useRef(beforeOlder); beforeOlderRef.current = beforeOlder;
  useEffect(() => {
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    let rows: T[] = [], cursor: string | null = null, legacyPage = 1, modern = false;
    let initialized = false, lastScan = 0, lastHead = 0, headFingerprint = "", running = false;
    let scan: { cursor: string; boundary: T } | null = null;
    olderRequested.current = false;
    setState({ cid: conversationId, rows, more: true, loading: true, error: "", compatibility: false });
    const merge = (items: T[]) => {
      rows = [...new Map([...rows, ...items].map(row => [row.id, row])).values()].sort(compareMessages);
    };
    const get = (before: string | null, page = 1) => chatRequest<Page<T>>(
      `/conversations/${conversationId}/messages?${before ? `before=${encodeURIComponent(before)}` : `page=${page}`}`,
      { signal: controller.signal });
    const tick = async () => {
      if (running || controller.signal.aborted) return;
      running = true;
      let delay = 3000;
      try {
        // A single request lane prevents old pages from overwriting newer data.
        // Deep scans continue one bounded page at a time; polling never cancels them.
        if (scan && Date.now() - lastHead >= 3000) {
          const data = await get(null);
          if (controller.signal.aborted) return;
          merge(data.items); lastHead = Date.now(); headFingerprint = JSON.stringify(data);
          delay = 250;
        } else if (scan) {
          const current = scan;
          const data = await get(current.cursor);
          if (controller.signal.aborted) return;
          merge(data.items);
          const tail = data.items[data.items.length - 1];
          if (!data.has_more || !data.next_cursor || (tail && compareMessages(tail, current.boundary) <= 0)) {
            cursor = data.next_cursor ?? null; scan = null; lastScan = Date.now();
            setState(s => ({ ...s, more: !!data.has_more }));
          } else {
            if (data.next_cursor === current.cursor) throw new Error("消息分页暂未推进，请稍后重试");
            scan = { ...current, cursor: data.next_cursor };
          }
          delay = scan ? 250 : 3000;
        } else if (olderRequested.current && initialized) {
          olderRequested.current = false;
          const restore = beforeOlderRef.current();
          const data = await get(modern ? cursor : null, modern ? 1 : legacyPage + 1);
          if (controller.signal.aborted) return;
          merge(data.items); cursor = data.next_cursor ?? null; legacyPage++;
          setState(s => ({ ...s, more: modern ? !!data.has_more : data.items.length === 20 }));
          requestAnimationFrame(() => { if (!controller.signal.aborted) restore(); });
        } else {
          const boundary = rows[0];
          const data = await get(null);
          if (controller.signal.aborted) return;
          modern = typeof data.has_more === "boolean" && data.items.every(row => !!row.order_key);
          const fingerprint = JSON.stringify(data);
          merge(data.items);
          if (!initialized) {
            cursor = data.next_cursor ?? null; initialized = true;
            setState(s => ({ ...s, more: modern ? !!data.has_more : data.items.length === 20 }));
          }
          const tail = data.items[data.items.length - 1];
          if (modern && boundary && data.has_more && data.next_cursor && tail && compareMessages(tail, boundary) > 0 &&
              (fingerprint !== headFingerprint || Date.now() - lastScan >= 15000)) {
            scan = { cursor: data.next_cursor, boundary }; delay = 250;
          } else if (modern && (!boundary || !tail || compareMessages(tail, boundary) <= 0)) {
            cursor = data.next_cursor ?? null;
            setState(s => ({ ...s, more: !!data.has_more }));
          }
          headFingerprint = fingerprint; lastHead = Date.now();
        }
        setState(s => ({ ...s, rows, loading: olderRequested.current, error: "", compatibility: !modern }));
      } catch (error) {
        if (controller.signal.aborted) return;
        const normalized = normalizeChatError(error, "消息暂不可读，请稍后重试");
        const denied = normalized instanceof ChatApiError && [401, 403, 404].includes(normalized.status);
        if (denied) { rows = []; scan = null; }
        setState(s => ({ ...s, rows, loading: false, error: denied ? "会话暂不可访问" : "消息暂不可读，请稍后重试" }));
      } finally { running = false; }
      if (!controller.signal.aborted) timer = setTimeout(tick, delay);
    };
    wake.current = () => { if (!running) { clearTimeout(timer); void tick(); } };
    void tick();
    return () => { controller.abort(); clearTimeout(timer); };
  }, [conversationId]);
  const visible = state.cid === conversationId ? state : { ...state, rows: [] as T[], loading: true, error: "" };
  return { ...visible, loadOlder: () => { olderRequested.current = true; setState(s => ({ ...s, loading: true })); wake.current(); } };
}
