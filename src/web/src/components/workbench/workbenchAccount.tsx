import { Calendar,ChevronLeft,ChevronRight,X } from "lucide-react";
import { ChangeEvent,FormEvent,useEffect,useRef,useState } from "react";
import { createPortal } from "react-dom";
import type { AdminSession } from "../../pages/admin/adminAuth";
import { canAccessAdmin,readAdminSession,updateAdminProfile } from "../../pages/admin/adminAuth";
import { readFrontendSession } from "../../pages/home/frontendSession";
type ProfileUploadState = "idle" | "uploading" | "done" | "failed";
export type Workspace = {
  organizationName: string;
  workspaceId: string;
  name: string;
  slug: string;
  description: string;
  timezone: string;
  memberCount: number;
  role: string;
  status?: string;
  readonly?: boolean;
};

export type FrontendUser = {
  name: string;
  avatarInitial: string;
  avatarUrl?: string | null;
  canAccessAdmin: boolean;
  permissions: string[];
};

export const emptyWorkspace: Workspace = {
  organizationName: "MoonBox",
  workspaceId: "",
  name: "暂无空间",
  slug: "",
  description: "",
  timezone: "Asia/Shanghai",
  memberCount: 0,
  role: "只读",
  readonly: true,
};

export const emptyUser: FrontendUser = {
  name: "未登录",
  avatarInitial: "未",
  avatarUrl: null,
  canAccessAdmin: false,
  permissions: [],
};

export function getStoredWorkspace(workspaces: Workspace[], selectedWorkspaceId?: string) {
  try {
    const raw = window.localStorage.getItem("moonbox.workspace");
    const fallback = workspaces.find((workspace) => workspace.workspaceId === selectedWorkspaceId) || workspaces[0] || emptyWorkspace;
    if (!workspaces.length) {
      window.localStorage.removeItem("moonbox.workspace");
      return emptyWorkspace;
    }
    if (!raw) {
      window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
      return fallback;
    }
    const stored = JSON.parse(raw) as Partial<Workspace>;
    const matched = workspaces.find((workspace) => workspace.workspaceId === stored.workspaceId);
    if (matched) return matched;
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
    return fallback;
  } catch {
    const fallback = workspaces[0] || emptyWorkspace;
    if (workspaces.length) window.localStorage.setItem("moonbox.workspace", JSON.stringify(fallback));
    return fallback;
  }
}

const apiBase = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

const apiUrl = (path: string) => `${apiBase}${path}`;

const avatarImageSrc = (avatarUrl: string | null | undefined) => {
  const url = avatarUrl?.trim();
  if (!url) return null;
  if (/^(https?:|blob:|data:)/i.test(url)) return url;
  return url.startsWith("/") ? apiUrl(url) : url;
};

const authenticatedAvatarCache = new Map<string, Promise<string>>();

const readAuthenticatedAvatar = async (source: string, token: string) => {
  const cached = authenticatedAvatarCache.get(source);
  if (cached) return cached;
  const pending = fetch(source, { headers: { authorization: `Bearer ${token}` } })
    .then((response) => {
      if (!response.ok) throw new Error("头像读取失败");
      return response.blob();
    })
    .then((blob) => URL.createObjectURL(blob))
    .catch((error) => {
      authenticatedAvatarCache.delete(source);
      throw error;
    });
  authenticatedAvatarCache.set(source, pending);
  return pending;
};

async function readProfileApiError(response: Response, fallback = "头像上传失败，请重试。") {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || fallback;
  } catch {
    return fallback;
  }
}

export function AuthenticatedRequirementAvatar({
  avatarUrl,
  alt,
  fallback,
}: {
  avatarUrl: string | null | undefined;
  alt: string;
  fallback: string;
}) {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    setObjectUrl(null);
    const source = avatarImageSrc(avatarUrl);
    if (!source) return undefined;
    if (/^(blob:|data:)/i.test(source)) {
      setObjectUrl(source);
      return undefined;
    }
    const session = readFrontendSession();
    const adminSession = readAdminSession();
    const token = session?.access_token || adminSession?.access_token;
    if (!token) return undefined;
    void readAuthenticatedAvatar(source, token)
      .then((nextObjectUrl) => {
        if (isActive) setObjectUrl(nextObjectUrl);
      })
      .catch(() => {
        if (isActive) setObjectUrl(null);
      });
    return () => {
      isActive = false;
    };
  }, [avatarUrl]);

  return <span className="rc-avatar">{objectUrl ? <img src={objectUrl} alt={alt} /> : fallback}</span>;
}

export function frontendUserFromAdmin(user: AdminSession["user"], fallback: FrontendUser): FrontendUser {
  const displayName = (user.nickname || user.username || fallback.name || emptyUser.name).trim();
  return {
    ...fallback,
    name: displayName,
    avatarInitial: avatarInitial(displayName, fallback.avatarInitial),
    avatarUrl: user.avatar_url ?? null,
  };
}

export function avatarInitial(name: string | null | undefined, fallback = emptyUser.avatarInitial) {
  const displayName = name?.trim();
  return displayName ? displayName.slice(0, 2).toUpperCase() : fallback;
}

export const sessionAvatarUrl = (avatarUrl: string | null | undefined) =>
  avatarUrl?.startsWith("/api/v1/admin/users/avatar/") ? null : avatarUrl ?? null;

export function fallbackUserFromSession(): FrontendUser {
  const frontendSession = readFrontendSession();
  const adminSession = readAdminSession();
  const sessionUser = frontendSession?.user || adminSession?.user;
  const displayName = (
    frontendSession?.username ||
    adminSession?.user?.nickname ||
    adminSession?.user?.username ||
    ""
  ).trim();
  if (!displayName) return emptyUser;
  return {
    name: displayName,
    avatarInitial: avatarInitial(displayName),
    avatarUrl: sessionAvatarUrl(sessionUser?.avatar_url),
    canAccessAdmin: canAccessAdmin(sessionUser),
    permissions: ["requirement:read"],
  };
}

export function FrontendProfileModal({
  user,
  onClose,
  onSaved,
}: {
  user: FrontendUser;
  onClose: () => void;
  onSaved: (nextUser: AdminSession["user"]) => void;
}) {
  const frontendSessionUser = readFrontendSession()?.user;
  const adminSessionUser = readAdminSession()?.user;
  const sessionUser = frontendSessionUser || adminSessionUser;
  const username = sessionUser?.username || user.name;
  const [nickname, setNickname] = useState(sessionUser?.nickname ?? user.name);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(user.avatarUrl ?? sessionUser?.avatar_url ?? null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(avatarImageSrc(user.avatarUrl ?? sessionUser?.avatar_url));
  const [uploadState, setUploadState] = useState<ProfileUploadState>("idle");
  const [uploadError, setUploadError] = useState("");
  const [saveError, setSaveError] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const avatarButtonText = uploadState === "uploading" ? "上传中" : avatarUrl ? "更换" : "上传";

  const uploadAvatar = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadState("uploading");
    setUploadError("");
    const session = readAdminSession();
    try {
      if (!session?.access_token) throw new Error("登录已失效，请重新登录");
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(apiUrl("/api/v1/auth/avatar"), {
        method: "POST",
        headers: { authorization: `Bearer ${session.access_token}` },
        body: formData,
      });
      if (!response.ok) throw new Error(await readProfileApiError(response));
      const payload = await response.json();
      const persistentUrl = payload.data.url as string;
      const objectUrl = await readAuthenticatedAvatar(apiUrl(persistentUrl), session.access_token);
      setAvatarUrl(persistentUrl);
      setAvatarPreviewUrl(objectUrl);
      setUploadState("done");
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "头像上传失败，请重试。");
      setUploadState("failed");
    } finally {
      event.target.value = "";
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (isSaving || uploadState === "uploading") return;
    setIsSaving(true);
    setSaveError("");
    try {
      const nextUser = await updateAdminProfile(nickname.trim() || null, avatarUrl);
      onSaved(nextUser);
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : "个人资料保存失败，请重试。");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="rc-profile-mask" role="presentation" onMouseDown={onClose}>
      <form
        className="rc-profile-modal"
        aria-label="个人资料"
        onSubmit={submit}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="rc-profile-head">
          <h2>个人资料</h2>
          <button aria-label="关闭个人资料" type="button" onClick={onClose}>
            <X size={17} />
          </button>
        </header>
        <p className="rc-profile-summary">{username}</p>
        <div className="rc-form-row">
          <label><span>头像</span></label>
          <div className="rc-profile-avatar-picker">
            <AuthenticatedRequirementAvatar avatarUrl={avatarPreviewUrl} alt="头像预览" fallback={avatarInitial(nickname || username || user.name)} />
            <span className="rc-profile-avatar-copy">
              <small>支持 JPG、PNG、WEBP，建议 1:1，最大 2MB</small>
              <button type="button" aria-label="上传或更换头像" disabled={uploadState === "uploading" || isSaving} onClick={() => fileInputRef.current?.click()}>
                {avatarButtonText}
              </button>
            </span>
            <input ref={fileInputRef} className="rc-profile-avatar-file" type="file" accept="image/jpeg,image/png,image/webp" aria-label="选择头像文件" onChange={uploadAvatar} />
          </div>
          {uploadState === "failed" && <div className="rc-profile-error" aria-live="polite">{uploadError}</div>}
        </div>
        <div className="rc-form-row">
          <label htmlFor="rc-profile-nickname">昵称</label>
          <input id="rc-profile-nickname" maxLength={128} value={nickname} onChange={(event) => setNickname(event.target.value)} />
        </div>
        {saveError && <div className="rc-profile-error" aria-live="polite">{saveError}</div>}
        <footer>
          <button type="button" onClick={onClose}>取消</button>
          <button className="primary" type="submit" disabled={uploadState === "uploading" || isSaving}>
            {isSaving ? "保存中" : "保存"}
          </button>
        </footer>
      </form>
    </div>
  );
}

export function canManageWorkspace(item: Workspace) {
  if (!item.workspaceId || item.readonly || item.status === "FROZEN") return false;
  return ["拥有者", "管理员"].includes(item.role);
}

export function isReadonlyWorkspace(item: Workspace) {
  return Boolean(item.readonly || item.status === "FROZEN");
}

export function readAccessToken() {
  const adminSession = readAdminSession();
  const frontendSession = readFrontendSession();
  return frontendSession?.access_token || adminSession?.access_token || "";
}

function toLocalDateTimeInputValue(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

export function defaultExpiryAt() {
  const now = new Date();
  const quarterEndMonth = Math.floor(now.getMonth() / 3) * 3 + 2;
  const quarterEnd = new Date(now.getFullYear(), quarterEndMonth + 1, 0, 23, 59, 59);
  if (quarterEnd <= now) {
    quarterEnd.setMonth(quarterEnd.getMonth() + 3);
  }
  return `${toLocalDateTimeInputValue(quarterEnd)}Z`;
}

function datetimeLocalValue(value: string) {
  return (value || defaultExpiryAt()).replace("Z", "").slice(0, 19);
}

function toDateTimeDisplayValue(value: string) {
  return datetimeLocalValue(value).replace("T", " ");
}

function fromDateTimeDisplayValue(value: string) {
  const normalized = value.trim().replace(/\//g, "-").replace(/\s+/, "T");
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$/.test(normalized)) return "";
  const parsed = new Date(`${normalized}Z`);
  if (!Number.isFinite(parsed.getTime())) return "";
  return `${normalized}Z`;
}

function daysInMonth(year: number, month: number) {
  return new Date(year, month + 1, 0).getDate();
}

function clampTimePart(value: string, max: number) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return "00";
  return String(Math.min(Math.max(parsed, 0), max)).padStart(2, "0");
}

function isFutureExpiry(value: string) {
  const parsed = new Date(value);
  return Number.isFinite(parsed.getTime()) && parsed > new Date();
}

export function nextFixedExpiryValue(value: string) {
  return isFutureExpiry(value) ? value : defaultExpiryAt();
}

export function validateCreateApplicationForm(form: {
  name: string;
  code: string;
  member_quota: string;
  storage_quota_gb: string;
  ai_quota_tokens: string;
  expiry_type: string;
  expires_at: string;
}) {
  const name = form.name.trim();
  const code = form.code.trim();
  const members = Number(form.member_quota);
  const storage = Number(form.storage_quota_gb);
  const aiTokens = Number(form.ai_quota_tokens);
  if (name.length < 2 || name.length > 80) return "空间名称需为 2-80 个字符";
  if (!/^[a-z][a-z0-9-]{1,31}$/.test(code)) return "空间标识需为 2-32 位，以小写字母开头，仅支持小写字母、数字和连字符";
  if (!Number.isInteger(members) || members < 1 || members > 100000) return "成员上限需为 1-100000 的整数";
  if (!Number.isFinite(storage) || storage <= 0) return "存储空间必须大于 0";
  if (!Number.isInteger(aiTokens) || aiTokens < 0) return "AI Tokens 需为不小于 0 的整数";
  if (form.expiry_type === "fixed_date" && !isFutureExpiry(form.expires_at)) return "到期时间必须晚于当前时间";
  return "";
}

export function RequirementDateTimePicker({ ariaLabel, value, onChange }: { ariaLabel: string; value: string; onChange: (value: string) => void }) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState(toDateTimeDisplayValue(value));
  const [panelRect, setPanelRect] = useState({ top: 0, left: 0, width: 0, maxHeight: 360, placement: "bottom" as "top" | "bottom" });
  const selectedLocalValue = datetimeLocalValue(value || defaultExpiryAt());
  const selectedDate = new Date(selectedLocalValue);
  const calendarDate = Number.isFinite(selectedDate.getTime()) ? selectedDate : new Date(datetimeLocalValue(defaultExpiryAt()));
  const year = calendarDate.getFullYear();
  const month = calendarDate.getMonth();
  const monthDays = daysInMonth(year, month);
  const leadingDays = (new Date(year, month, 1).getDay() + 6) % 7;
  const weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
  const days = Array.from({ length: leadingDays + monthDays }, (_, index) => index < leadingDays ? 0 : index - leadingDays + 1);

  useEffect(() => {
    setDraft(toDateTimeDisplayValue(value));
  }, [value]);

  useEffect(() => {
    if (!open) return undefined;
    const updatePanelRect = () => {
      const rect = rootRef.current?.getBoundingClientRect();
      if (!rect) return;
      const width = Math.max(rect.width, 360);
      const left = Math.min(Math.max(12, rect.left), window.innerWidth - width - 12);
      const margin = 12;
      const gap = 4;
      const preferredHeight = 392;
      const belowSpace = window.innerHeight - rect.bottom - margin;
      const aboveSpace = rect.top - margin;
      const openUpward = belowSpace < preferredHeight && aboveSpace > belowSpace;
      const availableHeight = Math.max(320, Math.min(preferredHeight, openUpward ? aboveSpace - gap : belowSpace));
      const rawTop = openUpward ? rect.top - gap - availableHeight : rect.bottom + gap;
      const top = Math.min(Math.max(margin, rawTop), window.innerHeight - availableHeight - margin);
      setPanelRect({ top, left, width, maxHeight: availableHeight, placement: openUpward ? "top" : "bottom" });
    };
    const handlePointerDown = (event: globalThis.MouseEvent) => {
      const target = event.target as Node;
      const panel = document.querySelector(".admin-datetime-panel");
      if (rootRef.current?.contains(target) || panel?.contains(target)) return;
      setOpen(false);
    };
    updatePanelRect();
    window.addEventListener("resize", updatePanelRect);
    window.addEventListener("scroll", updatePanelRect, true);
    document.addEventListener("mousedown", handlePointerDown, true);
    return () => {
      window.removeEventListener("resize", updatePanelRect);
      window.removeEventListener("scroll", updatePanelRect, true);
      document.removeEventListener("mousedown", handlePointerDown, true);
    };
  }, [open]);

  const commitLocalValue = (nextLocalValue: string) => {
    onChange(`${nextLocalValue}Z`);
    setDraft(nextLocalValue.replace("T", " "));
  };
  const updateDatePart = (nextDate: Date) => {
    const current = datetimeLocalValue(value || defaultExpiryAt());
    const [, time = "23:59:59"] = current.split("T");
    commitLocalValue(`${toLocalDateTimeInputValue(nextDate).slice(0, 10)}T${time}`);
  };
  const updateTimePart = (part: "hour" | "minute" | "second", rawValue: string) => {
    const [datePart, timePart = "23:59:59"] = selectedLocalValue.split("T");
    const [hour = "23", minute = "59", second = "59"] = timePart.split(":");
    const nextHour = part === "hour" ? clampTimePart(rawValue, 23) : hour;
    const nextMinute = part === "minute" ? clampTimePart(rawValue, 59) : minute;
    const nextSecond = part === "second" ? clampTimePart(rawValue, 59) : second;
    commitLocalValue(`${datePart}T${nextHour}:${nextMinute}:${nextSecond}`);
  };
  const shiftMonth = (step: number) => {
    const next = new Date(year, month + step, Math.min(calendarDate.getDate(), 28), calendarDate.getHours(), calendarDate.getMinutes(), calendarDate.getSeconds());
    updateDatePart(next);
  };
  const applyShortcut = (mode: "today" | "quarter" | "year") => {
    const now = new Date();
    if (mode === "today") {
      commitLocalValue(`${toLocalDateTimeInputValue(now).slice(0, 10)}T23:59:59`);
      setOpen(false);
      return;
    }
    if (mode === "year") {
      commitLocalValue(`${now.getFullYear() + 1}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}T23:59:59`);
      setOpen(false);
      return;
    }
    commitLocalValue(datetimeLocalValue(defaultExpiryAt()));
    setOpen(false);
  };
  const commitDraft = () => {
    const parsed = fromDateTimeDisplayValue(draft);
    if (parsed) {
      onChange(parsed);
      setDraft(toDateTimeDisplayValue(parsed));
    } else {
      setDraft(toDateTimeDisplayValue(value));
    }
  };
  const panel = open && createPortal(
    <div className={`admin-datetime-panel ${themeClassFromBody()}`} data-placement={panelRect.placement} role="dialog" aria-label={`${ariaLabel}选择器`} style={{ top: panelRect.top, left: panelRect.left, width: panelRect.width, maxHeight: panelRect.maxHeight }}>
      <div className="admin-datetime-calendar-head">
        <button type="button" aria-label="上个月" onClick={() => shiftMonth(-1)}><ChevronLeft size={16} /></button>
        <strong>{year}年{month + 1}月</strong>
        <button type="button" aria-label="下个月" onClick={() => shiftMonth(1)}><ChevronRight size={16} /></button>
      </div>
      <div className="admin-datetime-weekdays">{weekdays.map((day) => <span key={day}>{day}</span>)}</div>
      <div className="admin-datetime-days">
        {days.map((day, index) => day === 0 ? <span key={`blank-${index}`} /> : (
          <button key={day} type="button" className={day === calendarDate.getDate() ? "active" : ""} onClick={() => updateDatePart(new Date(year, month, day, calendarDate.getHours(), calendarDate.getMinutes(), calendarDate.getSeconds()))}>{day}</button>
        ))}
      </div>
      <div className="admin-datetime-time" aria-label="时间选择">
        <label>时<input type="number" min="0" max="23" value={selectedLocalValue.slice(11, 13)} onChange={(event) => updateTimePart("hour", event.target.value)} /></label>
        <label>分<input type="number" min="0" max="59" value={selectedLocalValue.slice(14, 16)} onChange={(event) => updateTimePart("minute", event.target.value)} /></label>
        <label>秒<input type="number" min="0" max="59" value={selectedLocalValue.slice(17, 19)} onChange={(event) => updateTimePart("second", event.target.value)} /></label>
      </div>
      <div className="admin-datetime-shortcuts">
        <button type="button" onClick={() => applyShortcut("today")}>今天 23:59:59</button>
        <button type="button" onClick={() => applyShortcut("quarter")}>本季度末</button>
        <button type="button" onClick={() => applyShortcut("year")}>一年后</button>
      </div>
    </div>,
    document.body,
  );

  return (
    <div className="admin-datetime-picker" ref={rootRef} data-testid="catalog-datetime-picker">
      <input ref={inputRef} aria-label={ariaLabel} type="text" required value={draft} onBlur={commitDraft} onChange={(event) => setDraft(event.target.value)} onFocus={() => setOpen(true)} placeholder="yyyy-mm-dd hh:mm:ss" />
      <button
        type="button"
        aria-label={`选择${ariaLabel}`}
        onClick={() => {
          if (open) {
            setOpen(false);
            return;
          }
          setOpen(true);
          inputRef.current?.focus();
        }}
      >
        <Calendar size={16} />
      </button>
      {panel}
    </div>
  );
}

function themeClassFromBody() {
  if (typeof document === "undefined") return "dark";
  return document.querySelector(".requirement-center.theme-light") ? "light" : "dark";
}


export type WorkbenchContext = { workspaces: Workspace[]; currentUser: FrontendUser; selectedWorkspaceId: string };
export function normalizeWorkbenchContext(payload: WorkbenchContext, frontendUsername?: string): WorkbenchContext {
  const rawContext = payload as WorkbenchContext & {
    current_user?: FrontendUser;
    selected_workspace_id?: string;
  };
  const rawUser = rawContext.current_user || payload.currentUser;
  const frontendDisplayName = frontendUsername?.trim();
  const rawUserName = rawUser?.name?.trim();
  const isAnonymousUser = !rawUser || !rawUserName || rawUserName === "未登录";
  const normalizedUser = isAnonymousUser && frontendDisplayName
      ? {
        name: frontendDisplayName,
        avatarInitial: avatarInitial(frontendDisplayName),
        avatarUrl: null,
        canAccessAdmin: false,
        permissions: ["requirement:read"],
      }
    : {
        ...(rawUser || emptyUser),
        avatarInitial: avatarInitial(rawUserName, rawUser?.avatarInitial || (rawUser as FrontendUser & { avatar_initial?: string } | undefined)?.avatar_initial),
        avatarUrl:
          (rawUser as FrontendUser & { avatar_url?: string | null } | undefined)?.avatar_url ?? rawUser?.avatarUrl ?? null,
        canAccessAdmin:
          (rawUser as FrontendUser & { can_access_admin?: boolean } | undefined)?.can_access_admin ?? rawUser?.canAccessAdmin ?? false,
      };
  return {
    workspaces: payload.workspaces.map((workspace) => ({
      ...workspace,
      organizationName: (workspace as Workspace & { organization_name?: string }).organization_name || workspace.organizationName,
      workspaceId: (workspace as Workspace & { workspace_id?: string }).workspace_id || workspace.workspaceId,
      memberCount: (workspace as Workspace & { member_count?: number }).member_count ?? workspace.memberCount,
      readonly: (workspace as Workspace & { readonly?: boolean }).readonly ?? false,
    })),
    currentUser: normalizedUser,
    selectedWorkspaceId: rawContext.selected_workspace_id || payload.selectedWorkspaceId,
  };
}
