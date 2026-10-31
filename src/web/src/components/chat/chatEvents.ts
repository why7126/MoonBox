import { sharedChatRead } from "./sharedChatRead";
import { readValidFrontendSession, redirectToFrontendLogin } from "../../pages/home/frontendSession";
import { ChatApiError, normalizeChatError } from "./chatApi";
export type ChatEvent = { sequence: number; type: string; payload: unknown };
/** Server emits finite replay pages. Every reconnect is authorized and resumes after a persisted cursor. */
async function fetchChatEvents(turnId: string, after: number, signal?: AbortSignal): Promise<ChatEvent[]> {
  const token = readValidFrontendSession()?.access_token;
  if (!token) {
    redirectToFrontendLogin();
    throw new ChatApiError(401, "登录已失效，请重新登录");
  }
  let response: Response;
  try {
    response = await fetch(`/api/v1/chat/turns/${encodeURIComponent(turnId)}/events?after=${after}`, { headers: { Authorization: `Bearer ${token}`, Accept: "text/event-stream" }, signal, cache: "no-store" });
  } catch (error) {
    throw normalizeChatError(error, "执行轨迹连接暂时中断，请稍后重试");
  }
  if (!response.ok) {
    if (response.status === 401) {
      redirectToFrontendLogin();
      throw new ChatApiError(401, "登录已失效，请重新登录");
    }
    throw new ChatApiError(response.status, response.status === 403 || response.status === 404 ? "执行记录已不可访问" : "事件读取失败，请重新连接");
  }
  if (!response.headers.get("Content-Type")?.startsWith("text/event-stream")) throw new ChatApiError(502, "执行事件响应格式异常，请重新连接");
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

export function readChatEvents(turnId: string, after: number, signal?: AbortSignal): Promise<ChatEvent[]> {
 return sharedChatRead(`events:${turnId}:${after}`, inner => fetchChatEvents(turnId, after, inner), signal);
}
