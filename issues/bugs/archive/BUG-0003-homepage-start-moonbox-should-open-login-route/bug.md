---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
title: 官网开启 MoonBox 应进入 /login 独立登录页
severity: medium
status: done
owner:
discovered_at: 2026-08-11 08:19:05
environment: local
related_requirement:
related_change:
created_at: 2026-08-11 08:22:55
updated_at: 2026-08-13 22:49:27
---

# 现象

官网首页「开启 MoonBox」入口当前进入 `/#login` hash 视图，而不是 `/login` 独立前端路由。用户在地址栏看到的是首页 hash 状态，登录页没有形成可直接访问、可分享、可刷新保持语义的独立页面地址。

# 复现步骤

1. 启动 MoonBox Web 本地服务。
2. 访问 `http://localhost:18102/`。
3. 点击首页 Hero 区域的「开启 MoonBox」按钮。
4. 观察浏览器地址栏与登录视图展示状态。

# 期望 vs 实际

## 期望

- 点击「开启 MoonBox」后进入 `http://localhost:18102/login`。
- `/login` 作为独立前端路由展示前台登录页。
- 直接访问或刷新 `/login` 时仍展示前台登录页。
- 返回首页后地址回到 `/`。

## 实际

- 点击「开启 MoonBox」后进入 `http://localhost:18102/#login`。
- 登录视图由首页内部 hash 状态控制，不是独立页面路由。
- 当前前端路由入口未识别 `/login` 前台登录页。

# 影响范围

- 影响官网首页前台登录入口的 URL 语义与导航体验。
- 影响用户直接访问、收藏或分享前台登录页。
- 影响后续前台登录页作为独立页面进行路由治理、测试覆盖和产品手册引用。
- 当前未发现 API、数据库、权限、安全或部署反向代理配置直接受影响；部署侧已有 SPA fallback，主要修复面在 Web 前端路由与测试。

# 严重等级说明

严重等级建议为 `medium`。该问题不会阻断本地服务启动、后端接口或管理后台登录，但会造成官网核心 CTA 进入非预期 URL，削弱前台登录页的独立页面语义和可验证性。优先级建议为 `P2`，适合作为常规修复进入后续 Sprint。
