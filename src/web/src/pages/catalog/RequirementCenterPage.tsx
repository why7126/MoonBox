import {
  Bot,
  BookOpen,
  Calendar,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleDot,
  ClipboardList,
  Code2,
  Command,
  FileCheck,
  GitBranch,
  ImageIcon,
  Loader2,
  KeyRound,
  LayoutDashboard,
  ListChecks,
  LogOut,
  MessageCircle,
  Plus,
  RefreshCw,
  Search,
  Send,
  Settings,
  Sigma,
  SunMoon,
  Table2,
  UserRound,
  Users,
  X,
} from "lucide-react";
import { ChangeEvent, FormEvent, KeyboardEvent, MouseEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
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
type MarkdownUploadState = "idle" | "uploading" | "done" | "failed";
type DrawerState =
  | { type: "none" }
  | { type: "markdown"; issue: IssueCard; document: IssueDocument; content: string; draft: string; loading: boolean; saving: boolean; error: string; mode: "preview" | "edit"; savedAt?: string }
  | { type: "tasks"; issue: IssueCard }
  | { type: "ai" };
type ChoiceDialog =
  | { type: "none" }
  | { type: "generation" | "completion" | "sprint"; issue: IssueCard; error: string };

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
  documentEntries?: IssueDocument[];
  detailUrl?: string;
  archiveUrl?: string;
  action?: IssueAction;
  tasks?: IssueTasks;
  updatedAt: string;
  blocked?: string;
  sprintId?: string;
  taskProgress?: [number, number];
  testProgress?: [number, number];
  manualAcceptanceCount?: number;
};

type IssueDocument = {
  name: string;
  type: "markdown" | "html" | string;
  openMode?: "drawer" | "new-tab" | string;
  open_mode?: "drawer" | "new-tab" | string;
  status?: string;
  label?: string;
  url?: string | null;
  editable?: boolean;
};

type IssueAction = {
  command: string;
  label: string;
  requiresChoice?: "generation" | "completion" | "sprint" | string | null;
  requires_choice?: "generation" | "completion" | "sprint" | string | null;
  disabledReason?: string | null;
  disabled_reason?: string | null;
};

type AuxiliaryAction = {
  command: string;
  label: string;
};

type IssueTasks = {
  done: number;
  total: number;
  blocked?: string[];
  source?: string | null;
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
  status?: string;
  readonly?: boolean;
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
  sprintOptions?: string[];
  sprint_options?: string[];
};

type ApiEnvelope<T> = {
  data: T;
};

type VditorEditorShellProps = {
  value: string;
  uploadState: MarkdownUploadState;
  uploadError: string;
  onChange: (value: string) => void;
  onImageUploadAttempt: () => void;
};

const markdownToolbarSnippets = {
  table: "\n| 列 1 | 列 2 |\n| --- | --- |\n| 内容 | 内容 |\n",
  code: "\n```ts\n// code\n```\n",
  formula: "\n$$\nE = mc^2\n$$\n",
};

function VditorEditorShell({ value, uploadState, uploadError, onChange, onImageUploadAttempt }: VditorEditorShellProps) {
  const insertSnippet = (snippet: string) => {
    const prefix = value && !value.endsWith("\n") ? "\n" : "";
    onChange(`${value}${prefix}${snippet}`);
  };

  return (
    <div className="rc-vditor-shell" data-testid="vditor-editor-shell">
      <div className="rc-vditor-toolbar" role="toolbar" aria-label="Vditor Markdown 工具栏">
        <button type="button" aria-label="插入图片" onClick={onImageUploadAttempt}>
          <ImageIcon size={14} aria-hidden="true" />
        </button>
        <button type="button" aria-label="插入表格" onClick={() => insertSnippet(markdownToolbarSnippets.table)}>
          <Table2 size={14} aria-hidden="true" />
        </button>
        <button type="button" aria-label="插入代码块" onClick={() => insertSnippet(markdownToolbarSnippets.code)}>
          <Code2 size={14} aria-hidden="true" />
        </button>
        <button type="button" aria-label="插入数学公式" onClick={() => insertSnippet(markdownToolbarSnippets.formula)}>
          <Sigma size={14} aria-hidden="true" />
        </button>
      </div>
      <div className={`rc-vditor-upload-state ${uploadState}`} data-testid="vditor-upload-state" role={uploadState === "failed" ? "alert" : "status"}>
        图片上传：{uploadState === "idle" ? "待选择" : uploadState === "uploading" ? "上传中" : uploadState === "done" ? "已插入" : "暂不可用"}
        {uploadError && <span>{uploadError}</span>}
      </div>
      <div className="rc-vditor-workspace">
        <textarea
          aria-label="编辑 capture.md"
          data-testid="markdown-source-fallback"
          value={value}
          onChange={(event) => onChange(event.target.value)}
        />
        <div className="rc-vditor-preview" aria-label="Markdown 安全预览">
          <pre>{value}</pre>
        </div>
      </div>
    </div>
  );
}

type CreatedSpaceApplicationResult = {
  application: {
    id: string;
    name: string;
    code: string;
    status: string;
  };
};

const emptyWorkspace: Workspace = {
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
  { id: "approved", title: "已评审", subtitle: "review.md 已生成", requiredDocs: ["review.md", "trace.md"] },
  { id: "sprint-planning", title: "迭代规划", subtitle: "sprint-propose", requiredDocs: ["sprint.md", "trace.md"] },
  { id: "ready-dev", title: "待开发", subtitle: "req-opsx / bug-opsx", requiredDocs: ["proposal.md", "tasks.md", "trace.md"] },
  { id: "development", title: "研发中", subtitle: "opsx-apply / sprint-apply", requiredDocs: ["tasks.md", "trace.md"] },
  { id: "acceptance", title: "验收中", subtitle: "测试与人工验收", requiredDocs: ["acceptance.md", "test-plan.md", "trace.md"] },
  { id: "done", title: "已完成", subtitle: "全链路留痕", requiredDocs: ["archive.md", "trace.md"] },
];

const stageVisibleDocs: Record<string, string[]> = {
  capture: ["capture.md", "trace.md"],
  planning: ["requirement.md", "bug.md", "prototype.html", "trace.md"],
  "review-ready": ["acceptance.md", "business-flow.md", "user-stories.md", "trace.md"],
  approved: ["review.md", "trace.md"],
  "sprint-planning": ["sprint.md", "trace.md"],
  "ready-dev": ["proposal.md", "design.md", "tasks.md", "prototype.html", "trace.md"],
  development: ["proposal.md", "tasks.md", "trace.md"],
  acceptance: ["acceptance.md", "test-plan.md", "trace.md"],
  done: ["archive.md", "trace.md"],
};

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

const nextStage: Record<string, string> = {
  capture: "planning",
  planning: "review-ready",
  "review-ready": "approved",
  approved: "sprint-planning",
  "sprint-planning": "ready-dev",
  "ready-dev": "development",
  development: "acceptance",
  acceptance: "done",
};
const sprintVisibleStages = new Set(["sprint-planning", "ready-dev", "development", "acceptance", "done"]);

const sanitizeFeedback = (value: string) =>
  value
    .replace(/\/Users\/[^ \n)]+/g, "[local-path]")
    .replace(/CodeSpaces\/Projects\/[^ \n)]+/g, "[workspace-path]")
    .replace(/token[^ \n]*/gi, "token=[redacted]")
    .slice(0, 420);

const issueDocumentEntries = (issue: IssueCard): IssueDocument[] =>
  issue.documentEntries?.length
    ? issue.documentEntries
    : issue.documents.map((name) => {
        const suffix = name.toLowerCase().endsWith(".html") ? "html" : "markdown";
        return { name, label: name, type: suffix, openMode: suffix === "html" ? "new-tab" : "drawer" };
      });

const visibleIssueDocuments = (stage: Stage, issue: IssueCard) => {
  const allowed = new Set(stageVisibleDocs[stage.id] || stage.requiredDocs);
  return issueDocumentEntries(issue).filter((document) => allowed.has(document.name));
};

const issueDetailUrl = (issue: IssueCard) => issue.detailUrl || `/requirements/${issue.id}`;

const actionChoice = (action: IssueAction | undefined) => action?.requiresChoice || action?.requires_choice || null;

const actionDisabledReason = (action: IssueAction | undefined) => action?.disabledReason || action?.disabled_reason || "";

const issueAction = (issue: IssueCard) =>
  issue.action || {
    command: `${stageAction[issue.stage]?.[issue.type] || "只读"} ${issue.id}`.trim(),
    label: stageActionLabel[issue.stage]?.[issue.type]?.replace(" →", "") || "只读",
  };

const drawerTitle = (drawer: DrawerState) => {
  if (drawer.type === "markdown") return `${drawer.issue.id} · ${drawer.document.name}`;
  if (drawer.type === "tasks") return `${drawer.issue.id} · tasks.md`;
  if (drawer.type === "ai") return "AI Chat";
  return "";
};

const visibleSprintId = (issue: IssueCard) => (sprintVisibleStages.has(issue.stage) ? issue.sprintId : undefined);

const visibleTaskProgress = (issue: IssueCard) => (["ready-dev", "development", "acceptance", "done"].includes(issue.stage) ? issue.taskProgress : undefined);

const auxiliaryActions = (issue: IssueCard): AuxiliaryAction[] => {
  if (issue.stage !== "capture") return [];
  if (issue.type === "bug") return [{ command: `/bug-explore ${issue.id}`, label: "Bug 分析" }];
  return [{ command: `/req-explore ${issue.id}`, label: "需求分析" }];
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
      documentEntries:
        (issue as IssueCard & { document_entries?: IssueDocument[] }).document_entries || issue.documentEntries || [],
      detailUrl: (issue as IssueCard & { detail_url?: string }).detail_url || issue.detailUrl,
      archiveUrl: (issue as IssueCard & { archive_url?: string }).archive_url || issue.archiveUrl,
      action: issue.action
        ? {
            ...issue.action,
            requiresChoice: issue.action.requires_choice || issue.action.requiresChoice,
            disabledReason: issue.action.disabled_reason || issue.action.disabledReason,
          }
        : undefined,
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
      readonly: (workspace as Workspace & { readonly?: boolean }).readonly ?? false,
    })),
    currentUser: normalizedUser,
    selectedWorkspaceId: rawContext.selected_workspace_id || payload.selectedWorkspaceId,
    sprintOptions: rawContext.sprint_options || payload.sprintOptions || [],
  };
}

function canManageWorkspace(item: Workspace) {
  if (!item.workspaceId || item.readonly || item.status === "FROZEN") return false;
  return ["拥有者", "管理员"].includes(item.role);
}

function isReadonlyWorkspace(item: Workspace) {
  return Boolean(item.readonly || item.status === "FROZEN");
}

function missingDocs(stage: Stage, issue: IssueCard) {
  return stage.requiredDocs.filter((doc) => !issue.documents.includes(doc));
}

function canArchive(issue: IssueCard) {
  if (issue.stage !== "acceptance") return true;
  const testsDone = !issue.testProgress || issue.testProgress[0] >= issue.testProgress[1];
  return testsDone && (issue.manualAcceptanceCount || 0) === 0;
}

function readAccessToken() {
  const adminSession = readAdminSession();
  const frontendSession = readFrontendSession();
  return frontendSession?.access_token || adminSession?.access_token || "";
}

function toLocalDateTimeInputValue(date: Date) {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
}

function defaultExpiryAt() {
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

function nextFixedExpiryValue(value: string) {
  return isFutureExpiry(value) ? value : defaultExpiryAt();
}

function validateCreateApplicationForm(form: {
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

function RequirementDateTimePicker({ ariaLabel, value, onChange }: { ariaLabel: string; value: string; onChange: (value: string) => void }) {
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
  const [isApplicationOpen, setIsApplicationOpen] = useState(false);
  const [applicationError, setApplicationError] = useState("");
  const [isSubmittingApplication, setIsSubmittingApplication] = useState(false);
  const [createdSpaceResult, setCreatedSpaceResult] = useState<CreatedSpaceApplicationResult | null>(null);
  const [isCodeManuallyEdited, setIsCodeManuallyEdited] = useState(false);
  const [createApplicationForm, setCreateApplicationForm] = useState({
    name: "",
    code: "",
    description: "",
    member_quota: "20",
    storage_quota_gb: "100",
    ai_quota_tokens: "1000000",
    expiry_type: "fixed_date",
    expires_at: defaultExpiryAt(),
  });
  const [settingsTab, setSettingsTab] = useState<SettingsTab>("general");
  const [toast, setToast] = useState("");
  const [captureOpen, setCaptureOpen] = useState(false);
  const [captureForm, setCaptureForm] = useState({ type: "requirement" as IssueType, title: "", priority: "P2" as IssueCard["priority"], description: "" });
  const [captureError, setCaptureError] = useState("");
  const [drawer, setDrawer] = useState<DrawerState>({ type: "none" });
  const [drawerWidth, setDrawerWidth] = useState(520);
  const [markdownUploadState, setMarkdownUploadState] = useState<MarkdownUploadState>("idle");
  const [markdownUploadError, setMarkdownUploadError] = useState("");
  const [choiceDialog, setChoiceDialog] = useState<ChoiceDialog>({ type: "none" });
  const [lockedActionId, setLockedActionId] = useState("");
  const [aiMessages, setAiMessages] = useState<Array<{ role: "ai" | "user"; content: string }>>([
    { role: "ai", content: "我会在这里汇总卡片动作、命令上下文和失败原因。" },
  ]);
  const [aiDraft, setAiDraft] = useState("");
  const [draftWorkspace, setDraftWorkspace] = useState(emptyWorkspace);
  const closeTimerRef = useRef<number | null>(null);
  const userZoneRef = useRef<HTMLDivElement>(null);
  const spacePopoverRef = useRef<HTMLElement>(null);
  const captureTitleRef = useRef<HTMLInputElement | null>(null);
  const drawerResizeRef = useRef({ active: false, startX: 0, startWidth: 520 });
  const issues = context?.issues ?? [];
  const availableWorkspaces = context?.workspaces ?? [];
  const [sessionFallbackUser, setSessionFallbackUser] = useState<FrontendUser>(() => fallbackUserFromSession());
  const activeUser = context?.currentUser ?? sessionFallbackUser;
  const sprintOptions = context?.sprintOptions || context?.sprint_options || [];

  const isDirtyMarkdownDrawer = useCallback((state: DrawerState = drawer) => (
    state.type === "markdown" && state.mode === "edit" && state.draft !== state.content
  ), [drawer]);

  const closeDrawer = useCallback(() => {
    if (isDirtyMarkdownDrawer() && !window.confirm("capture.md 有未保存修改，确认关闭？")) return;
    setDrawer({ type: "none" });
  }, [isDirtyMarkdownDrawer]);

  const isEditableDocument = (state: DrawerState) => (
    state.type === "markdown" && state.issue.stage === "capture" && state.document.name === "capture.md" && state.document.editable !== false
  );

  const markdownDrawerModeLabel = (state: DrawerState) => {
    if (state.type !== "markdown") return "";
    if (!isEditableDocument(state)) return "只读文档";
    return state.mode === "edit" ? "编辑 capture.md" : "预览 capture.md";
  };

  const beginDrawerResize = (event: MouseEvent<HTMLButtonElement>) => {
    event.preventDefault();
    drawerResizeRef.current = { active: true, startX: event.clientX, startWidth: drawerWidth };
    document.body.classList.add("rc-resizing-drawer");
  };

  const loadContext = useCallback(async (mode: "initial" | "refresh" = "initial") => {
    const isRefresh = mode === "refresh";
    if (isRefresh) {
      setIsRefreshingContext(true);
    } else {
      setIsLoadingContext(true);
    }
    setContextError("");
    try {
      const frontendSession = readFrontendSession();
      const token = readAccessToken();
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
      setCaptureOpen(false);
      setChoiceDialog({ type: "none" });
      closeDrawer();
    };
    document.addEventListener("keydown", closeOnEscape);
    return () => document.removeEventListener("keydown", closeOnEscape);
  }, [closeDrawer]);

  useEffect(() => {
    const handleResizeMove = (event: globalThis.MouseEvent) => {
      if (!drawerResizeRef.current.active) return;
      const delta = drawerResizeRef.current.startX - event.clientX;
      setDrawerWidth(Math.min(760, Math.max(420, drawerResizeRef.current.startWidth + delta)));
    };
    const stopResize = () => {
      drawerResizeRef.current.active = false;
      document.body.classList.remove("rc-resizing-drawer");
    };
    document.addEventListener("mousemove", handleResizeMove);
    document.addEventListener("mouseup", stopResize);
    return () => {
      document.removeEventListener("mousemove", handleResizeMove);
      document.removeEventListener("mouseup", stopResize);
      document.body.classList.remove("rc-resizing-drawer");
    };
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

  useEffect(() => {
    if (!captureOpen) return;
    window.setTimeout(() => captureTitleRef.current?.focus(), 0);
  }, [captureOpen]);

  const owners = useMemo(() => ["全部负责人", ...Array.from(new Set(issues.map((issue) => issue.owner)))], [issues]);
  const priorities = ["全部优先级", "P0", "P1", "P2"];
  const sprints = useMemo(
    () => ["全部 Sprint", ...Array.from(new Set(issues.map((issue) => visibleSprintId(issue)).filter(Boolean)))],
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
      const matchesSprint = sprintFilter === "全部 Sprint" || visibleSprintId(issue) === sprintFilter;
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

  const openApplicationCenter = () => {
    closeSpacePopoverNow();
    setIsUserMenuOpen(false);
    setIsApplicationOpen(true);
    setApplicationError("");
    setCreatedSpaceResult(null);
  };

  const submitCreateApplication = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const validationError = validateCreateApplicationForm(createApplicationForm);
    if (validationError) {
      setApplicationError(validationError);
      return;
    }
    setIsSubmittingApplication(true);
    setApplicationError("");
    try {
      const token = readAccessToken();
      const response = await fetch("/api/v1/catalog/workspace-applications/create", {
        method: "POST",
        headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
        body: JSON.stringify({
          ...createApplicationForm,
          member_quota: Number(createApplicationForm.member_quota),
          storage_quota_gb: Number(createApplicationForm.storage_quota_gb),
          ai_quota_tokens: Number(createApplicationForm.ai_quota_tokens),
          expires_at: createApplicationForm.expiry_type === "fixed_date" ? createApplicationForm.expires_at : null,
        }),
      });
      if (!response.ok) throw new Error(await response.text());
      const envelope = (await response.json()) as ApiEnvelope<CreatedSpaceApplicationResult>;
      setCreatedSpaceResult(envelope.data);
      setToast("创建空间申请已提交");
      setCreateApplicationForm({ name: "", code: "", description: "", member_quota: "20", storage_quota_gb: "100", ai_quota_tokens: "1000000", expiry_type: "fixed_date", expires_at: defaultExpiryAt() });
      setIsCodeManuallyEdited(false);
      await loadContext("refresh");
    } catch {
      setApplicationError("创建空间失败，请检查必填项、空间标识和配额范围");
    } finally {
      setIsSubmittingApplication(false);
    }
  };

  const updateCreateName = (value: string) => {
    const slug = value
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 32);
    setCreateApplicationForm((current) => ({ ...current, name: value, code: isCodeManuallyEdited ? current.code : slug }));
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

  const openIssueDetail = (issue: IssueCard) => {
    window.open(issueDetailUrl(issue), "_blank", "noopener,noreferrer");
  };

  const openDocument = async (issue: IssueCard, document: IssueDocument) => {
    const mode = document.openMode || document.open_mode;
    if (document.status && document.status !== "available") {
      setToast("文档暂不可用，未触发卡片流转");
      return;
    }
    if (document.type === "html" || mode === "new-tab") {
      window.open(document.url || `${issueDetailUrl(issue)}?document=${encodeURIComponent(document.name)}`, "_blank", "noopener,noreferrer");
      return;
    }
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setDrawer({ type: "markdown", issue, document, content: "", draft: "", loading: true, saving: false, error: "", mode: "preview" });
    try {
      const token = readAccessToken();
      const response = await fetch(document.url || `/api/v1/requirement-center/issues/${issue.id}/documents/${document.name}`, {
        headers: { accept: "application/json", ...(token ? { authorization: `Bearer ${token}` } : {}) },
      });
      if (!response.ok) throw new Error(response.status === 403 ? "无权读取该文档" : "文档读取失败");
      const envelope = (await response.json()) as ApiEnvelope<{ content: string }>;
      setDrawer({ type: "markdown", issue, document, content: envelope.data.content, draft: envelope.data.content, loading: false, saving: false, error: "", mode: "preview" });
    } catch (error) {
      setDrawer({ type: "markdown", issue, document, content: "", draft: "", loading: false, saving: false, error: sanitizeFeedback(error instanceof Error ? error.message : "文档读取失败"), mode: "preview" });
    }
  };

  const saveMarkdownDocument = async () => {
    if (drawer.type !== "markdown" || !isEditableDocument(drawer) || drawer.saving) return;
    setDrawer({ ...drawer, saving: true, error: "" });
    try {
      const token = readAccessToken();
      const response = await fetch(drawer.document.url || `/api/v1/requirement-center/issues/${drawer.issue.id}/documents/${drawer.document.name}`, {
        method: "PUT",
        headers: {
          accept: "application/json",
          "content-type": "application/json",
          ...(token ? { authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ content: drawer.draft }),
      });
      if (!response.ok) {
        if (response.status === 403) throw new Error("仅采集池 capture.md 支持编辑");
        if (response.status === 404) throw new Error("文档不存在或已移动");
        throw new Error("文档保存失败");
      }
      const envelope = (await response.json()) as ApiEnvelope<{ content: string }>;
      setDrawer({ ...drawer, content: envelope.data.content, draft: envelope.data.content, saving: false, error: "", mode: "preview", savedAt: "刚刚保存" });
      setToast("capture.md 已保存");
    } catch (error) {
      setDrawer({ ...drawer, saving: false, error: sanitizeFeedback(error instanceof Error ? error.message : "文档保存失败") });
    }
  };

  const updateMarkdownDraft = (value: string) => {
    setDrawer((current) => current.type === "markdown" ? { ...current, draft: value, savedAt: undefined } : current);
  };

  const enterMarkdownEditMode = () => {
    if (drawer.type !== "markdown") return;
    setMarkdownUploadState("idle");
    setMarkdownUploadError("");
    setDrawer({ ...drawer, draft: drawer.content, mode: "edit", savedAt: undefined });
  };

  const attemptMarkdownImageUpload = () => {
    setMarkdownUploadState("failed");
    setMarkdownUploadError("文档图片上传接口暂未启用；本次不会写入本机路径或私有对象地址。");
  };

  const submitCapture = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const title = captureForm.title.trim();
    if (!title) {
      setCaptureError("标题不能为空");
      return;
    }
    const prefix = captureForm.type === "requirement" ? "REQ" : "BUG";
    const nextNumber = Math.max(
      0,
      ...issues
        .filter((issue) => issue.id.startsWith(`${prefix}-`))
        .map((issue) => Number(issue.id.split("-")[1]) || 0),
    ) + 1;
    const id = `${prefix}-${String(nextNumber).padStart(4, "0")}`;
    const newIssue: IssueCard = {
      id,
      type: captureForm.type,
      title,
      priority: captureForm.priority,
      owner: activeUser.name,
      source: "capture",
      stage: "capture",
      documents: ["capture.md", "trace.md"],
      documentEntries: [
        { name: "capture.md", type: "markdown", openMode: "drawer", label: "capture.md", status: "available" },
        { name: "trace.md", type: "markdown", openMode: "drawer", label: "trace.md", status: "available" },
      ],
      updatedAt: "刚刚",
      detailUrl: `/requirements/${id}`,
      action: {
        command: `${captureForm.type === "requirement" ? "/req-generate" : "/bug-generate"} ${id}`,
        label: captureForm.type === "requirement" ? "生成需求" : "生成 Bug",
        requiresChoice: "generation",
      },
    };
    setContext((current) => current ? { ...current, issues: [newIssue, ...current.issues] } : current);
    setCaptureForm({ type: "requirement", title: "", priority: "P2", description: "" });
    setCaptureError("");
    setCaptureOpen(false);
    setToast("Capture 已创建并插入采集池");
  };

  const appendAiMessage = (content: string, role: "ai" | "user" = "ai") => {
    setAiMessages((current) => [...current, { role, content: sanitizeFeedback(content) }]);
  };

  const sendAiMessage = () => {
    const content = aiDraft.trim();
    if (!content) return;
    appendAiMessage(content, "user");
    setAiDraft("");
    appendAiMessage("已收到，我会结合当前看板上下文给出下一步建议。");
  };

  const handleAiKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    sendAiMessage();
  };

  const validateImportedFile = (file: File | undefined, dialog: ChoiceDialog) => {
    if (!file || dialog.type === "none") return "";
    const name = file.name.toLowerCase();
    if (dialog.type === "generation") {
      const expected = dialog.issue.type === "requirement" ? "requirement.md" : "bug.md";
      return name === expected ? "" : `仅允许导入单个 ${expected}`;
    }
    if (dialog.type === "completion") {
      return name.endsWith(".zip") || name.endsWith(".md") ? "" : "仅允许 ZIP 或约定 Markdown 文件";
    }
    return "";
  };

  const runIssueAction = async (issue: IssueCard, options?: { sprintId?: string; importedFile?: File }) => {
    const action = issueAction(issue);
    if (lockedActionId) return;
    if (actionDisabledReason(action)) {
      appendAiMessage(`${issue.id} 前置条件不满足：${actionDisabledReason(action)}`);
      setDrawer({ type: "ai" });
      return;
    }
    const choice = actionChoice(action);
    if (choice && !options) {
      setChoiceDialog({ type: choice as ChoiceDialog["type"], issue, error: "" });
      return;
    }
    if (issue.stage === "development") {
      setDrawer({ type: "tasks", issue });
      return;
    }
    setLockedActionId(issue.id);
    appendAiMessage(`准备执行：${action.command}；上下文：${issue.id} / ${issue.title} / ${issue.type} / ${issue.stage}`);
    await new Promise((resolve) => window.setTimeout(resolve, 260));
    const targetStage = nextStage[issue.stage] || issue.stage;
    setContext((current) => current ? {
      ...current,
      issues: current.issues.map((item) => item.id === issue.id ? {
        ...item,
        stage: targetStage,
        sprintId: options?.sprintId || item.sprintId,
        updatedAt: "刚刚",
      } : item),
    } : current);
    setLockedActionId("");
    setChoiceDialog({ type: "none" });
    setToast(`${issue.id} 已流转到 ${stages.find((stage) => stage.id === targetStage)?.title || targetStage}`);
    appendAiMessage(`执行成功：${action.command}，卡片已流转。`);
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
    setContext((current) => current ? { ...current, selectedWorkspaceId: item.workspaceId } : current);
    setTypeFilter("all");
    setSearchQuery("");
    setOwnerFilter("全部负责人");
    setPriorityFilter("全部优先级");
    setSprintFilter("全部 Sprint");
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
                data-testid="space-switcher-popover"
                ref={spacePopoverRef}
                role="dialog"
                aria-label="切换空间"
                onMouseEnter={cancelSpacePopoverClose}
                onMouseLeave={scheduleSpacePopoverClose}
              >
                <div className="rc-space-list" data-state={isLoadingContext ? "loading" : contextError ? "error" : availableWorkspaces.length ? "ready" : "empty"}>
                  {isLoadingContext && (
                    <div className="rc-space-state" data-testid="space-loading-state" role="status">空间加载中</div>
                  )}
                  {!isLoadingContext && contextError && (
                    <div className="rc-space-state error" data-testid="space-error-state" role="alert">空间暂不可用，请稍后重试</div>
                  )}
                  {!isLoadingContext && !contextError && availableWorkspaces.length === 0 && (
                    <div className="rc-space-state" data-testid="space-empty-state">暂无空间</div>
                  )}
                  {!isLoadingContext && !contextError && availableWorkspaces.map((item) => (
                    <button
                      className={`${item.workspaceId === workspace.workspaceId ? "selected" : ""} ${isReadonlyWorkspace(item) ? "readonly" : ""}`.trim()}
                      type="button"
                      key={item.workspaceId}
                      data-testid={`space-option-${item.workspaceId}`}
                      data-current={item.workspaceId === workspace.workspaceId ? "true" : "false"}
                      data-readonly={isReadonlyWorkspace(item) ? "true" : "false"}
                      onClick={() => selectWorkspace(item)}
                    >
                      <span>
                        <strong>{item.name}</strong>
                        <em>{item.role} · {item.memberCount} 人</em>
                      </span>
                      {isReadonlyWorkspace(item) && <i className="rc-space-status" data-testid="space-frozen-badge">只读</i>}
                      {item.workspaceId === workspace.workspaceId && <Check size={15} aria-label="当前空间" />}
                    </button>
                  ))}
                </div>
                <div className="rc-space-actions">
                  <button type="button" data-testid="space-create-or-join-entry" onClick={openApplicationCenter}><Plus size={14} /> 创建空间</button>
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
          <button className="rc-header-action" type="button" onClick={() => setCaptureOpen(true)}>
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
                      const action = issueAction(issue);
                      const actionLabel = action.label || stageActionLabel[stage.id][issue.type];
                      const showArchive = stage.id !== "acceptance" || canArchive(issue);
                      const isLocked = lockedActionId === issue.id;
                      const documents = visibleIssueDocuments(stage, issue);
                      const taskProgress = visibleTaskProgress(issue);
                      const auxActions = auxiliaryActions(issue);
                      return (
                        <article className={`rc-card ${issue.type}`} data-issue-id={issue.id} key={issue.id}>
                          <div className="rc-card-top">
                            <strong>{issue.id}</strong>
                            {visibleSprintId(issue) && <span className="rc-sprint-tag">{visibleSprintId(issue)}</span>}
                          </div>
                          <button className="rc-card-title" type="button" onClick={() => openIssueDetail(issue)}>{issue.title}</button>
                          <div className="rc-card-meta">
                            <span className={`rc-priority ${issue.priority.toLowerCase()}`}>{issue.priority} · {issue.owner}</span>
                          </div>
                          <div className="rc-docs" aria-label={`${issue.id} 关联文档`}>
                            {documents.map((document, index) => (
                              <span className="rc-doc-item" key={document.name}>
                                {index > 0 && <span className="rc-doc-separator" aria-hidden="true"> </span>}
                                <button type="button" onClick={(event) => { event.stopPropagation(); void openDocument(issue, document); }}>
                                  {document.label || document.name}
                                </button>
                              </span>
                            ))}
                          </div>
                          {taskProgress && <button className="rc-progress" type="button" onClick={() => setDrawer({ type: "tasks", issue })}>研发 {taskProgress[0]}/{taskProgress[1]}</button>}
                          {issue.testProgress && <p className="rc-progress">测试 {issue.testProgress[0]}/{issue.testProgress[1]} · 人工验收 {issue.manualAcceptanceCount}</p>}
                          {issue.blocked || missing.length ? (
                            <p className="rc-blocked"><CircleDot size={12} /> 缺失 {missing.join("、") || issue.blocked}</p>
                          ) : null}
                          <footer>
                            <span className="rc-updated">更新 {issue.updatedAt}</span>
                            <span className="rc-card-actions" aria-label={`${issue.id} 卡片动作`}>
                              {showArchive && (
                                <button className="primary" type="button" title={action.command} disabled={isLocked || Boolean(actionDisabledReason(action))} onClick={() => void runIssueAction(issue)}>
                                  {isLocked && <Loader2 size={13} aria-hidden="true" />} {actionLabel} →
                                </button>
                              )}
                              {auxActions.map((auxAction) => (
                                  <button
                                    className="secondary"
                                    key={auxAction.command}
                                    type="button"
                                    title={auxAction.command}
                                    onClick={() => {
                                      setDrawer({ type: "ai" });
                                      setAiMessages((messages) => [...messages, { role: "ai", content: `${auxAction.command}\n已准备探索上下文，确认后可在命令入口继续执行。` }]);
                                    }}
                                  >
                                    {auxAction.label}
                                  </button>
                                ))}
                              {stage.id === "done" && (
                                <button type="button" title="查看归档" onClick={() => window.open(issue.archiveUrl || issueDetailUrl(issue), "_blank", "noopener,noreferrer")}>查看归档</button>
                              )}
                            </span>
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

      {captureOpen && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setCaptureOpen(false)}>
          <form className="rc-flow-dialog rc-capture-dialog" role="dialog" aria-modal="true" aria-label="新建 Capture" onSubmit={submitCapture} onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-dialog-head">
              <h2>新建 Capture</h2>
              <button aria-label="关闭 Capture 表单" type="button" onClick={() => setCaptureOpen(false)}><X size={17} /></button>
            </header>
            <div className="rc-capture-grid">
              <fieldset className="rc-capture-fieldset">
                <legend>类型</legend>
                <div className="rc-capture-segmented" role="group" aria-label="Capture 类型">
                  {[
                    ["requirement", "Requirement"],
                    ["bug", "Bug"],
                  ].map(([value, label]) => (
                    <button
                      className={captureForm.type === value ? "selected" : ""}
                      key={value}
                      type="button"
                      onClick={() => setCaptureForm({ ...captureForm, type: value as IssueType })}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </fieldset>
              <fieldset className="rc-capture-fieldset">
                <legend>优先级</legend>
                <div className="rc-capture-segmented priority" role="group" aria-label="Capture 优先级">
                  {(["P0", "P1", "P2"] as const).map((priority) => (
                    <button
                      className={captureForm.priority === priority ? "selected" : ""}
                      key={priority}
                      type="button"
                      onClick={() => setCaptureForm({ ...captureForm, priority })}
                    >
                      {priority}
                    </button>
                  ))}
                </div>
              </fieldset>
            </div>
            <label className="rc-form-row">
              <span className="rc-field-label">标题 <b aria-hidden="true">*</b></span>
              <input
                ref={captureTitleRef}
                aria-label="Capture 标题"
                aria-invalid={captureError ? "true" : undefined}
                className={captureError ? "invalid" : ""}
                placeholder="一句话说明要采集的需求或缺陷"
                value={captureForm.title}
                onChange={(event) => {
                  setCaptureForm({ ...captureForm, title: event.target.value });
                  if (captureError) setCaptureError("");
                }}
              />
            </label>
            <label className="rc-form-row">
              <span className="rc-field-label">补充说明</span>
              <textarea aria-label="Capture 补充说明" placeholder="背景、目标、验收想法或相关链接" value={captureForm.description} onChange={(event) => setCaptureForm({ ...captureForm, description: event.target.value })} />
            </label>
            {captureError && <p className="rc-application-alert" role="alert">{captureError}</p>}
            <footer className="rc-dialog-actions">
              <button className="rc-secondary-action" type="button" onClick={() => setCaptureOpen(false)}>取消</button>
              <button className="rc-primary-action" type="submit">创建</button>
            </footer>
          </form>
        </div>
      )}

      {choiceDialog.type !== "none" && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setChoiceDialog({ type: "none" })}>
          <section className="rc-flow-dialog" role="dialog" aria-modal="true" aria-label="选择执行方式" onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-dialog-head">
              <h2>选择执行方式</h2>
              <button aria-label="关闭选择执行方式" type="button" onClick={() => setChoiceDialog({ type: "none" })}><X size={17} /></button>
            </header>
            {choiceDialog.type === "sprint" ? (
              <div className="rc-choice-list">
                {[...sprintOptions, "新建下一迭代"].map((sprint) => (
                  <button key={sprint} type="button" onClick={() => void runIssueAction(choiceDialog.issue, { sprintId: sprint === "新建下一迭代" ? "sprint-auto" : sprint })}>{sprint}</button>
                ))}
              </div>
            ) : (
              <div className="rc-choice-list">
                <button type="button" onClick={() => void runIssueAction(choiceDialog.issue)}>AI {choiceDialog.type === "generation" ? "生成" : "完善"}</button>
                <label className="rc-file-choice">
                  <input
                    type="file"
                    aria-label="导入文件"
                    accept={choiceDialog.type === "generation" ? ".md" : ".zip,.md"}
                    onChange={(event) => {
                      const file = event.target.files?.[0];
                      const error = validateImportedFile(file, choiceDialog);
                      if (error) {
                        setChoiceDialog({ ...choiceDialog, error });
                        event.target.value = "";
                        return;
                      }
                      void runIssueAction(choiceDialog.issue, { importedFile: file });
                    }}
                  />
                  导入文件
                </label>
              </div>
            )}
            {choiceDialog.error && <p className="rc-application-alert" role="alert">{choiceDialog.error}</p>}
          </section>
        </div>
      )}

      {drawer.type !== "none" && (
        <div className="rc-drawer-layer" role="presentation">
          <button className="rc-drawer-backdrop" type="button" aria-label="关闭右侧抽屉蒙层" onClick={closeDrawer} />
          <aside className="rc-drawer" style={{ width: drawerWidth }} role="dialog" aria-modal="true" aria-label={drawerTitle(drawer)} onMouseDown={(event) => event.stopPropagation()}>
            <button className="rc-drawer-resizer" type="button" aria-label="调整右侧抽屉宽度" onMouseDown={beginDrawerResize} />
            <header className="rc-drawer-head">
              <div>
                <h2>{drawerTitle(drawer)}</h2>
                {drawer.type === "markdown" && <span>{markdownDrawerModeLabel(drawer)}</span>}
              </div>
              <button aria-label="关闭右侧抽屉" type="button" onClick={closeDrawer}><X size={17} /></button>
            </header>
            {drawer.type === "markdown" && (
              <section className="rc-markdown-view" data-testid="markdown-drawer">
                {drawer.loading && <p role="status"><Loader2 size={14} /> Markdown 加载中</p>}
                {drawer.error && <p role="alert">{drawer.error}</p>}
                {!drawer.loading && !drawer.error && (
                  isEditableDocument(drawer) && drawer.mode === "edit" ? (
                    <>
                      <VditorEditorShell
                        value={drawer.draft}
                        uploadState={markdownUploadState}
                        uploadError={markdownUploadError}
                        onChange={updateMarkdownDraft}
                        onImageUploadAttempt={attemptMarkdownImageUpload}
                      />
                      <div className="rc-markdown-actions">
                        <span>{drawer.savedAt || (drawer.draft !== drawer.content ? "有未保存修改" : "已同步")}</span>
                        <button type="button" disabled={drawer.saving || drawer.draft === drawer.content} onClick={() => void saveMarkdownDocument()}>
                          {drawer.saving && <Loader2 size={13} aria-hidden="true" />} 保存
                        </button>
                      </div>
                    </>
                  ) : (
                    <>
                      {isEditableDocument(drawer) && (
                        <div className="rc-markdown-actions preview">
                          <span>{drawer.savedAt || "预览模式"}</span>
                          <button type="button" onClick={enterMarkdownEditMode}>编辑</button>
                        </div>
                      )}
                      <pre>{drawer.content}</pre>
                    </>
                  )
                )}
              </section>
            )}
            {drawer.type === "tasks" && (
              <section className="rc-tasks-view" data-testid="tasks-drawer">
                <strong>{drawer.issue.tasks?.done ?? drawer.issue.taskProgress?.[0] ?? 0}/{drawer.issue.tasks?.total ?? drawer.issue.taskProgress?.[1] ?? 0}</strong>
                <p>{drawer.issue.tasks?.source || "tasks.md"} · 只读进度</p>
                {(drawer.issue.tasks?.blocked || []).length ? drawer.issue.tasks?.blocked?.map((item) => <span key={item}>{item}</span>) : <span>暂无阻塞</span>}
              </section>
            )}
            {drawer.type === "ai" && (
              <section className="rc-ai-chat" data-testid="ai-chat-drawer">
                <div className="rc-ai-messages">
                  {aiMessages.map((message, index) => <p key={`${message.role}-${index}`} className={message.role}>{message.content}</p>)}
                </div>
                <div className="rc-ai-composer">
                  <textarea aria-label="AI 消息" value={aiDraft} onKeyDown={handleAiKeyDown} onChange={(event) => setAiDraft(event.target.value)} />
                  <button type="button" aria-label="发送 AI 消息" onClick={sendAiMessage}><Send size={15} /></button>
                </div>
              </section>
            )}
          </aside>
        </div>
      )}

      <button className="rc-ai-fab" type="button" aria-label="打开 AI 聊天" onClick={() => setDrawer({ type: "ai" })}>
        <Bot size={20} aria-hidden="true" />
      </button>

      {isApplicationOpen && (
        <div className="rc-settings-mask" role="presentation" onMouseDown={() => setIsApplicationOpen(false)}>
          <section className="rc-space-application" role="dialog" aria-modal="true" aria-labelledby="space-application-title" onMouseDown={(event) => event.stopPropagation()}>
            <header className="rc-settings-head">
              <div>
                <h2 id="space-application-title">创建空间</h2>
                <p>每个空间对应一个产品，成员与数据相互隔离；提交后进入平台管理员审批，通过后系统会创建空间并分配你为负责人。</p>
              </div>
              <button aria-label="关闭空间申请" type="button" onClick={() => setIsApplicationOpen(false)}><X size={17} /></button>
            </header>
            {applicationError && <p className="rc-application-alert" role="alert">{applicationError}</p>}
            {createdSpaceResult ? (
              <section className="rc-application-result" role="status">
                <strong>{createdSpaceResult.application.name} 申请已提交</strong>
                <p>{createdSpaceResult.application.code} · 当前状态：{createdSpaceResult.application.status}，待平台管理员审批后才可使用。</p>
                <button className="rc-primary-action" type="button" onClick={() => setIsApplicationOpen(false)}>知道了</button>
              </section>
            ) : (
              <form className="rc-application-panel" aria-label="创建空间" onSubmit={submitCreateApplication}>
                <div className="rc-application-grid">
                  <div className="rc-form-row"><label htmlFor="create-space-name">空间名称 <b aria-hidden="true">*</b></label><input id="create-space-name" aria-label="空间名称" required value={createApplicationForm.name} onChange={(event) => updateCreateName(event.target.value)} placeholder="例如：MoonBox 产品研发" /></div>
                  <div className="rc-form-row"><label htmlFor="create-space-code">空间标识 <b aria-hidden="true">*</b></label><input id="create-space-code" aria-label="空间标识" required value={createApplicationForm.code} onChange={(event) => { setIsCodeManuallyEdited(true); setCreateApplicationForm({ ...createApplicationForm, code: event.target.value }); }} placeholder="moonbox-product" /></div>
                </div>
                <div className="rc-form-row"><label htmlFor="create-space-description">空间说明</label><textarea id="create-space-description" value={createApplicationForm.description} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, description: event.target.value })} placeholder="简要说明这个空间对应的产品与协作目标" /></div>
                <strong className="rc-application-section">空间配额</strong>
                <div className="rc-application-grid">
                  <div className="rc-form-row">
                    <label htmlFor="create-space-members">成员上限 <b aria-hidden="true">*</b></label>
                    <div className="rc-unit-field">
                      <input id="create-space-members" aria-label="成员上限" required type="number" min="1" max="100000" step="1" value={createApplicationForm.member_quota} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, member_quota: event.target.value })} />
                      <span>人</span>
                    </div>
                  </div>
                  <div className="rc-form-row">
                    <label htmlFor="create-space-storage">存储空间 <b aria-hidden="true">*</b></label>
                    <div className="rc-unit-field">
                      <input id="create-space-storage" aria-label="存储空间" required type="number" min="0.01" step="0.01" value={createApplicationForm.storage_quota_gb} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, storage_quota_gb: event.target.value })} />
                      <span>GB</span>
                    </div>
                  </div>
                  <div className="rc-form-row">
                    <label htmlFor="create-space-ai">AI Tokens <b aria-hidden="true">*</b></label>
                    <input id="create-space-ai" aria-label="AI Tokens" required type="number" min="0" step="1" value={createApplicationForm.ai_quota_tokens} onChange={(event) => setCreateApplicationForm({ ...createApplicationForm, ai_quota_tokens: event.target.value })} />
                  </div>
                  <div className="rc-form-row">
                    <label>有效期 <b aria-hidden="true">*</b></label>
                    <div className="rc-period-options">
                      <label><input type="radio" checked={createApplicationForm.expiry_type === "long_term"} onChange={() => setCreateApplicationForm({ ...createApplicationForm, expiry_type: "long_term", expires_at: "" })} /> 长期有效</label>
                      <label><input type="radio" checked={createApplicationForm.expiry_type === "fixed_date"} onChange={() => setCreateApplicationForm({ ...createApplicationForm, expiry_type: "fixed_date", expires_at: nextFixedExpiryValue(createApplicationForm.expires_at) })} /> 固定日期</label>
                    </div>
                  </div>
                </div>
                {createApplicationForm.expiry_type === "fixed_date" && (
                  <div className="rc-form-row rc-application-date-row">
                    <label htmlFor="create-space-expires">到期时间 <b aria-hidden="true">*</b></label>
                    <RequirementDateTimePicker ariaLabel="到期时间" value={createApplicationForm.expires_at} onChange={(value) => setCreateApplicationForm({ ...createApplicationForm, expires_at: value })} />
                  </div>
                )}
                <div className="rc-application-actions">
                  <button type="button" onClick={() => setIsApplicationOpen(false)}>取消</button>
                  <button className="rc-primary-action" type="submit" disabled={isSubmittingApplication}>{isSubmittingApplication ? "正在创建..." : "创建空间"}</button>
                </div>
              </form>
            )}
          </section>
        </div>
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
