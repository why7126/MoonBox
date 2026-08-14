import type { AdminSession } from "../admin/adminAuth";

export type FrontendSession = {
  username: string;
  started_at: string;
  access_token?: string;
  expires_at?: string;
  user?: AdminSession["user"];
};

const STORAGE_KEY = "moonbox.session";

export function readFrontendSession(): FrontendSession | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as FrontendSession) : null;
  } catch {
    return null;
  }
}

export function saveFrontendSession(sessionOrUsername: AdminSession | string) {
  const username = typeof sessionOrUsername === "string" ? sessionOrUsername : sessionOrUsername.user.nickname || sessionOrUsername.user.username;
  if (typeof sessionOrUsername !== "string") {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(sessionOrUsername));
    return;
  }
  window.localStorage.setItem(
    STORAGE_KEY,
    JSON.stringify({
      username,
      started_at: new Date().toISOString(),
    }),
  );
}

export function clearFrontendSession() {
  window.localStorage.removeItem(STORAGE_KEY);
}
