import { ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { BookOpen, Check, Copy, KeyRound, LayoutDashboard, ListTree, LogOut, Network, Settings, SunMoon, UserRound, Users } from "lucide-react";
import { AdminCrudListTemplate, AdminModalBackdrop } from "./AdminCrudListTemplate";
import { AdminSession, logoutAdmin, readAdminSession } from "./adminAuth";

type Role = "后台管理员" | "前台用户";
type UserStatus = "待激活" | "正常" | "已冻结" | "已删除";
type UserStatusFilter = Exclude<UserStatus, "已删除">;
type UploadState = "idle" | "uploading" | "done" | "failed";

type AdminUser = {
  id: string;
  username: string;
  nickname: string | null;
  avatar_url: string | null;
  role: Role;
  status: UserStatus;
  status_before_freeze: Extract<UserStatus, "待激活" | "正常"> | null;
  workspace_count: number;
  last_login_at: string | null;
  is_system_superadmin: boolean;
  session_invalidated_at: string | null;
  created_at: string;
  updated_at: string;
};

type AdminUserListResponse = {
  items: AdminUser[];
  total: number;
  page: number;
  page_size: number;
};

type AdminUserCreateResponse = {
  user: AdminUser;
  temporary_password: string;
  message: string;
};

type TemporaryPasswordResult = {
  username: string;
  password: string;
  source: "create" | "reset";
};

const nowText = () => new Date().toISOString().slice(0, 19).replace("T", " ");

const apiUrl = (path: string) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
  return `${baseUrl}${path}`;
};

const authHeaders = () => {
  const session = readAdminSession();
  if (!session?.access_token) {
    throw new Error("登录已失效，请重新登录");
  }
  return { authorization: `Bearer ${session.access_token}` };
};

async function readApiError(response: Response, fallback: string) {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || fallback;
  } catch {
    return fallback;
  }
}

async function requestAdminApi<T>(path: string, init: RequestInit = {}, fallback = "操作失败，请重试") {
  const response = await fetch(apiUrl(path), {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init.body instanceof FormData ? {} : { "content-type": "application/json" }),
      ...init.headers,
    },
  });
  if (!response.ok) {
    throw new Error(await readApiError(response, fallback));
  }
  const payload = await response.json();
  return payload.data as T;
}

const initials = (user: Pick<AdminUser, "username" | "nickname">) => {
  const name = user.nickname || user.username;
  return name.slice(0, 2).toUpperCase();
};

export function AdminUserManagementPage({ session, onLogout }: { session?: AdminSession | null; onLogout?: () => void }) {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [query, setQuery] = useState("");
  const [role, setRole] = useState<"全部角色" | Role>("全部角色");
  const [status, setStatus] = useState<"全部状态" | UserStatusFilter>("全部状态");
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isLightTheme, setIsLightTheme] = useState(false);
  const [editing, setEditing] = useState<AdminUser | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [pendingAction, setPendingAction] = useState<{ user: AdminUser; action: "freeze" | "unfreeze" | "delete" | "reset" } | null>(null);
  const [temporaryPassword, setTemporaryPassword] = useState<TemporaryPasswordResult | null>(null);
  const [toast, setToast] = useState("");

  const pageCount = Math.max(1, Math.ceil(totalUsers / pageSize));
  const visibleUsers = users;

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2400);
  };

  const loadUsers = useCallback(async () => {
    setIsLoadingUsers(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
      if (query.trim()) params.set("q", query.trim());
      if (role !== "全部角色") params.set("role", role);
      if (status !== "全部状态") params.set("status", status);
      const data = await requestAdminApi<AdminUserListResponse>(`/api/v1/admin/users?${params.toString()}`, { method: "GET" }, "用户列表加载失败，请重试");
      const items = Array.isArray(data.items) ? data.items : [];
      const total = Number.isFinite(data.total) ? data.total : items.length;
      setUsers(items);
      setTotalUsers(total);
      const nextPageCount = Math.max(1, Math.ceil(total / pageSize));
      if (page > nextPageCount) setPage(nextPageCount);
    } catch (error) {
      showToast(error instanceof Error ? error.message : "用户列表加载失败，请重试");
    } finally {
      setIsLoadingUsers(false);
    }
  }, [page, pageSize, query, role, status]);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const exitAdmin = async () => {
    await logoutAdmin();
    showToast("已退出登录");
    onLogout?.();
  };

  const saveUser = async (user: AdminUser) => {
    try {
      if (isCreating) {
        const result = await requestAdminApi<AdminUserCreateResponse>(
          "/api/v1/admin/users",
          {
            method: "POST",
            body: JSON.stringify({ username: user.username, nickname: user.nickname || null, avatar_url: user.avatar_url, role: user.role }),
          },
          "用户创建失败，请重试",
        );
        setTemporaryPassword({ username: result.user.username, password: result.temporary_password, source: "create" });
      } else {
        await requestAdminApi<AdminUser>(
          `/api/v1/admin/users/${user.id}`,
          {
            method: "PUT",
            body: JSON.stringify({ nickname: user.nickname || null, avatar_url: user.avatar_url, role: user.role }),
          },
          "用户信息更新失败，请重试",
        );
        showToast("用户信息已更新");
      }
      setIsCreating(false);
      setEditing(null);
      void loadUsers();
    } catch (error) {
      showToast(error instanceof Error ? error.message : "用户保存失败，请重试");
    }
  };

  const applyAction = async (reason: string) => {
    if (!pendingAction) return;
    const { user, action } = pendingAction;
    try {
      if (action === "reset") {
        const result = await requestAdminApi<{ temporary_password: string; message: string }>(
          `/api/v1/admin/users/${user.id}/reset-password`,
          {
            method: "POST",
            body: JSON.stringify({ reason }),
          },
          "密码重置失败，请重试",
        );
        setTemporaryPassword({ username: user.username, password: result.temporary_password, source: "reset" });
      } else {
        const actionPath = action === "freeze" ? "freeze" : action === "unfreeze" ? "unfreeze" : "";
        await requestAdminApi<AdminUser>(
          action === "delete" ? `/api/v1/admin/users/${user.id}` : `/api/v1/admin/users/${user.id}/${actionPath}`,
          {
            method: action === "delete" ? "DELETE" : "POST",
            body: JSON.stringify({ reason }),
          },
          "用户状态更新失败，请重试",
        );
        const restoredStatus = action === "unfreeze" ? restoreTargetLabel(user) : "";
        showToast(`${user.username} 已${action === "freeze" ? "冻结，10 秒内会话失效" : action === "unfreeze" ? `解冻，恢复为${restoredStatus}` : "删除"}`);
      }
      setPendingAction(null);
      void loadUsers();
    } catch (error) {
      showToast(error instanceof Error ? error.message : "操作失败，请重试");
    }
  };

  const currentUsername = session?.user.username || "admin";
  const userColumns = [
    { key: "user", label: "用户" },
    { key: "workspace", label: "空间数" },
    { key: "role", label: "角色" },
    { key: "status", label: "状态" },
    { key: "status_before_freeze", label: "冻结前状态" },
    { key: "last_login", label: "最近登录时间" },
    { key: "created", label: "创建时间" },
    { key: "actions", label: "操作" },
  ];

  return (
    <main className={`admin-shell ${isCollapsed ? "collapsed" : ""} ${isLightTheme ? "light" : ""}`} data-theme={isLightTheme ? "light" : "dark"}>
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <span className="admin-mark">
            <img src="/brand/moonbox/moonbox-app-icon-256.png" alt="MoonBox 产品图标" />
          </span>
          <div className="admin-brand-name">
            <strong>MoonBox</strong>
            <small>PLATFORM OPS</small>
          </div>
          <em>v1.0.5</em>
          <button
            className="admin-collapse"
            aria-label={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
            title={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
            onClick={() => setIsCollapsed((value) => !value)}
          >
            {isCollapsed ? "›" : "‹"}
          </button>
        </div>
        <nav aria-label="管理后台导航">
          <span className="admin-nav-group">OPERATIONS</span>
          <button title="首页"><LayoutDashboard className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">首页</span></button>
          <button title="空间管理"><Network className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">空间管理</span></button>
          <span className="admin-nav-group">SYSTEM</span>
          <button className="active" title="用户管理"><Users className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">用户管理</span></button>
          <button title="系统设置"><Settings className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">系统设置</span></button>
          <button title="日志审计"><ListTree className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">日志审计</span></button>
          <button title="接口文档"><BookOpen className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">接口文档</span></button>
        </nav>
        <div className="admin-sidebar-user">
          {isUserMenuOpen && (
            <div className="admin-user-menu" role="menu">
              <button role="menuitem" onClick={() => showToast("个人资料页面已打开")}><UserRound className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>个人资料</span></button>
              <button role="menuitem" onClick={() => showToast("密码修改页面已打开")}><KeyRound className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>密码修改</span></button>
              <button
                type="button"
                className="admin-theme-row"
                role="switch"
                aria-label="切换明暗主题"
                aria-checked={isLightTheme}
                onClick={() => {
                  const nextTheme = !isLightTheme;
                  setIsLightTheme(nextTheme);
                  showToast(`已切换为${nextTheme ? "亮色" : "暗色"}主题`);
                }}
              >
                <SunMoon className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                <span>界面主题</span>
                <span className={`admin-theme-switch ${isLightTheme ? "on" : ""}`} aria-hidden="true" />
              </button>
              <button role="menuitem" className="logout" onClick={exitAdmin}><LogOut className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>退出登录</span></button>
            </div>
          )}
          <button className="admin-user-trigger" onClick={() => setIsUserMenuOpen((value) => !value)} aria-expanded={isUserMenuOpen}>
            <span className="admin-avatar">吴</span>
            <span className="admin-user-meta">
              <strong>{currentUsername}</strong>
              <small>{session?.user.is_system_superadmin ? "超级管理员" : "后台管理员"}</small>
            </span>
            <span className="admin-user-chevron">⌃</span>
          </button>
        </div>
      </aside>
      <AdminCrudListTemplate
        eyebrow="User Management"
        title="用户管理"
        description="统一管理平台用户、角色生命周期"
        primaryAction={
          <button className="admin-btn admin-primary" onClick={() => {
              setIsCreating(true);
              setEditing({
                id: `user_${Date.now()}`,
                username: "",
                nickname: "",
                avatar_url: null,
                role: "前台用户",
                status: "待激活",
                status_before_freeze: null,
                workspace_count: 0,
                last_login_at: null,
                is_system_superadmin: false,
                session_invalidated_at: null,
                created_at: nowText(),
                updated_at: nowText(),
              });
            }}>
              新增用户
            </button>
        }
        filters={[
          {
            id: "query",
            node: (
              <input
                aria-label="搜索用户"
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setPage(1);
                }}
                placeholder="用户名或昵称"
              />
            ),
          },
          {
            id: "role",
            node: (
              <select aria-label="角色筛选" value={role} onChange={(event) => setRole(event.target.value as typeof role)}>
                <option>全部角色</option>
                <option>后台管理员</option>
                <option>前台用户</option>
              </select>
            ),
          },
          {
            id: "status",
            node: (
              <select aria-label="状态筛选" value={status} onChange={(event) => setStatus(event.target.value as typeof status)}>
                <option>全部状态</option>
                <option>待激活</option>
                <option>正常</option>
                <option>已冻结</option>
              </select>
            ),
          },
        ]}
        columns={userColumns}
        tableClassName="admin-account-table"
        colgroup={
          <colgroup>
            <col className="admin-col-user" />
            <col className="admin-col-workspace" />
            <col className="admin-col-role" />
            <col className="admin-col-status" />
            <col className="admin-col-before-freeze" />
            <col className="admin-col-login" />
            <col className="admin-col-created" />
            <col className="admin-col-actions" />
          </colgroup>
        }
        isLoading={isLoadingUsers}
        loadingText="正在加载用户..."
        emptyText="暂无匹配用户"
        rowCount={visibleUsers.length}
        pagination={{
          label: "用户列表分页",
          totalLabel: "共",
          total: totalUsers,
          totalUnit: "个用户",
          page,
          pageCount,
          pageSize,
          pageSizeOptions: [10, 20, 50, 100],
          onPageChange: setPage,
          onPageSizeChange: (nextPageSize) => {
            setPageSize(nextPageSize);
            setPage(1);
          },
        }}
        toast={toast}
      >
        {visibleUsers.map((user) => (
                <tr key={user.id}>
                  <td>
                    <div className="admin-user-cell">
                      <span className="admin-avatar">{user.avatar_url ? <img src={user.avatar_url} alt={`${user.username} 头像`} /> : initials(user)}</span>
                      <span>
                        <span className="admin-user-name-line">
                          <strong>{user.username}</strong>
                          {user.is_system_superadmin && <em title="由部署环境初始化">系统内置</em>}
                        </span>
                        <small>{user.nickname || "未设置昵称"}</small>
                      </span>
                    </div>
                  </td>
                  <td>{user.workspace_count}</td>
                  <td>{user.role}</td>
                  <td><span className={`admin-status ${user.status}`} data-testid="admin-user-status-badge">{user.status}</span></td>
                  <td data-testid="admin-user-status-before-freeze">{user.status === "已冻结" ? restoreTargetLabel(user) : "—"}</td>
                  <td className="admin-date-cell">{user.last_login_at || "—"}</td>
                  <td className="admin-date-cell">{user.created_at}</td>
                  <td>
                    {user.is_system_superadmin || user.status === "已删除" ? (
                      <span className="admin-protected">不可操作</span>
                    ) : (
                      <div className="admin-operation-set">
                        <button onClick={() => { setIsCreating(false); setEditing(user); }}>编辑</button>
                        <button onClick={() => setPendingAction({ user, action: "reset" })}>重置密码</button>
                        <button data-testid={user.status === "已冻结" ? "admin-user-unfreeze-action" : "admin-user-freeze-action"} onClick={() => setPendingAction({ user, action: user.status === "已冻结" ? "unfreeze" : "freeze" })}>
                          {user.status === "已冻结" ? "解冻" : "冻结"}
                        </button>
                        <button className="danger-text" onClick={() => setPendingAction({ user, action: "delete" })}>删除</button>
                      </div>
                    )}
                  </td>
                </tr>
        ))}
      </AdminCrudListTemplate>
      {editing && <UserFormModal user={editing} isCreating={isCreating} onSave={saveUser} onClose={() => setEditing(null)} />}
      {pendingAction && <ConfirmModal action={pendingAction.action} user={pendingAction.user} onCancel={() => setPendingAction(null)} onConfirm={applyAction} />}
      {temporaryPassword && (
        <TemporaryPasswordModal
          result={temporaryPassword}
          onCopied={() => showToast("临时密码已复制")}
          onClose={() => setTemporaryPassword(null)}
        />
      )}
    </main>
  );
}

function restoreTargetLabel(user: AdminUser) {
  return user.status_before_freeze || "待确认";
}

function UserFormModal({ user, isCreating, onSave, onClose }: {
  user: AdminUser;
  isCreating: boolean;
  onSave: (user: AdminUser) => Promise<void>;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState(user);
  const [isSaving, setIsSaving] = useState(false);
  const [uploadState, setUploadState] = useState<UploadState>("idle");
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(user.avatar_url);
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const validUsername = /^[A-Za-z][A-Za-z0-9]{3,31}$/.test(draft.username);
  const showUsernameError = isCreating && draft.username.length > 0 && !validUsername;
  const avatarButtonText = uploadState === "uploading" ? "上传中" : draft.avatar_url ? "更换" : "上传";

  const uploadAvatar = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadState("uploading");
    const session = readAdminSession();
    try {
      if (!session?.access_token) {
        throw new Error("未登录");
      }
      const formData = new FormData();
      formData.append("file", file);
      const response = await fetch(apiUrl("/api/v1/admin/users/avatar"), {
        method: "POST",
        headers: { authorization: `Bearer ${session.access_token}` },
        body: formData,
      });
      if (!response.ok) {
        throw new Error(await readUploadError(response));
      }
      const payload = await response.json();
      const mediaResponse = await fetch(apiUrl(payload.data.url), {
        headers: { authorization: `Bearer ${session.access_token}` },
      });
      if (!mediaResponse.ok) {
        throw new Error(await readUploadError(mediaResponse));
      }
      const objectUrl = URL.createObjectURL(await mediaResponse.blob());
      setDraft((current) => ({ ...current, avatar_url: objectUrl }));
      setAvatarPreviewUrl(objectUrl);
      setUploadError("");
      setUploadState("done");
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "头像上传失败，请重试");
      setUploadState("failed");
    } finally {
      event.target.value = "";
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!validUsername || isSaving) return;
    setIsSaving(true);
    try {
      await onSave({ ...draft, updated_at: nowText() });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AdminModalBackdrop>
      <form className="admin-user-modal" aria-label={isCreating ? "新增用户" : "编辑用户"} onSubmit={submit}>
        <h2>{isCreating ? "新增用户" : "编辑用户"}</h2>
        <div className="admin-form-row">
          <label className="required" htmlFor="admin-user-username"><span>用户名</span></label>
          <input id="admin-user-username" value={draft.username} disabled={!isCreating} onChange={(event) => setDraft({ ...draft, username: event.target.value })} />
          <div className="admin-form-hint">系统唯一，4-32 位；仅允许字母、数字，且必须以字母开头。创建后不可修改。</div>
          {showUsernameError && <div className="admin-form-error">请输入 4-32 位字母或数字，且以字母开头。</div>}
        </div>
        <div className="admin-form-row">
          <label><span>头像</span></label>
          <div className="admin-avatar-picker">
            <span className="admin-avatar large">{avatarPreviewUrl ? <img src={avatarPreviewUrl} alt="头像预览" /> : initials(draft)}</span>
            <span className="admin-avatar-copy">
              <small>支持 JPG、PNG，建议 1:1</small>
              <button type="button" aria-label="上传或更换头像" disabled={uploadState === "uploading"} onClick={() => fileInputRef.current?.click()}>
                {avatarButtonText}
              </button>
            </span>
            <input ref={fileInputRef} className="admin-avatar-file" type="file" accept="image/jpeg,image/png,image/webp" aria-label="选择头像文件" onChange={uploadAvatar} />
          </div>
          {uploadState === "failed" && <div className="admin-form-error">{uploadError}</div>}
        </div>
        <div className="admin-form-row">
          <label htmlFor="admin-user-nickname"><span>昵称</span></label>
          <input id="admin-user-nickname" value={draft.nickname || ""} onChange={(event) => setDraft({ ...draft, nickname: event.target.value })} />
        </div>
        <div className="admin-form-row">
          <label className="required" htmlFor="admin-user-role"><span>角色</span></label>
          <select id="admin-user-role" value={draft.role} onChange={(event) => setDraft({ ...draft, role: event.target.value as Role })}>
            <option>前台用户</option>
            <option>后台管理员</option>
          </select>
        </div>
        <footer className="admin-drawer-actions">
          <button type="button" onClick={onClose}>取消</button>
          <button className="admin-primary" type="submit" disabled={!validUsername || uploadState === "uploading" || isSaving}>
            {isSaving ? "保存中" : "保存"}
          </button>
        </footer>
      </form>
    </AdminModalBackdrop>
  );
}

async function readUploadError(response: Response) {
  try {
    const payload = await response.json();
    return payload.detail || payload.message || "头像上传失败，请重试";
  } catch {
    return "头像上传失败，请重试";
  }
}

function ConfirmModal({ action, user, onCancel, onConfirm }: {
  action: "freeze" | "unfreeze" | "delete" | "reset";
  user: AdminUser;
  onCancel: () => void;
  onConfirm: (reason: string) => void;
}) {
  const [reason, setReason] = useState("");
  const showReasonError = reason.length > 0 && reason.trim().length < 4;
  const title = action === "freeze" ? "冻结用户" : action === "unfreeze" ? "解冻用户" : action === "delete" ? "删除用户" : "重置密码";
  const actionDescription =
    action === "freeze"
      ? "冻结成功后，目标用户全部有效会话将在 10 秒内失效。"
      : action === "unfreeze"
        ? `解冻后恢复为${restoreTargetLabel(user)}，不会替用户完成首次激活。`
        : "该操作将写入不可篡改审计记录。";
  return (
    <AdminModalBackdrop>
      <section className="admin-confirm-modal" aria-label={title} data-testid={action === "unfreeze" ? "admin-user-unfreeze-modal" : undefined}>
        <h2>{title}</h2>
        <p>{actionDescription}</p>
        {action === "unfreeze" && (
          <p className="admin-restore-target" data-testid="admin-user-unfreeze-restore-target">恢复目标状态：{restoreTargetLabel(user)}</p>
        )}
        <div className="admin-form-row">
          <label htmlFor="admin-action-reason"><span>操作原因</span></label>
          <textarea id="admin-action-reason" value={reason} onChange={(event) => setReason(event.target.value)} />
          <div className="admin-form-hint">请填写至少 4 个字，便于审计追踪。</div>
          {showReasonError && <div className="admin-form-error">操作原因至少需要 4 个字。</div>}
        </div>
        <footer>
          <button onClick={onCancel}>取消</button>
          <button className="admin-primary" disabled={reason.trim().length < 4} onClick={() => onConfirm(reason)}>确认</button>
        </footer>
      </section>
    </AdminModalBackdrop>
  );
}

function TemporaryPasswordModal({ result, onCopied, onClose }: {
  result: TemporaryPasswordResult;
  onCopied: () => void;
  onClose: () => void;
}) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState("");
  const copyPassword = async () => {
    try {
      await navigator.clipboard.writeText(result.password);
      setCopied(true);
      setCopyError("");
      onCopied();
    } catch {
      setCopyError("复制失败，请手动选择密码复制。");
    }
  };

  return (
    <AdminModalBackdrop>
      <section className="admin-password-modal" aria-label="临时密码">
        <h2>{result.source === "create" ? "用户创建成功" : "密码重置成功"}</h2>
        <p>{result.username} 的临时密码仅展示一次，请立即复制并通过安全渠道发送给用户。</p>
        <p className="admin-form-hint">该临时密码可用于后台管理员账号首次登录激活或正常登录；前台用户、已冻结或已删除账号无法登录后台。</p>
        <div className="admin-password-copy" role="group" aria-label="一次性临时密码">
          <code>{result.password}</code>
          <button type="button" onClick={copyPassword}>
            {copied ? <Check className="admin-menu-icon" size={14} strokeWidth={1.6} aria-hidden="true" /> : <Copy className="admin-menu-icon" size={14} strokeWidth={1.6} aria-hidden="true" />}
            <span>{copied ? "已复制" : "复制"}</span>
          </button>
        </div>
        <div className="admin-form-hint">关闭后将无法再次查看该密码，请确认已妥善保存。系统不会在前端持久化保存临时密码。</div>
        {copyError && <div className="admin-form-error">{copyError}</div>}
        <footer>
          <button className="admin-primary" type="button" onClick={onClose}>关闭</button>
        </footer>
      </section>
    </AdminModalBackdrop>
  );
}
