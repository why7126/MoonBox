import { BookOpen, KeyRound, LayoutDashboard, ListTree, LogOut, Network, Settings, SunMoon, UserRound, Users } from "lucide-react";
import { useEffect, useState } from "react";
import { PRODUCT_VERSION } from "../../../../shared/product-version";
import { AdminSession, readAdminSession } from "./adminAuth";
import { saveUiTheme } from "../home/uiPreferences";

const apiUrl = (path: string) => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ?? "";
  return `${baseUrl}${path}`;
};

export const avatarImageSrc = (url: string | null | undefined) => {
  if (!url) return null;
  if (/^(blob:|data:)/i.test(url)) return url;
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

export const initials = (user: Pick<AdminSession["user"], "username" | "nickname">) => {
  const name = user.nickname || user.username;
  return name.slice(0, 2).toUpperCase();
};

export function AuthenticatedAvatar({ avatarUrl, alt, fallback, className = "admin-avatar" }: {
  avatarUrl: string | null | undefined;
  alt: string;
  fallback: string;
  className?: string;
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
    const session = readAdminSession();
    if (!session?.access_token) return undefined;
    void readAuthenticatedAvatar(source, session.access_token)
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

  return <span className={className}>{objectUrl ? <img src={objectUrl} alt={alt} /> : fallback}</span>;
}

export function AdminSidebar({
  active,
  currentUser,
  isCollapsed,
  isLightTheme,
  isUserMenuOpen,
  onToggleCollapse,
  onToggleUserMenu,
  onCloseUserMenu,
  onNavigate,
  onOpenProfile,
  onOpenPassword,
  onThemeChange,
  onLogout,
  onToast,
}: {
  active: "spaces" | "users";
  currentUser: AdminSession["user"] | null;
  isCollapsed: boolean;
  isLightTheme: boolean;
  isUserMenuOpen: boolean;
  onToggleCollapse: () => void;
  onToggleUserMenu: () => void;
  onCloseUserMenu: () => void;
  onNavigate: (path: string) => void;
  onOpenProfile: () => void;
  onOpenPassword: () => void;
  onThemeChange: (isLight: boolean) => void;
  onLogout: () => void;
  onToast: (message: string) => void;
}) {
  const username = currentUser?.username || "admin";
  const displayName = currentUser?.nickname || username;

  const openMenuItem = (handler: () => void) => {
    onCloseUserMenu();
    handler();
  };

  return (
    <aside className="admin-sidebar">
      <div className="admin-brand">
        <span className="admin-mark">
          <img src="/brand/moonbox/moonbox-app-icon-256.png" alt="MoonBox 产品图标" />
        </span>
        <div className="admin-brand-name">
          <strong>MoonBox</strong>
          <small>PLATFORM OPS</small>
        </div>
        <em>{PRODUCT_VERSION}</em>
        <button
          className="admin-collapse"
          aria-label={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
          title={isCollapsed ? "展开侧边栏" : "收起侧边栏"}
          onClick={onToggleCollapse}
        >
          {isCollapsed ? "›" : "‹"}
        </button>
      </div>
      <nav aria-label="管理后台导航">
        <span className="admin-nav-group">OPERATIONS</span>
        <button title="首页"><LayoutDashboard className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">首页</span></button>
        <button className={active === "spaces" ? "active" : ""} title="空间管理" onClick={() => onNavigate("/admin/spaces")}><Network className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">空间管理</span></button>
        <span className="admin-nav-group">SYSTEM</span>
        <button className={active === "users" ? "active" : ""} title="用户管理" onClick={() => onNavigate("/admin#admin-users")}><Users className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">用户管理</span></button>
        <button title="系统设置"><Settings className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">系统设置</span></button>
        <button title="日志审计"><ListTree className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">日志审计</span></button>
        <button title="接口文档"><BookOpen className="admin-ico" size={16} strokeWidth={1.5} aria-hidden="true" /><span className="admin-nav-label">接口文档</span></button>
      </nav>
      <div className="admin-sidebar-user">
        {isUserMenuOpen && (
          <div className="admin-user-menu" role="menu">
            <div className="admin-menu-group" role="group" aria-label="账号">
              <button role="menuitem" onClick={() => openMenuItem(onOpenProfile)}><UserRound className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>个人资料</span></button>
              <button role="menuitem" onClick={() => openMenuItem(onOpenPassword)}><KeyRound className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>修改密码</span></button>
            </div>
            <div className="admin-menu-group" role="group" aria-label="导航">
              <button role="menuitem" onClick={() => openMenuItem(() => onNavigate("/requirements"))}><LayoutDashboard className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>返回前台</span></button>
            </div>
            <div className="admin-menu-group" role="group" aria-label="偏好">
              <button
                type="button"
                className="admin-theme-row"
                role="switch"
                aria-label="切换明暗主题"
                aria-checked={isLightTheme}
                onClick={() => {
                  const nextTheme = !isLightTheme;
                  onThemeChange(nextTheme);
                  saveUiTheme(nextTheme ? "light" : "dark");
                  onToast(`已切换为${nextTheme ? "亮色" : "暗色"}主题`);
                }}
              >
                <SunMoon className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" />
                <span>界面主题</span>
                <span className={`admin-theme-switch ${isLightTheme ? "on" : ""}`} aria-hidden="true" />
              </button>
            </div>
            <div className="admin-menu-group admin-menu-session" role="group" aria-label="会话">
              <button role="menuitem" className="logout" onClick={() => openMenuItem(onLogout)}><LogOut className="admin-menu-icon" size={14} strokeWidth={1.5} aria-hidden="true" /><span>退出登录</span></button>
            </div>
          </div>
        )}
        <button className="admin-user-trigger" onClick={onToggleUserMenu} aria-expanded={isUserMenuOpen}>
          <AuthenticatedAvatar avatarUrl={currentUser?.avatar_url} alt={`${username} 头像`} fallback={initials({ username, nickname: displayName })} />
          <span className="admin-user-meta">
            <strong>{displayName}</strong>
          </span>
          <span className="admin-user-chevron">⌃</span>
        </button>
      </div>
    </aside>
  );
}
