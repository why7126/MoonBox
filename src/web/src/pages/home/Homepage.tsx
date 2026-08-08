import { FormEvent, useEffect, useRef, useState } from "react";

const homepageFeatures = [
  { number: "01", title: "Agent 工作流" },
  { number: "02", title: "产品知识库" },
  { number: "03", title: "交付 Harness" },
] as const;

export function Homepage() {
  const [isLoginOpen, setIsLoginOpen] = useState(() => window.location.hash === "#login");
  const usernameInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleHashChange = () => {
      setIsLoginOpen(window.location.hash === "#login");
    };

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    if (!isLoginOpen) return;
    window.scrollTo(0, 0);
    usernameInputRef.current?.focus();
  }, [isLoginOpen]);

  const openAdmin = () => {
    window.history.pushState(null, "", "/admin");
    window.dispatchEvent(new PopStateEvent("popstate"));
  };

  const backHome = () => {
    window.history.replaceState(null, "", `${window.location.pathname}${window.location.search}`);
    setIsLoginOpen(false);
  };

  const submitLoginPrototype = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
  };

  return (
    <>
      <main className="homepage-shell" data-theme="dark" hidden={isLoginOpen}>
        <nav className="homepage-nav" aria-label="首页">
          <a className="homepage-brand" href="/" aria-label="MoonBox 首页">
            <img src="/brand/moonbox/moonbox-nav-logo.png" alt="MoonBox PM Harness" />
          </a>
          <button className="homepage-button homepage-button-secondary" type="button" onClick={openAdmin}>
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
            <button className="homepage-button homepage-button-primary" type="button" onClick={openAdmin}>
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
            <input type="password" name="password" autoComplete="current-password" placeholder="请输入密码" required />
          </label>

          <label className="login-remember">
            <input type="checkbox" name="remember" />
            记住我
          </label>

          <button className="login-submit" type="submit">
            登录并开启宝盒
          </button>
        </form>
      </section>
    </>
  );
}
