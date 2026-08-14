import {
  Bot,
  BookOpen,
  Check,
  CircleDot,
  ClipboardList,
  Command,
  FileCheck,
  GitBranch,
  KeyRound,
  LayoutDashboard,
  ListChecks,
  LogOut,
  MessageCircle,
  Plus,
  RefreshCw,
  Search,
  Settings,
  SunMoon,
  UserRound,
  Users,
  X,
} from "lucide-react";
import { ChangeEvent, FormEvent, KeyboardEvent, MouseEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { LucideIcon } from "lucide-react";
import type { AdminSession } from "../admin/adminAuth";
import { PRODUCT_VERSION } from "../../../../shared/product-version";
import { ChangePasswordModal } from "../admin/AdminUserManagementPage";
import { canAccessAdmin, clearAdminSession, logoutAdmin, readAdminSession, updateAdminProfile } from "../admin/adminAuth";
import { clearFrontendSession, readFrontendSession, saveFrontendSession } from "../home/frontendSession";
import { readUiPreferences, saveUiTheme, UI_PREFERENCES_EVENT } from "../home/uiPreferences";

type IssueType = "requirement" | "bug";
type Theme = "dark" | "light";
type SettingsTab = "general" | "members" | "agents" | "skills" | "integrations" | "danger";
type ProfileUploadState = "idle" | "uploading" | "done" | "failed";

type Stage = {
  id: string;
  title: string;
  subtitle: string;
  requiredDocs: string[];
};

type IssueCard = {
  id: string;
  type: IssueType;
  title: string;
  priority: "P0" | "P1" | "P2";
  owner: string;
  source: string;
  stage: string;
  documents: string[];
  updatedAt: string;
  blocked?: string;
  sprintId?: string;
  taskProgress?: [number, number];
  testProgress?: [number, number];
  manualAcceptanceCount?: number;
};

type Workspace = {
  organizationName: string;
  workspaceId: string;
  name: string;
  slug: string;
  description: string;
  timezone: string;
  memberCount: number;
  role: string;
};

type FrontendUser = {
  name: string;
  avatarInitial: string;
  avatarUrl?: string | null;
  canAccessAdmin: boolean;
  permissions: string[];
};

type RequirementCenterContext = {
  issues: IssueCard[];
  workspaces: Workspace[];
  currentUser: FrontendUser;
  selectedWorkspaceId: string;
  stats: {
    total: number;
    requirements: number;
    bugs: number;
    blocked: number;
    drift: number;
  };
};

type ApiEnvelope<T> = {
  data: T;
};

const emptyWorkspace: Workspace = {
  organizationName: "MoonBox",
  workspaceId: "loading",
  name: "加载空间中",
  slug: "loading",
  description: "",
  timezone: "Asia/Shanghai",
  memberCount: 0,
  role: "只读",
};

const emptyUser: FrontendUser = {
  name: "未登录",
  avatarInitial: "未",
  avatarUrl: null,
  canAccessAdmin: false,
  permissions: [],
};

const frontendNavGroups: Array<{
  group: string;
  items: Array<{ label: string; title: string; icon: LucideIcon; active?: boolean }>;
}> = [
  {
    group: "WORKSPACE",
    items: [
      { label: "研发总览", title: "研发总览", icon: LayoutDashboard },
      { label: "Chat 工作台", title: "Chat 工作台", icon: MessageCircle },
      { label: "需求中心", title: "需求中心", icon: ClipboardList, active: true },
      { label: "Spec", title: "Spec", icon: GitBranch },
      { label: "任务中心", title: "任务中心", icon: ListChecks },
    ],
  },
  {
    group: "CAPABILITIES",
    items: [
      { label: "Skill Center", title: "Skill Center", icon: Command },
      { label: "Agent Center", title: "Agent Center", icon: Bot },
      { label: "知识中心", title: "知识中心", icon: BookOpen },
    ],
  },
] as const;

const stages: Stage[] = [
  { id: "capture", title: "采集池", subtitle: "Capture / req-capture / bug-capture", requiredDocs: ["capture.md", "trace.md"] },
  { id: "planning", title: "规划中", subtitle: "req-generate / bug-generate", requiredDocs: ["requirement.md", "trace.md"] },
  { id: "review-ready", title: "待评审", subtitle: "req-complete / bug-complete", requiredDocs: ["acceptance.md", "trace.md"] },
  { id: "approved", title: "已通过", subtitle: "review.md 已生成", requiredDocs: ["review.md", "trace.md"] },
  { id: "sprint-planning", title: "迭代规划", subtitle: "sprint-propose", requiredDocs: ["sprint.md", "trace.md"] },
  { id: "ready-dev", title: "待开发", subtitle: "req-opsx / bug-opsx", requiredDocs: ["proposal.md", "tasks.md", "trace.md"] },
  { id: "development", title: "研发中", subtitle: "opsx-apply / sprint-apply", requiredDocs: ["tasks.md", "trace.md"] },
  { id: "acceptance", title: "验收中", subtitle: "测试与人工验收", requiredDocs: ["acceptance.md", "test-plan.md", "trace.md"] },
  { id: "done", title: "已完成", subtitle: "全链路留痕", requiredDocs: ["archive.md", "trace.md"] },
];

const stageAction: Record<string, Record<IssueType, string>> = {
  capture: { requirement: "/req-generate", bug: "/bug-generate" },
  planning: { requirement: "/req-complete", bug: "/bug-complete" },
  "review-ready": { requirement: "/req-review", bug: "/bug-review" },
  approved: { requirement: "/sprint-propose", bug: "/sprint-propose" },
  "sprint-planning": { requirement: "/req-opsx", bug: "/bug-opsx" },
  "ready-dev": { requirement: "/opsx-apply", bug: "/opsx-apply" },
  development: { requirement: "/opsx-apply", bug: "/opsx-apply" },
  acceptance: { requirement: "/opsx-archive", bug: "/opsx-archive" },
  done: { requirement: "只读", bug: "只读" },
};

const stageActionLabel: Record<string, Record<IssueType, string>> = {
  capture: { requirement: "生成需求 →", bug: "生成 Bug →" },
  planning: { requirement: "完善需求 →", bug: "完善 Bug →" },
  "review-ready": { requirement: "发起评审 →", bug: "确认修复 →" },
  approved: { requirement: "加入迭代 →", bug: "加入迭代 →" },
  "sprint-planning": { requirement: "生成 Opsx →", bug: "生成 Opsx →" },
  "ready-dev": { requirement: "开始开发 →", bug: "开始修复 →" },
  development: { requirement: "查看进度 →", bug: "查看进度 →" },
  acceptance: { requirement: "完成 / 归档 →", bug: "完成 / 归档 →" },
  done: { requirement: "查看归档 →", bug: "查看归档 →" },
};

const settingsTabs: Array<{ id: SettingsTab; label: string }> = [
  { id: "general", label: "常规" },
  { id: "members", label: "成员与权限" },
  { id: "agents", label: "Agent" },
  { id: "skills", label: "Skill" },
  { id: "integrations", label: "集成" },
  { id: "danger", label: "高级设置" },
];

function getStoredWorkspace(workspaces: Workspace[], selectedWorkspaceId?: string) {
  try {
    const raw = window.localStorage.getItem("moonbox.workspace");
    const fallback = workspaces.find((workspace) => workspace.workspaceId === selectedWorkspaceId) || workspaces[0] || emptyWorkspace;
    if (!raw) return fallback;
    const stored = JSON.parse(raw) as Partial<Workspace>;
    const matched = workspaces.find((workspace) => workspace.workspaceId === stored.workspaceId);
    return matched ? { ...matched, ...stored } : fallback;
  } catch {
    return workspaces[0] || emptyWorkspace;
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

function AuthenticatedRequirementAvatar({
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

function frontendUserFromAdmin(user: AdminSession["user"], fallback: FrontendUser): FrontendUser {
  const displayName = (user.nickname || user.username || fallback.name || emptyUser.name).trim();
  return {
    ...fallback,
    name: displayName,
    avatarInitial: avatarInitial(displayName, fallback.avatarInitial),
    avatarUrl: user.avatar_url ?? null,
  };
}

function avatarInitial(name: string | null | undefined, fallback = emptyUser.avatarInitial) {
  const displayName = name?.trim();
  return displayName ? displayName.slice(0, 2).toUpperCase() : fallback;
}

const sessionAvatarUrl = (avatarUrl: string | null | undefined) =>
  avatarUrl?.startsWith("/api/v1/admin/users/avatar/") ? null : avatarUrl ?? null;

function fallbackUserFromSession(): FrontendUser {
  const frontendSession = readFrontendSession();
  const adminSession = readAdminSession();
  const sessionUser = frontendSession?.user || adminSession?.user;
  const displayName = (
    frontendSession?.username ||
    adminSession?.user.nickname ||
    adminSession?.user.username ||
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

function FrontendProfileModal({
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

function normalizeContext(payload: RequirementCenterContext, frontendUsername?: string): RequirementCenterContext {
  const rawContext = payload as RequirementCenterContext & {
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
    ...payload,
    issues: payload.issues.map((issue) => ({
      ...issue,
      updatedAt: (issue as IssueCard & { updated_at?: string }).updated_at || issue.updatedAt,
      sprintId: (issue as IssueCard & { sprint_id?: string }).sprint_id || issue.sprintId,
      taskProgress: (issue as IssueCard & { task_progress?: [number, number] }).task_progress || issue.taskProgress,
      testProgress: (issue as IssueCard & { test_progress?: [number, number] }).test_progress || issue.testProgress,
      manualAcceptanceCount:
        (issue as IssueCard & { manual_acceptance_count?: number }).manual_acceptance_count ?? issue.manualAcceptanceCount,
    })),
    workspaces: payload.workspaces.map((workspace) => ({
      ...workspace,
      organizationName: (workspace as Workspace & { organization_name?: string }).organization_name || workspace.organizationName,
      workspaceId: (workspace as Workspace & { workspace_id?: string }).workspace_id || workspace.workspaceId,
      memberCount: (workspace as Workspace & { member_count?: number }).member_count ?? workspace.memberCount,
    })),
    currentUser: normalizedUser,
    selectedWorkspaceId: rawContext.selected_workspace_id || payload.selectedWorkspaceId,
  };
}

function canManageWorkspace(item: Workspace) {
  return ["拥有者", "管理员"].includes(item.role);
}

function missingDocs(stage: Stage, issue: IssueCard) {
  return stage.requiredDocs.filter((doc) => !issue.documents.includes(doc));
}

function canArchive(issue: IssueCard) {
  if (issue.stage !== "acceptance") return true;
  const testsDone = !issue.testProgress || issue.testProgress[0] >= issue.testProgress[1];
  return testsDone && (issue.manualAcceptanceCount || 0) === 0;
}

export function RequirementCenterPage() {
  const [context, setContext] = useState<RequirementCenterContext | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState(true);
  const [isRefreshingContext, setIsRefreshingContext] = useState(false);
  const [contextError, setContextError] = useState("");
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [theme, setTheme] = useState<Theme>(() => readUiPreferences().theme);
  const [typeFilter, setTypeFilter] = useState<"all" | IssueType>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [ownerFilter, setOwnerFilter] = useState("全部负责人");
  const [priorityFilter, setPriorityFilter] = useState("全部优先级");
  const [sprintFilter, setSprintFilter] = useState("全部 Sprint");
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSpacePopoverOpen, setIsSpacePopoverOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [workspace, setWorkspace] = useState<Workspace>(emptyWorkspace);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [settingsTab, setSettingsTab] = useState<SettingsTab>("general");
  const [toast, setToast] = useState("");
  const [draftWorkspace, setDraftWorkspace] = useState(emptyWorkspace);
  const closeTimerRef = useRef<number | null>(null);
  const userZoneRef = useRef<HTMLDivElement>(null);
  const spacePopoverRef = useRef<HTMLElement>(null);
  const issues = context?.issues ?? [];
  const availableWorkspaces = context?.workspaces ?? [];
  const [sessionFallbackUser, setSessionFallbackUser] = useState<FrontendUser>(() => fallbackUserFromSession());
  const activeUser = context?.currentUser ?? sessionFallbackUser;

  const loadContext = useCallback(async (mode: "initial" | "refresh" = "initial") => {
    const isRefresh = mode === "refresh";
    if (isRefresh) {
      setIsRefreshingContext(true);
    } else {
      setIsLoadingContext(true);
    }
    setContextError("");
    try {
      const adminSession = readAdminSession();
      const frontendSession = readFrontendSession();
      const token = frontendSession?.access_token || adminSession?.access_token;
      const response = await fetch("/api/v1/requirement-center/context", {
        headers: {
          accept: "application/json",
          ...(token ? { authorization: `Bearer ${token}` } : {}),
        },
      });
      if (response.status === 401 || response.status === 403) {
        setContext(null);
        clearFrontendSession();
        clearAdminSession();
        setSessionFallbackUser(emptyUser);
        if (window.location.pathname !== "/login") {
          window.history.replaceState(null, "", "/login");
          window.dispatchEvent(new PopStateEvent("popstate"));
        }
        setContextError("登录态已失效，请重新登录");
        return;
      }
      if (!response.ok) {
        throw new Error(`需求中心数据加载失败：${response.status}`);
      }
      const envelope = (await response.json()) as ApiEnvelope<RequirementCenterContext>;
      const nextContext = normalizeContext(envelope.data, frontendSession?.username);
      const nextWorkspace = getStoredWorkspace(nextContext.workspaces, nextContext.selectedWorkspaceId);
      setContext(nextContext);
      setSessionFallbackUser(nextContext.currentUser);
      setWorkspace(nextWorkspace);
      setDraftWorkspace(nextWorkspace);
    } catch {
      if (isRefresh) {
        setToast("刷新失败，已保留当前看板");
      } else {
        setContext(null);
        setContextError("需求中心数据暂时不可用，请稍后重试");
      }
    } finally {
      if (isRefresh) {
        setIsRefreshingContext(false);
      } else {
        setIsLoadingContext(false);
      }
    }
  }, []);

  useEffect(() => {
    void loadContext();
  }, [loadContext]);

  useEffect(() => {
    const syncTheme = () => setTheme(readUiPreferences().theme);
    window.addEventListener(UI_PREFERENCES_EVENT, syncTheme);
    window.addEventListener("storage", syncTheme);
    return () => {
      window.removeEventListener(UI_PREFERENCES_EVENT, syncTheme);
      window.removeEventListener("storage", syncTheme);
    };
  }, []);

  useEffect(() => {
    const closeOnEscape = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setIsSpacePopoverOpen(false);
      setIsUserMenuOpen(false);
      setIsSettingsOpen(false);
      setIsProfileModalOpen(false);
      setIsPasswordModalOpen(false);
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, []);

  useEffect(() => {
    const closeOnOutsideClick = (event: globalThis.MouseEvent) => {
      const target = event.target as Node;
      if (userZoneRef.current?.contains(target) || spacePopoverRef.current?.contains(target)) return;
      setIsUserMenuOpen(false);
      setIsSpacePopoverOpen(false);
    };
    document.addEventListener("mousedown", closeOnOutsideClick);
    return () => document.removeEventListener("mousedown", closeOnOutsideClick);
  }, []);

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(""), 2200);
    return () => window.clearTimeout(timer);
  }, [toast]);

  const owners = useMemo(() => ["全部负责人", ...Array.from(new Set(issues.map((issue) => issue.owner)))], [issues]);
  const priorities = ["全部优先级", "P0", "P1", "P2"];
  const sprints = useMemo(
    () => ["全部 Sprint", ...Array.from(new Set(issues.map((issue) => issue.sprintId).filter(Boolean)))],
    [issues],
  );

  const filteredIssues = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    return issues.filter((issue) => {
      const matchesType = typeFilter === "all" || issue.type === typeFilter;
      const matchesSearch =
        !query ||
        issue.id.toLowerCase().includes(query) ||
        issue.title.toLowerCase().includes(query) ||
        issue.owner.toLowerCase().includes(query) ||
        issue.documents.some((doc) => doc.toLowerCase().includes(query));
      const matchesOwner = ownerFilter === "全部负责人" || issue.owner === ownerFilter;
      const matchesPriority = priorityFilter === "全部优先级" || issue.priority === priorityFilter;
      const matchesSprint = sprintFilter === "全部 Sprint" || issue.sprintId === sprintFilter;
      return matchesType && matchesSearch && matchesOwner && matchesPriority && matchesSprint;
    });
  }, [issues, ownerFilter, priorityFilter, searchQuery, sprintFilter, typeFilter]);

  const manageableWorkspace = canManageWorkspace(workspace);

  const stats = [
    { label: "全部对象", value: filteredIssues.length },
    { label: "需求", value: filteredIssues.filter((issue) => issue.type === "requirement").length },
    { label: "Bug", value: filteredIssues.filter((issue) => issue.type === "bug").length },
    { label: "当前阻塞", value: filteredIssues.filter((issue) => issue.blocked).length },
  ];

  const cancelSpacePopoverClose = () => {
    if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current);
    closeTimerRef.current = null;
  };

  const scheduleSpacePopoverClose = () => {
    cancelSpacePopoverClose();
    closeTimerRef.current = window.setTimeout(() => {
      setIsSpacePopoverOpen(false);
    }, 180);
  };

  const closeSpacePopoverNow = () => {
    cancelSpacePopoverClose();
    setIsSpacePopoverOpen(false);
  };

  const enterAdmin = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    window.history.pushState(null, "", "/admin");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const openChangePassword = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsPasswordModalOpen(true);
  };

  const openProfile = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsProfileModalOpen(true);
  };

  const completeProfileSave = (nextUser: AdminSession["user"]) => {
    const nextFrontendUser = frontendUserFromAdmin(nextUser, activeUser);
    setContext((current) => current ? { ...current, currentUser: nextFrontendUser } : current);
    const session = readAdminSession();
    if (session) {
      saveFrontendSession({ ...session, user: nextUser });
    } else {
      saveFrontendSession(nextFrontendUser.name);
    }
    setIsProfileModalOpen(false);
    setToast("个人资料已更新");
  };

  const completePasswordChange = () => {
    setIsPasswordModalOpen(false);
    clearFrontendSession();
    window.history.pushState(null, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const logoutFrontend = async () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    const adminSession = readAdminSession();
    if (adminSession?.access_token) {
      await logoutAdmin();
    } else {
      clearFrontendSession();
    }
    window.history.pushState(null, "", "/login");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed((value) => !value);
    setIsUserMenuOpen(false);
    setIsSpacePopoverOpen(false);
  };

  const selectWorkspace = (item: Workspace) => {
    setWorkspace(item);
    setDraftWorkspace(item);
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(item));
    setIsSpacePopoverOpen(false);
    setIsUserMenuOpen(false);
    setToast(`已切换到 ${item.name}`);
  };

  const openSpaceSettings = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setDraftWorkspace(workspace);
    setIsSettingsOpen(true);
    setIsUserMenuOpen(false);
    setIsSpacePopoverOpen(false);
  };

  const updateDraft = (field: keyof Workspace) => (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setDraftWorkspace((current) => ({ ...current, [field]: event.target.value }));
  };

  const saveSpaceSettings = () => {
    setWorkspace(draftWorkspace);
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(draftWorkspace));
    setIsSettingsOpen(false);
    setToast("空间设置已保存");
    void loadContext();
  };

  const handleMenuKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      setIsUserMenuOpen(false);
      setIsSpacePopoverOpen(false);
    }
  };

  return (
    <main className={`requirement-center theme-${theme}`} data-theme={theme}>
      <aside className={`rc-sidebar ${isSidebarCollapsed ? "collapsed" : ""}`}>
        <div className="rc-brand">
          <span className="rc-brand-mark">
            <img src="/brand/moonbox/moonbox-app-icon-256.png" alt="MoonBox 产品图标" />
          </span>
          {!isSidebarCollapsed && (
            <span className="rc-brand-copy">
              <strong>MoonBox</strong>
              <em>AI原生软件工厂</em>
            </span>
          )}
          {!isSidebarCollapsed && <span className="rc-version-badge">{PRODUCT_VERSION}</span>}
          <button
            className="rc-collapse"
            type="button"
            onClick={toggleSidebar}
            aria-label={isSidebarCollapsed ? "展开侧边栏" : "收起侧边栏"}
          >
            {isSidebarCollapsed ? "›" : "‹"}
          </button>
        </div>
        <nav className="rc-nav" aria-label="前台导航">
          {frontendNavGroups.map((group) => (
            <div className="rc-nav-group" key={group.group}>
              <span className="rc-nav-group-label">{group.group}</span>
              {group.items.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    className={`rc-nav-item ${item.active ? "active" : ""}`}
                    type="button"
                    title={item.title}
                    aria-current={item.active ? "page" : undefined}
                    key={item.label}
                  >
                    <Icon className="rc-nav-icon" size={16} strokeWidth={1.5} aria-hidden="true" />
                    <span className="rc-nav-label">{item.label}</span>
                  </button>
                );
              })}
            </div>
          ))}
        </nav>
        <div className="rc-sidebar-bottom">
          <div className="rc-user-zone" ref={userZoneRef} onKeyDown={handleMenuKey}>
            <button
              className="rc-user-trigger"
              type="button"
              onClick={() => setIsUserMenuOpen((value) => !value)}
              aria-haspopup="menu"
              aria-expanded={isUserMenuOpen}
            >
              <AuthenticatedRequirementAvatar avatarUrl={activeUser.avatarUrl} alt={`${activeUser.name} 头像`} fallback={activeUser.avatarInitial} />
              {!isSidebarCollapsed && (
              <span className="rc-user-copy">
                <strong>{activeUser.name}</strong>
                <em>{workspace.name}</em>
              </span>
            )}
              {!isSidebarCollapsed && <span className={`rc-user-chevron ${isUserMenuOpen ? "open" : ""}`} aria-hidden="true">{isUserMenuOpen ? "⌄" : "⌃"}</span>}
            </button>
            {isUserMenuOpen && !isSidebarCollapsed && (
              <div className="rc-user-menu" role="menu" aria-label="用户菜单" onMouseLeave={scheduleSpacePopoverClose} onMouseEnter={cancelSpacePopoverClose}>
                <div className="rc-menu-group" role="group" aria-label="账号">
                  <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openProfile}>
                    <UserRound className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 个人资料
                  </button>
                  <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openChangePassword}>
                    <KeyRound className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 修改密码
                  </button>
                  {activeUser.canAccessAdmin && (
                    <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={enterAdmin}>
                      <LayoutDashboard className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 进入后台
                    </button>
                  )}
                </div>
                <div className="rc-menu-group" role="group" aria-label="空间">
                  <button
                    className="rc-has-submenu"
                    role="menuitem"
                    type="button"
                    onMouseEnter={() => {
                      cancelSpacePopoverClose();
                      setIsSpacePopoverOpen(true);
                    }}
                  >
                    <Users className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>切换空间</span>
                    <span className="rc-submenu-arrow" aria-hidden="true">&gt;</span>
                  </button>
                  {manageableWorkspace && (
                    <button role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={openSpaceSettings}>
                      <Settings className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 设置空间
                    </button>
                  )}
                </div>
                <div className="rc-menu-group" role="group" aria-label="偏好">
                  <button
                    id="themeSwitch"
                    className="rc-theme-switch"
                    role="switch"
                    type="button"
                    aria-checked={theme === "light"}
                    aria-label="切换明暗主题"
                    onMouseEnter={closeSpacePopoverNow}
                    onClick={() => {
                      const nextTheme = theme === "dark" ? "light" : "dark";
                      setTheme(nextTheme);
                      saveUiTheme(nextTheme);
                      setToast(nextTheme === "light" ? "已切换为浅色主题" : "已切换为深色主题");
                    }}
                  >
                    <SunMoon className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>界面主题</span>
                    <i className={`rc-theme-toggle ${theme === "light" ? "on" : ""}`} aria-hidden="true" />
                  </button>
                </div>
                <div className="rc-menu-group rc-menu-session" role="group" aria-label="会话">
                  <button className="logout" role="menuitem" type="button" onMouseEnter={closeSpacePopoverNow} onClick={() => void logoutFrontend()}>
                    <LogOut className="rc-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /> 退出登录
                  </button>
                </div>
              </div>
            )}
            {isSpacePopoverOpen && !isSidebarCollapsed && (
              <section
                className="rc-space-popover"
                ref={spacePopoverRef}
                role="dialog"
                aria-label="切换空间"
                onMouseEnter={cancelSpacePopoverClose}
                onMouseLeave={scheduleSpacePopoverClose}
              >
                <div className="rc-space-list">
                  {availableWorkspaces.map((item) => (
                    <button
                      className={item.workspaceId === workspace.workspaceId ? "selected" : ""}
                      type="button"
                      key={item.workspaceId}
                      onClick={() => selectWorkspace(item)}
                    >
                      <span>
                        <strong>{item.name}</strong>
                        <em>{item.role} · {item.memberCount} 人</em>
                      </span>
                      {item.workspaceId === workspace.workspaceId && <Check size={15} aria-label="当前空间" />}
                    </button>
                  ))}
                </div>
                <div className="rc-space-actions">
                  <button type="button"><Plus size={14} /> 创建或加入空间</button>
                </div>
              </section>
            )}
          </div>
        </div>
      </aside>

      <section className="rc-content">
        <header className="rc-page-header">
          <div>
            <p>Requirement Operations</p>
            <h1>需求研发流转看板</h1>
          </div>
          <button className="rc-header-action" type="button">
            <Command size={16} aria-hidden="true" /> 新建 Capture
          </button>
        </header>

        <section className="rc-stats" aria-label="需求中心统计" data-state={isLoadingContext ? "loading" : contextError ? "error" : "ready"}>
          {stats.map((item) => (
            <article className="rc-stat" key={item.label}>
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          ))}
        </section>

        <section className="rc-toolbar" aria-label="需求中心筛选">
          <label className="rc-search">
            <Search size={15} aria-hidden="true" />
            <input
              aria-label="搜索治理对象"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="搜索 ID、标题、文档或负责人"
              disabled={isLoadingContext || Boolean(contextError)}
            />
          </label>
          <div className="rc-segmented" aria-label="对象类型筛选">
            {[
              ["all", "全部"],
              ["requirement", "需求"],
              ["bug", "Bug"],
            ].map(([value, label]) => (
              <button
                className={typeFilter === value ? "selected" : ""}
                type="button"
                key={value}
                onClick={() => setTypeFilter(value as "all" | IssueType)}
                disabled={isLoadingContext || Boolean(contextError)}
              >
                {label}
              </button>
            ))}
          </div>
          <select aria-label="负责人筛选" value={ownerFilter} onChange={(event) => setOwnerFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
            {owners.map((owner) => <option key={owner}>{owner}</option>)}
          </select>
          <select aria-label="优先级筛选" value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
            {priorities.map((priority) => <option key={priority}>{priority}</option>)}
          </select>
          <select aria-label="Sprint 筛选" value={sprintFilter} onChange={(event) => setSprintFilter(event.target.value)} disabled={isLoadingContext || Boolean(contextError)}>
            {sprints.map((sprint) => <option key={sprint}>{sprint}</option>)}
          </select>
          <button
            className={`rc-refresh-button ${isRefreshingContext ? "refreshing" : ""}`}
            type="button"
            aria-label="刷新需求中心"
            aria-busy={isRefreshingContext}
            title="刷新"
            disabled={isLoadingContext || isRefreshingContext}
            onClick={() => void loadContext("refresh")}
          >
            <RefreshCw size={15} aria-hidden="true" />
          </button>
        </section>

        <section className="rc-board-wrap" aria-label="9 阶段需求研发流转看板" data-state={isLoadingContext ? "loading" : contextError ? "error" : filteredIssues.length ? "ready" : "empty"}>
          {isLoadingContext && (
            <div className="rc-state-panel" role="status">
              <span className="rc-skeleton" />
              <strong>正在聚合需求中心数据</strong>
              <p>读取 REQ、BUG、Sprint 和 OpenSpec Change 状态。</p>
            </div>
          )}
          {!isLoadingContext && contextError && (
            <div className="rc-state-panel error" role="alert">
              <strong>{contextError}</strong>
              <p>筛选与看板已暂停，避免展示过期治理信息。</p>
              <button type="button" onClick={() => void loadContext()}>重试</button>
            </div>
          )}
          {!isLoadingContext && !contextError && filteredIssues.length === 0 && (
            <div className="rc-state-panel" role="status">
              <strong>没有匹配的治理对象</strong>
              <p>调整搜索、负责人、优先级或 Sprint 筛选后再查看。</p>
            </div>
          )}
          <div className="rc-board">
            {stages.map((stage) => {
              const items = filteredIssues.filter((issue) => issue.stage === stage.id);
              return (
                <section className="rc-column" data-stage={stage.id} aria-labelledby={`stage-${stage.id}`} key={stage.id}>
                  <header className="rc-column-head">
                    <div>
                      <h2 id={`stage-${stage.id}`}>{stage.title}</h2>
                      <p>{stage.subtitle}</p>
                    </div>
                    <span aria-label={`${stage.title} ${items.length} 个对象`}>{String(items.length).padStart(2, "0")}</span>
                  </header>
                  <div className="rc-column-body">
                    {items.map((issue) => {
                      const missing = missingDocs(stage, issue);
                      const action = stageAction[stage.id][issue.type];
                      const actionLabel = stageActionLabel[stage.id][issue.type];
                      const showArchive = stage.id !== "acceptance" || canArchive(issue);
                      return (
                        <article className={`rc-card ${issue.type}`} data-issue-id={issue.id} key={issue.id}>
                          <div className="rc-card-top">
                            <strong>{issue.id}</strong>
                            {issue.sprintId && <span className="rc-sprint-tag">{issue.sprintId}</span>}
                          </div>
                          <h3>{issue.title}</h3>
                          <div className="rc-card-meta">
                            <span className={`rc-priority ${issue.priority.toLowerCase()}`}>{issue.priority} · {issue.owner}</span>
                          </div>
                          <p className="rc-docs">{issue.documents.join(" · ")}</p>
                          {issue.taskProgress && <p className="rc-progress">研发 {issue.taskProgress[0]}/{issue.taskProgress[1]}</p>}
                          {issue.testProgress && <p className="rc-progress">测试 {issue.testProgress[0]}/{issue.testProgress[1]} · 人工验收 {issue.manualAcceptanceCount}</p>}
                          {issue.blocked || missing.length ? (
                            <p className="rc-blocked"><CircleDot size={12} /> 缺失 {missing.join("、") || issue.blocked}</p>
                          ) : null}
                          <footer>
                            <span className="rc-updated">更新 {issue.updatedAt}</span>
                            {showArchive && <button type="button" title={action}>{actionLabel}</button>}
                          </footer>
                        </article>
                      );
                    })}
                  </div>
                </section>
              );
            })}
          </div>
        </section>
      </section>

      {isPasswordModalOpen && (
        <ChangePasswordModal
          onClose={() => setIsPasswordModalOpen(false)}
          onChanged={completePasswordChange}
        />
      )}

      {isProfileModalOpen && (
        <FrontendProfileModal
          user={activeUser}
          onClose={() => setIsProfileModalOpen(false)}
          onSaved={completeProfileSave}
        />
      )}

      {isSettingsOpen && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setIsSettingsOpen(false)}>
          <section
            className="rc-space-settings"
            role="dialog"
            aria-modal="true"
            aria-labelledby="space-settings-title"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <aside className="rc-settings-nav">
              <div className="rc-settings-head">
                <h2 id="space-settings-title">空间设置</h2>
                <button aria-label="关闭空间设置" type="button" onClick={() => setIsSettingsOpen(false)}>
                  <X size={17} />
                </button>
              </div>
              <p>{workspace.organizationName}</p>
              {settingsTabs.map((tab) => (
                <button
                  className={settingsTab === tab.id ? "selected" : ""}
                  key={tab.id}
                  type="button"
                  onClick={() => setSettingsTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </aside>
            <div className="rc-settings-body">
              <form className="rc-settings-panel" aria-label="空间常规设置" onSubmit={(event) => event.preventDefault()}>
                {settingsTab === "general" ? (
                  <>
                    <div className="rc-panel-intro">
                      <h3>常规</h3>
                      <p>配置当前空间“{workspace.name}”的基本信息。</p>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-name">空间名称</label>
                      <input id="workspace-name" value={draftWorkspace.name} onChange={updateDraft("name")} />
                      <span>用于侧边栏、通知和空间切换列表。</span>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-slug">空间标识</label>
                      <input id="workspace-slug" value={draftWorkspace.slug} onChange={updateDraft("slug")} />
                      <span>创建后可修改，修改可能影响外部集成。</span>
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-description">空间描述</label>
                      <textarea id="workspace-description" value={draftWorkspace.description} onChange={updateDraft("description")} />
                    </div>
                    <div className="rc-form-row">
                      <label htmlFor="workspace-timezone">默认时区</label>
                      <select id="workspace-timezone" value={draftWorkspace.timezone} onChange={updateDraft("timezone")}>
                        <option value="Asia/Shanghai">Asia/Shanghai (UTC+08:00)</option>
                        <option value="Asia/Tokyo">Asia/Tokyo</option>
                        <option value="UTC">UTC</option>
                      </select>
                    </div>
                  </>
                ) : (
                  <div className="rc-settings-placeholder">
                    <FileCheck size={20} aria-hidden="true" />
                    <strong>{settingsTabs.find((tab) => tab.id === settingsTab)?.label}</strong>
                    <span>当前分组配置项已预留，后续按权限与集成契约接入。</span>
                  </div>
                )}
              </form>
            </div>
            <footer>
              <button type="button" onClick={() => setIsSettingsOpen(false)}>取消</button>
              <button className="primary" type="button" onClick={saveSpaceSettings}>保存更改</button>
            </footer>
          </section>
        </div>
      )}

      {toast && (
        <div className="rc-toast" role="status">
          <Check size={15} aria-hidden="true" /> {toast}
        </div>
      )}
    </main>
  );
}
