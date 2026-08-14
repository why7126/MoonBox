import { FormEvent, useEffect, useRef, useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { AdminSession, canAccessAdmin, loginAdmin } from "../admin/adminAuth";
import { saveFrontendSession } from "./frontendSession";

const homepageFeatures = [
  { number: "01", title: "Agent 工作流" },
  { number: "02", title: "产品知识库" },
  { number: "03", title: "交付 Harness" },
] as const;

export function Homepage({ onAdminLogin }: { onAdminLogin?: (session: AdminSession) => void }) {
  const isLoginRoute = () => window.location.pathname === "/login" || window.location.hash === "#login";
  const [isLoginOpen, setIsLoginOpen] = useState(isLoginRoute);
  const [loginError, setLoginError] = useState("");
  const [isLoginSubmitting, setIsLoginSubmitting] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const usernameInputRef = useRef<HTMLInputElement>(null);
  const passwordInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const syncLoginRoute = () => {
      setIsLoginOpen(isLoginRoute());
    };

    window.addEventListener("popstate", syncLoginRoute);
    window.addEventListener("hashchange", syncLoginRoute);
    return () => {
      window.removeEventListener("popstate", syncLoginRoute);
      window.removeEventListener("hashchange", syncLoginRoute);
    };
  }, []);

  useEffect(() => {
    if (!isLoginOpen) return;
    window.scrollTo(0, 0);
    usernameInputRef.current?.focus();
  }, [isLoginOpen]);

  const openFrontendLogin = () => {
    window.history.pushState(null, "", "/login");
    setIsLoginOpen(true);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const backHome = () => {
    window.history.replaceState(null, "", "/");
    setIsLoginOpen(false);
    setIsPasswordVisible(false);
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const togglePasswordVisibility = () => {
    const input = passwordInputRef.current;
    const selectionStart = input?.selectionStart ?? null;
    const selectionEnd = input?.selectionEnd ?? null;

    setIsPasswordVisible((visible) => !visible);
    window.requestAnimationFrame(() => {
      passwordInputRef.current?.focus();
      if (selectionStart !== null && selectionEnd !== null) {
        passwordInputRef.current?.setSelectionRange(selectionStart, selectionEnd);
      }
    });
  };

  const submitLoginPrototype = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const username = String(formData.get("username") || "").trim();
    const password = String(formData.get("password") || "");
    if (!username || !password) {
      setLoginError("请输入用户名和密码。");
      return;
    }

    setIsLoginSubmitting(true);
    setLoginError("");
    try {
      const session = await loginAdmin(username, password);
      if (canAccessAdmin(session.user)) {
        onAdminLogin?.(session);
      }
      saveFrontendSession(session);
      window.history.pushState(null, "", "/requirements");
      setIsLoginOpen(false);
      setIsPasswordVisible(false);
      window.dispatchEvent(new PopStateEvent("popstate"));
    } catch (exc) {
      setLoginError(exc instanceof Error ? exc.message : "登录失败，请稍后重试。");
    } finally {
      setIsLoginSubmitting(false);
    }
  };

  return (
    <>
      <main className="homepage-shell" data-theme="dark" hidden={isLoginOpen}>
        <nav className="homepage-nav" aria-label="首页">
          <a className="homepage-brand" href="/" aria-label="MoonBox 首页">
            <img src="/brand/moonbox/moonbox-nav-logo.png" alt="MoonBox PM Harness" />
          </a>
          <button className="homepage-button homepage-button-secondary" type="button" onClick={openFrontendLogin}>
            打开第一个项目
          </button>
        </nav>

        <section className="homepage-hero" aria-labelledby="homepage-title">
          <div className="homepage-copy">
            <p className="homepage-eyebrow">AI 原生软件工厂</p>
            <h1 id="homepage-title">打开宝盒，拥有一家软件公司</h1>
            <p className="homepage-lede">
              MoonBox 将 Harness、Agent 工作流与产品知识放进同一座 AI 原生软件工厂。
            </p>
            <button className="homepage-button homepage-button-primary" type="button" onClick={openFrontendLogin}>
              开启 MoonBox
            </button>
          </div>

          <div className="homepage-stage" aria-label="MoonBox 产品视觉">
            <img src="/brand/moonbox/image.png" alt="MoonBox 产品视觉" />
          </div>
        </section>

        <section className="homepage-features" aria-label="MoonBox capabilities">
          {homepageFeatures.map((feature) => (
            <article className="homepage-feature" key={feature.number}>
              <span className="homepage-feature-number">{feature.number}</span>
              <h2>{feature.title}</h2>
              <p>面向企业生产环境的 MoonBox 能力</p>
            </article>
          ))}
        </section>
      </main>

      <section className="login-page" data-theme="dark" hidden={!isLoginOpen} aria-labelledby="login-title">
        <button className="login-back" type="button" onClick={backHome}>
          ← 返回首页
        </button>

        <form className="login-card" aria-label="MoonBox login" onSubmit={submitLoginPrototype}>
          <div className="login-logo">
            <img src="/brand/moonbox/Logo1-20260728001940.png" alt="MoonBox PM Harness" />
          </div>
          <h1 id="login-title">开启你的宝盒</h1>
          <p className="login-intro">登录 MoonBox，继续构建你的 Agent 研发组织。</p>

          <label className="login-field">
            <span>用户名</span>
            <input
              ref={usernameInputRef}
              type="text"
              name="username"
              autoComplete="username"
              placeholder="请输入用户名"
              required
            />
          </label>

          <label className="login-field">
            <span>密码</span>
            <span className="login-password-field">
              <input
                ref={passwordInputRef}
                type={isPasswordVisible ? "text" : "password"}
                name="password"
                autoComplete="current-password"
                placeholder="请输入密码"
                required
              />
              <button
                className="login-password-toggle"
                type="button"
                aria-label={isPasswordVisible ? "隐藏密码" : "显示密码"}
                aria-pressed={isPasswordVisible}
                title={isPasswordVisible ? "隐藏密码" : "显示密码"}
                onClick={togglePasswordVisibility}
              >
                {isPasswordVisible ? (
                  <EyeOff size={16} strokeWidth={1.7} aria-hidden="true" />
                ) : (
                  <Eye size={16} strokeWidth={1.7} aria-hidden="true" />
                )}
              </button>
            </span>
          </label>

          <label className="login-remember">
            <input type="checkbox" name="remember" />
            记住我
          </label>

          <button className="login-submit" type="submit">
            {isLoginSubmitting ? "登录中..." : "登录并开启宝盒"}
          </button>
          <div className={`admin-login-error ${loginError ? "visible" : ""}`} aria-live="polite">
            {loginError}
          </div>
        </form>
      </section>
    </>
  );
}
