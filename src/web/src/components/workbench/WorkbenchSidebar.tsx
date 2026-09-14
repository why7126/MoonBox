import type { LucideIcon } from "lucide-react";
import { BookOpen,Bot,Check,ClipboardList,Command,FileCheck,GitBranch,KeyRound,LayoutDashboard,ListChecks,LogOut,MessageCircle,Plus,Settings,SunMoon,UserRound,Users,X } from "lucide-react";
import { ChangeEvent,FormEvent,KeyboardEvent,MouseEvent,useEffect,useRef,useState } from "react";
import { PRODUCT_VERSION } from "../../../../shared/product-version";
import type { AdminSession } from "../../pages/admin/adminAuth";
import { logoutAdmin,readAdminSession } from "../../pages/admin/adminAuth";
import { ChangePasswordModal } from "../../pages/admin/AdminUserManagementPage";
import { clearFrontendSession,saveFrontendSession } from "../../pages/home/frontendSession";
import "../../styles/workbench.css";
import { useWorkbenchTheme } from "./useWorkbenchTheme";
import { AuthenticatedRequirementAvatar,canManageWorkspace,defaultExpiryAt,FrontendProfileModal,frontendUserFromAdmin,isReadonlyWorkspace,nextFixedExpiryValue,readAccessToken,RequirementDateTimePicker,validateCreateApplicationForm,type FrontendUser,type Workspace } from "./workbenchAccount";
type SettingsTab = "general" | "members" | "agents" | "skills" | "integrations" | "danger";
type ApiEnvelope<T> = { data: T };
type CreatedSpaceApplicationResult = {
  application: {
    id: string;
    name: string;
    code: string;
    status: string;
  };
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
      { label: "需求中心", title: "需求中心", icon: ClipboardList },
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

const settingsTabs: Array<{ id: SettingsTab; label: string }> = [
  { id: "general", label: "常规" },
  { id: "members", label: "成员与权限" },
  { id: "agents", label: "Agent" },
  { id: "skills", label: "Skill" },
  { id: "integrations", label: "集成" },
  { id: "danger", label: "高级设置" },
];


type Props = {
  activePage: "chat" | "requirements";
  activeUser: FrontendUser;
  workspace: Workspace;
  availableWorkspaces: Workspace[];
  isLoadingContext: boolean;
  contextError: string;
  onWorkspaceChange: (workspace: Workspace) => void;
  onUserChange: (user: FrontendUser) => void;
  onRefresh: () => void | Promise<void>;
  spaceSwitchDisabled?: boolean;
};
/** 两个工作台共用导航、账号和空间动作；业务数据由页面授权上下文提供。 */
export function WorkbenchSidebar({ activePage, activeUser, workspace, availableWorkspaces, isLoadingContext, contextError, onWorkspaceChange, onUserChange, onRefresh, spaceSwitchDisabled = false }: Props) {
  const [theme, setTheme] = useWorkbenchTheme();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => window.matchMedia?.("(max-width: 1023px)").matches ?? false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSpacePopoverOpen, setIsSpacePopoverOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
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
  const [draftWorkspace, setDraftWorkspace] = useState(workspace);
  const closeTimerRef = useRef<number | null>(null);
  const userZoneRef = useRef<HTMLDivElement>(null);
  const spacePopoverRef = useRef<HTMLElement>(null);
  const manageableWorkspace = canManageWorkspace(workspace);

  useEffect(() => {
    const media = window.matchMedia?.("(max-width: 1023px)");
    const sync = () => { setIsSidebarCollapsed(media?.matches ?? false); setIsUserMenuOpen(false); setIsSpacePopoverOpen(false); };
    media?.addEventListener?.("change", sync);
    return () => media?.removeEventListener?.("change", sync);
  }, []);
  useEffect(() => {
    const close = (event: globalThis.MouseEvent) => {
      const target = event.target as Node;
      if (userZoneRef.current?.contains(target) || spacePopoverRef.current?.contains(target)) return;
      setIsUserMenuOpen(false); setIsSpacePopoverOpen(false);
    };
    const escape = (event: globalThis.KeyboardEvent) => {
      if (event.key !== "Escape") return;
      setIsUserMenuOpen(false); setIsSpacePopoverOpen(false);
      setIsProfileModalOpen(false); setIsPasswordModalOpen(false); setIsSettingsOpen(false); setIsApplicationOpen(false);
      userZoneRef.current?.querySelector<HTMLButtonElement>(".rc-user-trigger")?.focus();
    };
    document.addEventListener("mousedown", close, true);
    document.addEventListener("keydown", escape);
    return () => { document.removeEventListener("mousedown", close, true); document.removeEventListener("keydown", escape); if (closeTimerRef.current) window.clearTimeout(closeTimerRef.current); };
  }, []);
  useEffect(() => { if (!toast) return; const timer = window.setTimeout(() => setToast(""), 2200); return () => window.clearTimeout(timer); }, [toast]);
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
      await onRefresh();
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
    onUserChange(nextFrontendUser);
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
    if (spaceSwitchDisabled) return;
    onWorkspaceChange(item);
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
    onWorkspaceChange(draftWorkspace);
    window.localStorage.setItem("moonbox.workspace", JSON.stringify(draftWorkspace));
    setIsSettingsOpen(false);
    setToast("空间设置已保存");
    void onRefresh();
  };

  const handleMenuKey = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === "Escape") {
      setIsUserMenuOpen(false);
      setIsSpacePopoverOpen(false);
    }
  };

  return <>
      <aside className={`rc-sidebar ${isSidebarCollapsed ? "collapsed" : ""}`}>
        <div className="rc-brand">
          <span className="rc-brand-mark">
            <img src="/brand/moonbox/moonbox-app-icon-256.png" alt="MoonBox 产品图标" />
          </span>
          {!isSidebarCollapsed && (
            <div className="rc-brand-copy">
              <strong>MoonBox</strong>
              <small>OPS WORKBENCH</small>
            </div>
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
                    className={`rc-nav-item ${(item.label === (activePage === "chat" ? "Chat 工作台" : "需求中心")) ? "active" : ""}`}
                    type="button"
                    title={item.title}
                    onClick={item.label === "Chat 工作台" || item.label === "需求中心" ? () => { window.location.href = item.label === "Chat 工作台" ? "/chat" : "/requirements"; } : undefined}
                    aria-current={(item.label === (activePage === "chat" ? "Chat 工作台" : "需求中心")) ? "page" : undefined}
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
              aria-label={`${activeUser.name} ${workspace.name} 用户菜单`}
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
            {isUserMenuOpen && (
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
                    onClick={() => setIsSpacePopoverOpen(value => !value)}
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
            {isSpacePopoverOpen && (
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
                      disabled={spaceSwitchDisabled}
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

      {isApplicationOpen && (
        <div className="rc-settings-mask workbench-overlay" role="presentation" onMouseDown={() => setIsApplicationOpen(false)}>
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
        <div className="rc-settings-mask workbench-overlay" role="presentation" onMouseDown={() => setIsSettingsOpen(false)}>
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

      {toast && <div className="rc-toast" role="status"><Check size={15} /> {toast}</div>}
  </>;
}
