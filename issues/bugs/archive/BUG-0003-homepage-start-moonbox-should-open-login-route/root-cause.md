---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
created_at: 2026-08-11 08:27:11
updated_at: 2026-08-11 08:27:11
classification: design
---

# 根因分析

## 直接原因

首页前台登录入口仍使用 `#login` 作为状态开关。`Homepage` 组件通过 `window.location.hash === "#login"` 控制登录视图显隐，并在点击「开启 MoonBox」时把地址写成当前路径加 `#login`。

## 根本原因

前台登录页没有被建模为应用级独立路由。当前 `App` 路由只识别 `/admin`、`/requirements`、`/requirement-center` 以及少量历史 hash 路由，未识别 `/login`。因此首页只能用内部 hash 状态展示登录视图，导致官网 CTA 无法进入 `/login` 独立页面。

## 触发条件

- 用户访问官网首页。
- 点击首页 Hero 区域「开启 MoonBox」按钮。
- 或点击同一首页中复用前台登录入口逻辑的按钮。

## 证据

- `src/web/src/pages/home/Homepage.tsx`：`isLoginOpen` 依赖 `window.location.hash === "#login"`。
- `src/web/src/pages/home/Homepage.tsx`：`openFrontendLogin` 使用 `pushState` 写入 `#login`。
- `src/web/src/App.tsx`：未包含 `/login` 前台登录路由分支。
- `src/web/src/homepage.test.tsx`：现有首页测试把 `#login` 作为预期行为。

## 分类

- 类型：design / frontend-routing
- 修复面：Web 前端路由、首页 CTA 行为、前台登录页入口测试
- 非修复面：API、数据库、对象存储、权限模型、部署反向代理
