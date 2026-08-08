export type AdminSession = {
  access_token: string;
  expires_at: string;
  user: {
    id: string;
    username: string;
    role: string;
    status: string;
    is_system_superadmin: boolean;
  };
};

const STORAGE_KEY = "moonbox.admin.session";

function apiUrl(path: string) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
  return `${baseUrl}${path}`;
}

export function readAdminSession(): AdminSession | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AdminSession) : null;
  } catch {
    return null;
  }
}

export function saveAdminSession(session: AdminSession) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function clearAdminSession() {
  window.localStorage.removeItem(STORAGE_KEY);
}

async function readAuthError(response: Response) {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || "登录失败，请稍后重试。";
  } catch {
    return "登录失败，请稍后重试。";
  }
}

export async function loginAdmin(username: string, password: string): Promise<AdminSession> {
  const response = await fetch(apiUrl("/api/v1/admin/auth/login"), {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username, password, remember_me: false }),
  });
  if (!response.ok) {
    throw new Error(await readAuthError(response));
  }
  const payload = await response.json();
  const session = payload.data as AdminSession;
  saveAdminSession(session);
  return session;
}

export async function logoutAdmin() {
  const session = readAdminSession();
  clearAdminSession();
  if (!session?.access_token) return;
  await fetch(apiUrl("/api/v1/admin/auth/logout"), {
    method: "POST",
    headers: { authorization: `Bearer ${session.access_token}` },
  }).catch(() => undefined);
}
