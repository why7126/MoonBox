import type { AdminSession } from "../admin/adminAuth";
import { ADMIN_SESSION_EVENT } from "../admin/adminAuth";

export type FrontendSession = {
  username: string;
  started_at: string;
  access_token?: string;
  expires_at?: string;
  user?: AdminSession["user"];
};

const STORAGE_KEY = "moonbox.session";

function isExpired(expiresAt?: string) {
  if (!expiresAt) return false;
  const expires = Date.parse(expiresAt);
  return Number.isFinite(expires) && expires <= Date.now();
}

export function readFrontendSession(): FrontendSession | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as FrontendSession) : null;
  } catch {
    return null;
  }
}

export function readValidFrontendSession(): FrontendSession | null {
  const session = readFrontendSession();
  if (isExpired(session?.expires_at)) {
    clearFrontendSession();
    return null;
  }
  return session;
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
  window.dispatchEvent(new CustomEvent(ADMIN_SESSION_EVENT, { detail: null }));
}

export function redirectToFrontendLogin() {
  clearFrontendSession();
  if (window.location.pathname !== "/login") {
    window.history.replaceState(null, "", "/login");
  }
  window.dispatchEvent(new PopStateEvent("popstate"));
}
