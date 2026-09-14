import { readFrontendSession } from "../../pages/home/frontendSession";
import { ChatApiError } from "./chatApi";
export type ChatEvent = { sequence: number; type: string; payload: unknown };
/** Server emits finite replay pages. Every reconnect is authorized and resumes after a persisted cursor. */
export async function readChatEvents(turnId: string, after: number, signal?: AbortSignal): Promise<ChatEvent[]> {
  const token = readFrontendSession()?.access_token;
  if (!token) throw new ChatApiError(401, "登录已失效，请重新登录");
  const response = await fetch(`/api/v1/chat/turns/${encodeURIComponent(turnId)}/events?after=${after}`, { headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" }, signal, cache: "no-store" });
  if (!response.ok) throw new ChatApiError(response.status, response.status === 401 ? "登录已失效，请重新登录" : response.status === 403 || response.status === 404 ? "执行记录已不可访问" : "事件读取失败，请重新连接");
  if (!response.headers.get("Content-Type")?.startsWith("text/event-stream")) throw new Error("事件响应格式异常");
  const result: ChatEvent[] = [];
  for (const block of (await response.text()).replace(/\r\n/g, "\n").split("\n\n")) {
    let sequence = 0, type = "", data = "";
    for (const line of block.split("\n")) {
      if (line.startsWith("id:")) sequence = Number(line.slice(3).trim());
      if (line.startsWith("event:")) type = line.slice(6).trim();
      if (line.startsWith("data:")) data += line.slice(5).trimStart() + "\n";
    }
    if (Number.isSafeInteger(sequence) && sequence > after && type && data) result.push({ sequence, type, payload: JSON.parse(data) });
  }
  return [...new Map(result.map(event => [event.sequence, event])).values()].sort((a, b) => a.sequence - b.sequence);
}
