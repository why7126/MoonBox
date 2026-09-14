import { readAccessToken } from "./workbenchAccount";
export type Project = { space_id: string; repository_id: string; status: "connected" | "unavailable"; readonly: boolean };
export type Application = { id: string; state: string; phase: string; error_code?: string };
export class GovernanceError extends Error {
  constructor(message: string, public status: number, public code?: number, public kind?: string, public requestId?: string) { super(message); }
}
export async function governanceRequest<T>(url: string, options: RequestInit = {}): Promise<T> {
  const token = readAccessToken();
  const response = await fetch(url, { ...options, headers: { accept: "application/json", "content-type": "application/json", "X-Chat-Client": "web", ...(token ? { authorization: `Bearer ${token}` } : {}), ...options.headers } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new GovernanceError(typeof body.message === "string" ? body.message : typeof body.detail === "string" ? body.detail : `项目请求失败（${response.status}）`, response.status, typeof body.code === "number" ? body.code : undefined, typeof body.data?.kind === "string" ? body.data.kind : undefined, response.headers?.get("X-Request-ID") || body.data?.request_id);
  return body.data;
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
