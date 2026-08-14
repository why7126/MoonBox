---
bug_id: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
created_at: 2026-08-11 18:32:00
updated_at: 2026-08-11 18:32:00
classification: code
---

# 根因分析

## 直接原因

前台需求中心页面在加载上下文前，用户菜单使用空上下文兜底用户 `emptyUser` 渲染，而该兜底用户的名称是“未登录”。当用户从后台返回前台时，需求中心会重新挂载并异步请求 `/api/v1/requirement-center/context`，在请求完成前用户菜单会短暂显示“未登录”。

## 根本原因

前台路由放行、前台用户展示和后台鉴权 token 分属不同状态源：

- `/requirements` 路由只检查 `moonbox.frontend.session` 是否存在。
- 需求中心接口请求使用 `moonbox.admin.session` 中的 access token。
- 用户菜单实际展示依赖接口返回的 `context.currentUser`，初始阶段没有从本地 session 派生稳定的已登录用户展示。
- 当接口返回 `401/403` 时，页面只设置权限错误，没有统一清理前台 session 和后台 session，也没有跳转登录页，导致半登录状态可以持续存在。

## 触发条件

- 用户已登录并进入前台需求中心。
- 用户通过前台用户菜单进入后台，再返回前台需求中心。
- 需求中心上下文接口请求存在可见延迟，或后台 session 已丢失、过期、被撤销，或接口返回 `401/403`。

## 影响分类

- 类型：code
- 影响层：前端路由、前台用户菜单、登录态同步、鉴权失败处理
- 主要风险：登录态展示不一致、用户误判账号状态、后台入口权限显示不稳定

## 证据

- `src/web/src/App.tsx`：前台需求中心路由仅通过 `readFrontendSession()` 判断是否允许进入。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：`activeUser` 在 `context` 为空时回退到 `emptyUser`。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：需求中心上下文请求读取 `readAdminSession()` 并携带后台 token。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：`401/403` 分支只设置错误文案，未统一清理前后台 session 或跳转登录页。
