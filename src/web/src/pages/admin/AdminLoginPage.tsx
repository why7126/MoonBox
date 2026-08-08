import { FormEvent, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { AdminSession, loginAdmin } from "./adminAuth";

export function AdminLoginPage({ onLogin }: { onLogin: (session: AdminSession) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!username.trim() || !password) {
      setError("请输入用户名和密码。");
      return;
    }
    setIsSubmitting(true);
    setError("");
    try {
      const session = await loginAdmin(username.trim(), password);
      onLogin(session);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : "登录失败，请稍后重试。");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="admin-login-page" data-theme="dark">
      <form className="admin-login-panel" aria-label="管理后台登录" onSubmit={submit}>
        <p>MoonBox Admin</p>
        <h1>管理后台登录</h1>
        <span>使用后台管理员账号进入 MoonBox 管理后台。</span>
        <label>
          用户名
          <input autoComplete="username" autoFocus value={username} aria-invalid={Boolean(error)} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          密码
          <span className="admin-login-password">
            <input
              autoComplete="current-password"
              type={isPasswordVisible ? "text" : "password"}
              value={password}
              aria-invalid={Boolean(error)}
              onChange={(event) => setPassword(event.target.value)}
            />
            <button
              type="button"
              aria-label={isPasswordVisible ? "隐藏密码" : "显示密码"}
              title={isPasswordVisible ? "隐藏密码" : "显示密码"}
              onClick={() => setIsPasswordVisible((value) => !value)}
            >
              {isPasswordVisible ? <EyeOff size={16} aria-hidden="true" /> : <Eye size={16} aria-hidden="true" />}
            </button>
          </span>
        </label>
        <button className="admin-login-submit admin-primary" type="submit" disabled={isSubmitting}>
          {isSubmitting ? "登录中..." : "登录管理后台"}
        </button>
        <div className={`admin-login-error ${error ? "visible" : ""}`} aria-live="polite">{error}</div>
      </form>
    </main>
  );
}
