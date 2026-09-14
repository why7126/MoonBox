import { readFrontendSession } from "../../pages/home/frontendSession";
import type { ConversationRead, ConversationPage, TurnRead } from "../../api/generated/chat";
export type { ConversationRead, TurnRead };
export type Capabilities = { execution_ready: boolean; reason: string; repositories: { id: string; space_id: string }[] };
export type Space = { id: string; name: string };
export class ChatApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export async function chatRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = readFrontendSession()?.access_token;
  if (!token) throw new ChatApiError(401, "登录已失效，请重新登录");
  const response = await fetch(`/api/v1/chat${path}`, { ...options, headers: { "Content-Type": "application/json", ...options.headers, "X-Chat-Client": "web", Authorization: `Bearer ${token}` }, cache: "no-store" });
  const body = await response.json().catch(() => null);
  if (!response.ok || body?.code !== 0) throw new ChatApiError(response.status, response.status === 401 ? "登录已失效，请重新登录" : response.status === 403 ? "无权访问当前空间或会话，请切换空间" : body?.message || "请求失败，请稍后重试");
  return body.data as T;
}
export const listSessions = (space: string, query: string, archived: boolean | "all" | "pinned", page: number, signal?: AbortSignal) => chatRequest<ConversationPage>(`/conversations?${new URLSearchParams({ space_id: space, q: query, archived: String(archived === true), ...(typeof archived === "string" ? { filter: archived } : {}), page: String(page), page_size: "20" })}`, { signal });
export const patchSession = (id: string, patch: { title?: string; pinned?: boolean; archived?: boolean }) => chatRequest<ConversationRead>(`/conversations/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(patch) });
