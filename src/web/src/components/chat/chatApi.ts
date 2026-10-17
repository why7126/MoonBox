import { readValidFrontendSession, redirectToFrontendLogin } from "../../pages/home/frontendSession";
import type { ConversationRead as GeneratedConversationRead, ConversationPage, TurnRead as GeneratedTurnRead } from "../../api/generated/chat";
export type ConversationRead = GeneratedConversationRead & { write_scope?: string; write_reason_code?: string };
export type ExecutionConfig = { agent: string; model: string; reasoning: string };
export type ExecutionOption = { value: string; display_name: string; available: boolean; disabled_reason?: string | null };
export type ExecutionCapabilities = { policy_version: string; agents: ExecutionOption[]; models: ExecutionOption[]; reasoning: ExecutionOption[]; defaults: ExecutionConfig };
export type TurnRead = GeneratedTurnRead & { requested_config?: ExecutionConfig; effective_config?: ExecutionConfig; config_fallback_reason?: string | null };
export type MaterialLimits = { max_images: number; max_image_bytes: number; max_total_image_bytes: number; allowed_image_mime_types: string[]; max_files?: number; max_file_bytes?: number; max_total_file_bytes?: number; allowed_file_mime_types?: string[]; max_skills: number; max_skill_summary_chars: number; max_prompt_chars: number };
export type MaterialRef = { kind?: "image" | "file" | "skill"; name: string; summary?: string; mime_type?: string | null; size_bytes?: number; ref_id?: string | null; metadata?: Record<string, string> };
export type SkillCandidate = { id: string; name: string; summary: string; source: string; digest: string; injection_scope: string };
export type BranchCatalog = { items: { name: string; is_default?: boolean }[]; default: string; source?: string };
export type ChatRepository = { id: string; space_id: string; branches?: BranchCatalog };
export type UploadedMaterial = { ref_id: string; kind: "image" | "file"; name: string; mime_type: string; size_bytes: number; status: string };
export type Capabilities = { execution_ready: boolean; reason: string; reason_code?: string; repositories: ChatRepository[]; materials?: MaterialLimits; execution?: ExecutionCapabilities };
export type Space = { id: string; name: string };
export class ChatApiError extends Error { constructor(public status: number, message: string) { super(message); } }
export function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}
export function normalizeChatError(error: unknown, fallback = "工作台连接暂时中断，请检查服务状态后重试") {
  if (isAbortError(error) || error instanceof ChatApiError) return error;
  const message = error instanceof Error ? error.message : "";
  if (/NetworkError|Failed to fetch|Load failed|network/i.test(message)) return new ChatApiError(0, fallback);
  return new Error(message || fallback);
}
function authError(message = "登录已失效，请重新登录") {
  redirectToFrontendLogin();
  return new ChatApiError(401, message);
}
function chatStatusError(response: Response, body: any, fallback: string) {
  if (response.status === 401) return authError();
  return new ChatApiError(response.status, response.status === 403 ? (body?.code === 2509 ? "关联对象不可访问，请检查对象状态或权限" : "无权访问当前空间或会话，请切换空间") : body?.message || fallback);
}
export async function chatRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = readValidFrontendSession()?.access_token;
  if (!token) throw authError();
  let response: Response;
  try {
    response = await fetch(`/api/v1/chat${path}`, { ...options, headers: { "Content-Type": "application/json", ...options.headers, "X-Chat-Client": "web", Authorization: `Bearer ${token}` }, cache: "no-store" });
  } catch (error) {
    throw normalizeChatError(error);
  }
  const body = await response.json().catch(() => null);
  if (!response.ok || body?.code !== 0) throw chatStatusError(response, body, "请求失败，请稍后重试");
  return body.data as T;
}
export async function uploadChatMaterial(spaceId: string, repositoryId: string, file: File): Promise<UploadedMaterial> {
  const token = readValidFrontendSession()?.access_token;
  if (!token) throw authError();
  const form = new FormData();
  form.append("file", file);
  const query = new URLSearchParams({ space_id: spaceId, repository_id: repositoryId });
  let response: Response;
  try {
    response = await fetch(`/api/v1/chat/materials?${query}`, { method: "POST", body: form, headers: { "X-Chat-Client": "web", Authorization: `Bearer ${token}` }, cache: "no-store" });
  } catch (error) {
    throw normalizeChatError(error, "材料上传连接暂时中断，请稍后重试");
  }
  const body = await response.json().catch(() => null);
  if (!response.ok || body?.code !== 0) throw chatStatusError(response, body, "上传失败，请稍后重试");
  return body.data as UploadedMaterial;
}
export async function fetchChatMaterialBlob(path: string, signal?: AbortSignal): Promise<Blob> {
  const token = readValidFrontendSession()?.access_token;
  if (!token) throw authError();
  let response: Response;
  try {
    response = await fetch(path, { headers: { "X-Chat-Client": "web", Authorization: `Bearer ${token}` }, signal, cache: "no-store" });
  } catch (error) {
    throw normalizeChatError(error, "材料读取连接暂时中断，请稍后重试");
  }
  if (!response.ok) {
    if (response.status === 401) throw authError();
    throw new ChatApiError(response.status, response.status === 403 ? "无权访问当前材料" : "读取材料失败，请稍后重试");
  }
  return response.blob();
}
export const listSessions = (space: string, query: string, archived: boolean | "all" | "pinned", page: number, signal?: AbortSignal) => chatRequest<ConversationPage>(`/conversations?${new URLSearchParams({ space_id: space, q: query, archived: String(archived === true), ...(typeof archived === "string" ? { filter: archived } : {}), page: String(page), page_size: "20" })}`, { signal });
export const patchSession = (id: string, patch: { title?: string; pinned?: boolean; archived?: boolean }) => chatRequest<ConversationRead>(`/conversations/${encodeURIComponent(id)}`, { method: "PATCH", body: JSON.stringify(patch) });
