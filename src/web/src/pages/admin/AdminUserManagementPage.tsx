import { ChangeEvent, FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { Check, CheckCircle2, CircleDashed, Copy, Eye, EyeOff, ShieldCheck, Snowflake, Trash2, UserRound, X } from "lucide-react";
import { AdminCrudListTemplate, AdminModalBackdrop } from "./AdminCrudListTemplate";
import { AdminSelect } from "./AdminSelect";
import { AdminSession, changeAdminPassword, logoutAdmin, readAdminSession, saveAdminSession, updateAdminProfile } from "./adminAuth";
import { AdminSidebar, AuthenticatedAvatar, avatarImageSrc, initials } from "./AdminSidebar";
import { readUiPreferences, UI_PREFERENCES_EVENT } from "../home/uiPreferences";

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

const hasLegacyAvatarUrl = (avatarUrl: string | null | undefined) =>
  Boolean(avatarUrl?.startsWith("/api/v1/admin/users/avatar/"));

const padDatePart = (value: number) => String(value).padStart(2, "0");

function formatAdminDateTime(value: string | null | undefined) {
  if (!value) return "—";
  const matched = value.match(/^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}:\d{2})/);
  if (matched) return `${matched[1]} ${matched[2]}`;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return [
    `${date.getFullYear()}-${padDatePart(date.getMonth() + 1)}-${padDatePart(date.getDate())}`,
    `${padDatePart(date.getHours())}:${padDatePart(date.getMinutes())}:${padDatePart(date.getSeconds())}`,
  ].join(" ");
}

const roleMeta: Record<Role, { className: string; icon: typeof ShieldCheck }> = {
  后台管理员: { className: "admin-role-admin", icon: ShieldCheck },
  前台用户: { className: "admin-role-user", icon: UserRound },
};

function AdminRoleTag({ role }: { role: Role }) {
  const meta = roleMeta[role];
  const Icon = meta.icon;
  return (
    <span className={`admin-role-tag ${meta.className}`} data-testid="admin-user-role-tag">
      <Icon size={14} strokeWidth={1.7} aria-hidden="true" />
      {role}
    </span>
  );
}

const statusMeta: Record<UserStatus, { className: string; icon: typeof CheckCircle2 }> = {
  待激活: { className: "admin-status-pending", icon: CircleDashed },
  正常: { className: "admin-status-active", icon: CheckCircle2 },
  已冻结: { className: "admin-status-frozen", icon: Snowflake },
  已删除: { className: "admin-status-deleted", icon: Trash2 },
};

function AdminStatusBadge({ status }: { status: UserStatus }) {
  const meta = statusMeta[status];
  const Icon = meta.icon;
  return (
    <span className={`admin-status ${meta.className}`} data-testid="admin-user-status-badge">
      <Icon size={14} strokeWidth={1.8} aria-hidden="true" />
      {status}
    </span>
  );
}

type CurrentUserResponse = {
  user: AdminSession["user"];
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
  const [isLightTheme, setIsLightTheme] = useState(() => readUiPreferences().theme === "light");
  const [editing, setEditing] = useState<AdminUser | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [pendingAction, setPendingAction] = useState<{ user: AdminUser; action: "freeze" | "unfreeze" | "delete" | "reset" } | null>(null);
  const [temporaryPassword, setTemporaryPassword] = useState<TemporaryPasswordResult | null>(null);
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [currentSessionUser, setCurrentSessionUser] = useState<AdminSession["user"] | null>(session?.user ?? readAdminSession()?.user ?? null);
  const [toast, setToast] = useState("");

  const pageCount = Math.max(1, Math.ceil(totalUsers / pageSize));
  const visibleUsers = users;

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2400);
  };

  const refreshCurrentUser = useCallback(async () => {
    const storedSession = readAdminSession();
    if (!storedSession?.access_token) return;
    if (!hasLegacyAvatarUrl(storedSession.user?.avatar_url)) {
      setCurrentSessionUser(storedSession.user);
      return;
    }
    try {
      const data = await requestAdminApi<CurrentUserResponse>("/api/v1/auth/me", { method: "GET" }, "当前用户刷新失败，请重试");
      const nextSession = { ...storedSession, user: data.user };
      saveAdminSession(nextSession);
      setCurrentSessionUser(data.user);
    } catch {
      setCurrentSessionUser(storedSession.user);
    }
  }, []);

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

  useEffect(() => {
    setCurrentSessionUser(session?.user ?? readAdminSession()?.user ?? null);
  }, [session]);

  useEffect(() => {
    void refreshCurrentUser();
  }, [refreshCurrentUser]);

  useEffect(() => {
    const syncTheme = () => setIsLightTheme(readUiPreferences().theme === "light");
    window.addEventListener(UI_PREFERENCES_EVENT, syncTheme);
    window.addEventListener("storage", syncTheme);
    return () => {
      window.removeEventListener(UI_PREFERENCES_EVENT, syncTheme);
      window.removeEventListener("storage", syncTheme);
    };
  }, []);

  const exitAdmin = async () => {
    await logoutAdmin();
    showToast("已退出登录");
    onLogout?.();
  };

  const returnFrontend = () => {
    setIsUserMenuOpen(false);
    navigateTo("/requirements");
  };

  const navigateTo = (path: string) => {
    window.history.pushState(null, "", path);
    window.dispatchEvent(new PopStateEvent("popstate"));
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
        const updatedUser = await requestAdminApi<AdminUser>(
          `/api/v1/admin/users/${user.id}`,
          {
            method: "PUT",
            body: JSON.stringify({ nickname: user.nickname || null, avatar_url: user.avatar_url, role: user.role }),
          },
          "用户信息更新失败，请重试",
        );
        if (currentSessionUser?.id === updatedUser.id) {
          const nextSessionUser = {
            ...currentSessionUser,
            username: updatedUser.username,
            nickname: updatedUser.nickname,
            avatar_url: updatedUser.avatar_url,
            role: updatedUser.role,
            status: updatedUser.status,
            is_system_superadmin: updatedUser.is_system_superadmin,
          };
          setCurrentSessionUser(nextSessionUser);
          const currentSession = readAdminSession();
          if (currentSession?.access_token) {
            saveAdminSession({ ...currentSession, user: nextSessionUser });
          }
        }
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

  const currentUsername = currentSessionUser?.username || "admin";
  const currentDisplayName = currentSessionUser?.nickname || currentUsername;
  const currentUserRole = currentSessionUser?.is_system_superadmin ? "超级管理员" : "后台管理员";
  const userColumns = [
    { key: "user", label: "用户" },
    { key: "workspace", label: "空间数" },
    { key: "role", label: "角色" },
    { key: "status", label: "状态" },
    { key: "status_before_freeze", label: "冻结前状态" },
    { key: "last_login", label: "最近登录时间" },
    { key: "created", label: "创建时间" },
    { key: "updated", label: "更新时间" },
    { key: "actions", label: "操作" },
  ];

  return (
    <main className={`admin-shell ${isCollapsed ? "collapsed" : ""} ${isLightTheme ? "light" : ""}`} data-theme={isLightTheme ? "light" : "dark"}>
      <AdminSidebar
        active="users"
        currentUser={currentSessionUser}
        isCollapsed={isCollapsed}
        isLightTheme={isLightTheme}
        isUserMenuOpen={isUserMenuOpen}
        onToggleCollapse={() => setIsCollapsed((value) => !value)}
        onToggleUserMenu={() => setIsUserMenuOpen((value) => !value)}
        onCloseUserMenu={() => setIsUserMenuOpen(false)}
        onNavigate={navigateTo}
        onOpenProfile={() => setIsProfileModalOpen(true)}
        onOpenPassword={() => setIsPasswordModalOpen(true)}
        onThemeChange={setIsLightTheme}
        onLogout={exitAdmin}
        onToast={showToast}
      />
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
              <AdminSelect
                ariaLabel="角色筛选"
                value={role}
                options={[
                  { value: "全部角色", label: "全部角色" },
                  { value: "后台管理员", label: "后台管理员" },
                  { value: "前台用户", label: "前台用户" },
                ]}
                onChange={(value) => setRole(value as typeof role)}
              />
            ),
          },
          {
            id: "status",
            node: (
              <AdminSelect
                ariaLabel="状态筛选"
                value={status}
                options={[
                  { value: "全部状态", label: "全部状态" },
                  { value: "待激活", label: "待激活" },
                  { value: "正常", label: "正常" },
                  { value: "已冻结", label: "已冻结" },
                ]}
                onChange={(value) => setStatus(value as typeof status)}
              />
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
            <col className="admin-col-updated" />
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
        {visibleUsers.map((user) => {
          const isCurrentUser = currentSessionUser?.id === user.id;
          const isProtectedUser = user.is_system_superadmin || user.status === "已删除";
          return (
                <tr key={user.id}>
                  <td>
                    <div className="admin-user-cell">
                      <AuthenticatedAvatar avatarUrl={user.avatar_url} alt={`${user.username} 头像`} fallback={initials(user)} />
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
                  <td><AdminRoleTag role={user.role} /></td>
                  <td><AdminStatusBadge status={user.status} /></td>
                  <td data-testid="admin-user-status-before-freeze">{user.status === "已冻结" ? restoreTargetLabel(user) : "—"}</td>
                  <td className="admin-date-cell">{formatAdminDateTime(user.last_login_at)}</td>
                  <td className="admin-date-cell">{formatAdminDateTime(user.created_at)}</td>
                  <td className="admin-date-cell">{formatAdminDateTime(user.updated_at)}</td>
                  <td>
	                    {isProtectedUser ? (
	                      <span className="admin-protected">不可操作</span>
	                    ) : (
	                      <div className="admin-operation-set">
	                        <button onClick={() => { setIsCreating(false); setEditing(user); }}>编辑</button>
	                        <button onClick={() => setPendingAction({ user, action: "reset" })}>重置密码</button>
                        <button
                          data-testid={user.status === "已冻结" ? "admin-user-unfreeze-action" : "admin-user-freeze-action"}
                          disabled={isCurrentUser}
                          title={isCurrentUser ? "不能冻结当前登录账号" : undefined}
                          onClick={() => setPendingAction({ user, action: user.status === "已冻结" ? "unfreeze" : "freeze" })}
                        >
                          {user.status === "已冻结" ? "解冻" : "冻结"}
                        </button>
                        <button
                          className="danger-text"
                          disabled={isCurrentUser}
                          title={isCurrentUser ? "不能删除当前登录账号" : undefined}
                          onClick={() => setPendingAction({ user, action: "delete" })}
                        >
                          删除
                        </button>
                      </div>
                    )}
	                  </td>
	                </tr>
          );
        })}
      </AdminCrudListTemplate>
      {editing && <UserFormModal user={editing} isCreating={isCreating} onSave={saveUser} onClose={() => setEditing(null)} />}
      {pendingAction && <ConfirmModal action={pendingAction.action} user={pendingAction.user} onCancel={() => setPendingAction(null)} onConfirm={applyAction} />}
      {isProfileModalOpen && currentSessionUser && (
        <ProfileModal
          user={currentSessionUser}
          roleLabel={currentUserRole}
          onClose={() => setIsProfileModalOpen(false)}
          onSaved={(nextUser) => {
            setCurrentSessionUser(nextUser);
            setUsers((currentUsers) => currentUsers.map((item) => (
              item.id === nextUser.id
                ? { ...item, nickname: nextUser.nickname ?? null, avatar_url: nextUser.avatar_url ?? null, updated_at: nowText() }
                : item
            )));
            setIsProfileModalOpen(false);
            showToast("个人资料已更新");
          }}
        />
      )}
      {isPasswordModalOpen && (
        <ChangePasswordModal
          onClose={() => setIsPasswordModalOpen(false)}
          onChanged={() => {
            setIsPasswordModalOpen(false);
            showToast("密码已更新，请重新登录");
            onLogout?.();
          }}
        />
      )}
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

export function ProfileModal({ user, roleLabel, onClose, onSaved }: {
  user: AdminSession["user"];
  roleLabel: string;
  onClose: () => void;
  onSaved: (user: AdminSession["user"]) => void;
}) {
  const [nickname, setNickname] = useState(user.nickname || "");
  const [avatarUrl, setAvatarUrl] = useState<string | null>(user.avatar_url || null);
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(avatarImageSrc(user.avatar_url));
  const [uploadState, setUploadState] = useState<UploadState>("idle");
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
      if (!response.ok) throw new Error(await readUploadError(response));
      const payload = await response.json();
      const persistentUrl = payload.data.url as string;
      const mediaResponse = await fetch(apiUrl(persistentUrl), {
        headers: { authorization: `Bearer ${session.access_token}` },
      });
      if (!mediaResponse.ok) throw new Error(await readUploadError(mediaResponse));
      const objectUrl = URL.createObjectURL(await mediaResponse.blob());
      setAvatarUrl(persistentUrl);
      setAvatarPreviewUrl(objectUrl);
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
    <AdminModalBackdrop>
      <form className="admin-profile-modal" aria-label="个人资料" onSubmit={submit}>
        <header className="admin-profile-head">
          <h2>个人资料</h2>
          <button aria-label="关闭个人资料" type="button" onClick={onClose}>
            <X size={17} />
          </button>
        </header>
        <p className="admin-profile-summary">{user.username}</p>
        <div className="admin-form-row">
          <label><span>头像</span></label>
          <div className="admin-avatar-picker">
            <AuthenticatedAvatar avatarUrl={avatarPreviewUrl} alt="头像预览" fallback={initials({ username: user.username, nickname })} className="admin-avatar large" />
            <span className="admin-avatar-copy">
              <small>支持 JPG、PNG、WEBP，建议 1:1，最大 2MB</small>
              <button type="button" aria-label="上传或更换头像" disabled={uploadState === "uploading" || isSaving} onClick={() => fileInputRef.current?.click()}>
                {avatarButtonText}
              </button>
            </span>
            <input ref={fileInputRef} className="admin-avatar-file" type="file" accept="image/jpeg,image/png,image/webp" aria-label="选择头像文件" onChange={uploadAvatar} />
          </div>
          {uploadState === "failed" && <div className="admin-form-error" aria-live="polite">{uploadError}</div>}
        </div>
        <div className="admin-form-row">
          <label htmlFor="admin-profile-nickname"><span>昵称</span></label>
          <input id="admin-profile-nickname" maxLength={128} value={nickname} onChange={(event) => setNickname(event.target.value)} />
        </div>
        {saveError && <div className="admin-form-error" aria-live="polite">{saveError}</div>}
        <footer>
          <button type="button" onClick={onClose}>取消</button>
          <button className="admin-primary" type="submit" disabled={uploadState === "uploading" || isSaving}>
            {isSaving ? "保存中" : "保存"}
          </button>
        </footer>
      </form>
    </AdminModalBackdrop>
  );
}

export function ChangePasswordModal({ onClose, onChanged }: { onClose: () => void; onChanged: () => void }) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [visibleFields, setVisibleFields] = useState({ current: false, next: false, confirm: false });
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const passwordsMismatch = confirmPassword.length > 0 && newPassword !== confirmPassword;
  const canSubmit = currentPassword.length > 0 && newPassword.length > 0 && confirmPassword.length > 0 && !passwordsMismatch && !isSubmitting;

  const toggleVisibility = (field: keyof typeof visibleFields) => {
    setVisibleFields((current) => ({ ...current, [field]: !current[field] }));
  };

  const updatePasswordField = (setter: (value: string) => void) => (value: string) => {
    setter(value);
    if (error) setError("");
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("请完整填写当前密码、新密码和确认新密码。");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("两次输入的新密码不一致。");
      return;
    }
    setIsSubmitting(true);
    setError("");
    try {
      await changeAdminPassword(currentPassword, newPassword, confirmPassword);
      onChanged();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "密码修改失败，请重试。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AdminModalBackdrop>
      <form className="admin-change-password-modal" aria-label="修改密码" onSubmit={submit}>
        <h2>修改密码</h2>
        <p>更新成功后，当前账号的旧会话将全部失效，需要重新登录。</p>
        <div className="admin-form-row">
          <label className="required" htmlFor="admin-current-password"><span>当前密码</span></label>
          <PasswordInputWithToggle
            id="admin-current-password"
            label="当前密码"
            autoComplete="current-password"
            value={currentPassword}
            isVisible={visibleFields.current}
            onChange={updatePasswordField(setCurrentPassword)}
            onToggle={() => toggleVisibility("current")}
          />
        </div>
        <div className="admin-form-row">
          <label className="required" htmlFor="admin-new-password"><span>新密码</span></label>
          <PasswordInputWithToggle
            id="admin-new-password"
            label="新密码"
            autoComplete="new-password"
            value={newPassword}
            isVisible={visibleFields.next}
            onChange={updatePasswordField(setNewPassword)}
            onToggle={() => toggleVisibility("next")}
          />
          <div className="admin-form-hint">至少 12 位，并包含字母、数字和符号；不能使用示例密码或当前密码。</div>
        </div>
        <div className="admin-form-row">
          <label className="required" htmlFor="admin-confirm-password"><span>确认新密码</span></label>
          <PasswordInputWithToggle
            id="admin-confirm-password"
            label="确认新密码"
            autoComplete="new-password"
            value={confirmPassword}
            isVisible={visibleFields.confirm}
            ariaInvalid={passwordsMismatch}
            onChange={updatePasswordField(setConfirmPassword)}
            onToggle={() => toggleVisibility("confirm")}
          />
          {passwordsMismatch && <div className="admin-form-error">两次输入的新密码不一致。</div>}
        </div>
        <div className="admin-form-error" aria-live="polite">{error}</div>
        <footer>
          <button type="button" onClick={onClose}>取消</button>
          <button className="admin-primary" type="submit" disabled={!canSubmit}>{isSubmitting ? "更新中" : "更新密码"}</button>
        </footer>
      </form>
    </AdminModalBackdrop>
  );
}

function PasswordInputWithToggle({
  id,
  label,
  autoComplete,
  value,
  isVisible,
  ariaInvalid,
  onChange,
  onToggle,
}: {
  id: string;
  label: string;
  autoComplete: string;
  value: string;
  isVisible: boolean;
  ariaInvalid?: boolean;
  onChange: (value: string) => void;
  onToggle: () => void;
}) {
  return (
    <div className="admin-password-field">
      <input
        id={id}
        type={isVisible ? "text" : "password"}
        autoComplete={autoComplete}
        aria-invalid={ariaInvalid}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <button
        type="button"
        aria-label={isVisible ? `隐藏${label}` : `显示${label}`}
        title={isVisible ? `隐藏${label}` : `显示${label}`}
        aria-pressed={isVisible}
        onClick={onToggle}
      >
        {isVisible ? <EyeOff size={15} strokeWidth={1.6} aria-hidden="true" /> : <Eye size={15} strokeWidth={1.6} aria-hidden="true" />}
      </button>
    </div>
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
  const [avatarPreviewUrl, setAvatarPreviewUrl] = useState<string | null>(avatarImageSrc(user.avatar_url));
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const validUsername = /^[A-Za-z][A-Za-z0-9]{3,31}$/.test(draft.username);
  const canSubmitUser = (!isCreating || validUsername) && uploadState !== "uploading" && !isSaving;
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
      const response = await fetch(apiUrl("/api/v1/auth/avatar"), {
        method: "POST",
        headers: { authorization: `Bearer ${session.access_token}` },
        body: formData,
      });
      if (!response.ok) {
        throw new Error(await readUploadError(response));
      }
      const payload = await response.json();
      const persistentUrl = payload.data.url as string;
      const mediaResponse = await fetch(apiUrl(persistentUrl), {
        headers: { authorization: `Bearer ${session.access_token}` },
      });
      if (!mediaResponse.ok) {
        throw new Error(await readUploadError(mediaResponse));
      }
      const objectUrl = URL.createObjectURL(await mediaResponse.blob());
      setDraft((current) => ({ ...current, avatar_url: persistentUrl }));
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
    if (!canSubmitUser) return;
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
            <AuthenticatedAvatar avatarUrl={avatarPreviewUrl} alt="头像预览" fallback={initials(draft)} className="admin-avatar large" />
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
          <AdminSelect
            id="admin-user-role"
            ariaLabel="角色"
            value={draft.role}
            options={[
              { value: "前台用户", label: "前台用户" },
              { value: "后台管理员", label: "后台管理员" },
            ]}
            onChange={(value) => setDraft({ ...draft, role: value as Role })}
          />
        </div>
        <footer className="admin-drawer-actions">
          <button type="button" onClick={onClose}>取消</button>
          <button className="admin-primary" type="submit" disabled={!canSubmitUser}>
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
  const [hasTriedConfirm, setHasTriedConfirm] = useState(false);
  const showReasonError = (hasTriedConfirm || reason.length > 0) && reason.trim().length < 4;
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
          <label className="required" htmlFor="admin-action-reason"><span>操作原因</span></label>
          <textarea
            id="admin-action-reason"
            value={reason}
            aria-invalid={showReasonError}
            onChange={(event) => {
              setReason(event.target.value);
              if (hasTriedConfirm) setHasTriedConfirm(false);
            }}
          />
          <div className="admin-form-hint">请填写至少 4 个字，便于审计追踪。</div>
          {showReasonError && <div className="admin-form-error" aria-live="polite">操作原因至少需要 4 个字。</div>}
        </div>
        <footer>
          <button onClick={onCancel}>取消</button>
          <button
            className="admin-primary"
            onClick={() => {
              if (reason.trim().length < 4) {
                setHasTriedConfirm(true);
                return;
              }
              onConfirm(reason);
            }}
          >
            确认
          </button>
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
