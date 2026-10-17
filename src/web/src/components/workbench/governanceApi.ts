import { readAccessToken } from "./workbenchAccount";
import { isAbortError } from "../chat/chatApi";
export type Project = { space_id: string; repository_id: string; status: "connected" | "unavailable"; readonly: boolean };
export type Application = { id: string; state: string; phase: string; error_code?: string };
export type GovernanceErrorDetails = { reason?: string; roots?: string[]; categories?: string[]; suggested_action?: string; dirty_count?: number };
export class GovernanceError extends Error {
  constructor(message: string, public status: number, public code?: number, public kind?: string, public requestId?: string, public details?: GovernanceErrorDetails) { super(message); }
}
function normalizeGovernanceError(error: unknown, fallback = "项目连接暂不可用，请稍后重试") {
  if (isAbortError(error) || error instanceof GovernanceError) return error;
  const message = error instanceof Error ? error.message : "";
  if (/NetworkError|Failed to fetch|Load failed|network/i.test(message)) return new GovernanceError(fallback, 0, undefined, "network_unavailable");
  return new GovernanceError(message || fallback, 0, undefined, "request_failed");
}
export async function governanceRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = readAccessToken();
  let response: Response;
  try {
    response = await fetch(url, { ...options, headers: { accept: "application/json", "content-type": "application/json", "X-Chat-Client": "web", ...(token ? { authorization: `Bearer ${token}` } : {}), ...options.headers } });
  } catch (error) {
    throw normalizeGovernanceError(error);
  }
  const body = await response.json().catch(() => ({}));
  const data = body && typeof body.data === "object" ? body.data : undefined;
  const details = data ? {
    reason: typeof data.reason === "string" ? data.reason : undefined,
    roots: Array.isArray(data.roots) ? data.roots.filter((item: unknown) => typeof item === "string") : undefined,
    categories: Array.isArray(data.categories) ? data.categories.filter((item: unknown) => typeof item === "string") : undefined,
    suggested_action: typeof data.suggested_action === "string" ? data.suggested_action : undefined,
    dirty_count: typeof data.dirty_count === "number" ? data.dirty_count : undefined,
  } : undefined;
  if (!response.ok) throw new GovernanceError(typeof body.message === "string" ? body.message : typeof body.detail === "string" ? body.detail : `项目请求失败（${response.status}）`, response.status, typeof body.code === "number" ? body.code : undefined, typeof data?.kind === "string" ? data.kind : undefined, response.headers?.get("X-Request-ID") || data?.request_id, details);
  return body.data;
}
export async function governanceTextRequest(url: string, options: RequestInit = {}): Promise<string> {
  const token = readAccessToken();
  let response: Response;
  try {
    response = await fetch(url, { ...options, headers: { accept: "text/html, text/plain;q=0.9, */*;q=0.8", "X-Chat-Client": "web", ...(token ? { authorization: `Bearer ${token}` } : {}), ...options.headers } });
  } catch (error) {
    throw normalizeGovernanceError(error, "项目文档连接暂不可用，请稍后重试");
  }
  if (!response.ok) {
    const body = await response.clone().json().catch(() => ({}));
    const data = body && typeof body.data === "object" ? body.data : undefined;
    const details = data ? {
      reason: typeof data.reason === "string" ? data.reason : undefined,
      roots: Array.isArray(data.roots) ? data.roots.filter((item: unknown) => typeof item === "string") : undefined,
      categories: Array.isArray(data.categories) ? data.categories.filter((item: unknown) => typeof item === "string") : undefined,
      suggested_action: typeof data.suggested_action === "string" ? data.suggested_action : undefined,
      dirty_count: typeof data.dirty_count === "number" ? data.dirty_count : undefined,
    } : undefined;
    throw new GovernanceError(typeof body.message === "string" ? body.message : typeof body.detail === "string" ? body.detail : `项目请求失败（${response.status}）`, response.status, typeof body.code === "number" ? body.code : undefined, typeof data?.kind === "string" ? data.kind : undefined, response.headers?.get("X-Request-ID") || data?.request_id, details);
  }
  return response.text();
}
export function scopedUrl(url: string, project: Project, suffix = "") {
  const parsed = new URL(url, window.location.origin);
  if (parsed.origin !== window.location.origin || !parsed.pathname.startsWith("/api/v1/requirement-center/")) throw new Error("文档地址无效");
  parsed.pathname += suffix;
  parsed.searchParams.set("space_id", project.space_id); parsed.searchParams.set("repository_id", project.repository_id);
  return parsed.pathname + parsed.search;
}
export async function waitApplication(id: string, signal?: AbortSignal): Promise<Application> {
  for (;;) {
    const row = await governanceRequest<Application>(`/api/v1/chat/governance-applications/${encodeURIComponent(id)}`, { signal });
    if (!["pending", "applying", "recovering"].includes(row.state)) return row;
    await new Promise<void>((resolve, reject) => {
      const abort = () => { clearTimeout(timer); reject(new DOMException("Aborted", "AbortError")); };
      const timer = setTimeout(() => { signal?.removeEventListener("abort", abort); resolve(); }, 1000);
      if (signal?.aborted) abort(); else signal?.addEventListener("abort", abort, { once: true });
    });
  }
}
