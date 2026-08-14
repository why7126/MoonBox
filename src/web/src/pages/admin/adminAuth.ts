export type AdminSession = {
  access_token: string;
  expires_at: string;
  user: {
    id: string;
    username: string;
    nickname?: string | null;
    avatar_url?: string | null;
    role: string;
    status: string;
    is_system_superadmin: boolean;
  };
};

const STORAGE_KEY = "moonbox.session";
export const ADMIN_SESSION_EVENT = "moonbox.session.changed";

export function canAccessAdmin(user: AdminSession["user"] | null | undefined) {
  return user?.role === "后台管理员";
}

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
  window.dispatchEvent(new CustomEvent(ADMIN_SESSION_EVENT, { detail: session }));
}

export function clearAdminSession() {
  window.localStorage.removeItem(STORAGE_KEY);
  window.dispatchEvent(new CustomEvent(ADMIN_SESSION_EVENT, { detail: null }));
}

async function readAuthError(response: Response, fallback = "登录失败，请稍后重试。") {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || fallback;
  } catch {
    return fallback;
  }
}

export async function loginAdmin(username: string, password: string): Promise<AdminSession> {
  const response = await fetch(apiUrl("/api/v1/auth/login"), {
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
  await fetch(apiUrl("/api/v1/auth/logout"), {
    method: "POST",
    headers: { authorization: `Bearer ${session.access_token}` },
  }).catch(() => undefined);
}

export async function changeAdminPassword(currentPassword: string, newPassword: string, confirmPassword: string) {
  const session = readAdminSession();
  const accessToken = session?.access_token;
  if (!accessToken) {
    throw new Error("登录已失效，请重新登录");
  }
  const response = await fetch(apiUrl("/api/v1/auth/change-password"), {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    }),
  });
  if (!response.ok) {
    throw new Error(await readAuthError(response, "密码修改失败，请稍后重试。"));
  }
  clearAdminSession();
  return response.json();
}

export async function updateAdminProfile(nickname: string | null, avatarUrl: string | null): Promise<AdminSession["user"]> {
  const session = readAdminSession();
  if (!session?.access_token) {
    throw new Error("登录已失效，请重新登录");
  }
  const response = await fetch(apiUrl("/api/v1/auth/me"), {
    method: "PATCH",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${session.access_token}`,
    },
    body: JSON.stringify({ nickname, avatar_url: avatarUrl }),
  });
  if (!response.ok) {
    throw new Error(await readAuthError(response, "个人资料保存失败，请稍后重试。"));
  }
  const payload = await response.json();
  const nextUser = payload.data.user as AdminSession["user"];
  saveAdminSession({ ...session, user: nextUser });
  return nextUser;
}
