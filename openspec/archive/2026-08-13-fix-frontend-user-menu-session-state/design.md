---
change_id: fix-frontend-user-menu-session-state
status: applied
created_at: 2026-08-11 18:55:00
updated_at: 2026-08-11 19:05:00
source_bug: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
---

# 技术设计

## 根因

前台需求中心用户菜单在 `context` 尚未加载时回退到 `emptyUser`，而 `emptyUser.name` 为“未登录”。同时 `/requirements` 路由只检查 `moonbox.frontend.session`，需求中心接口请求却依赖 `moonbox.admin.session` access token。当后台 token 缺失、过期或被撤销时，页面只显示权限错误，不清理前台 session，也不跳转登录页，导致半登录状态持续存在。

## 修复方案

1. 为需求中心构建本地用户兜底：优先读取 `moonbox.frontend.session.username`，必要时读取 `moonbox.admin.session.user.nickname || username`。
2. `context` 未加载完成时，用户菜单使用本地已知用户展示；只有本地也没有登录信息时才允许显示“未登录”。
3. `context` 加载成功后继续以接口返回用户为准，避免本地 session 覆盖真实后台访问权限。
4. `401/403` 鉴权失败时统一清理前台 session 与后台 session，并导航到 `/login`，避免停留在半登录需求中心页面。
5. 保持退出登录、修改密码成功后的会话清理和后台进入路径不回归。

## 会话边界

| 场景 | 期望 |
|---|---|
| 从后台返回前台，context pending | 用户菜单显示已知用户名，不显示“未登录” |
| context 成功返回当前用户 | 用户菜单展示接口用户、头像和后台访问权限 |
| context 返回 `401/403` | 清理前后台 session，并进入 `/login` |
| context 返回其他错误 | 保留已有错误态，不展示过期治理数据 |

## API 与数据

本 Change 不新增 API，不修改数据库。前台继续调用既有 `/api/v1/requirement-center/context` 和已有认证接口。若实现过程中改变 API 错误结构或权限边界，必须同步 `docs/03-api-index.md`、OpenAPI 和相关测试；默认方案不触发 API 文档变更。

## 测试策略

- 前端测试覆盖从后台返回前台且上下文接口 pending 时，用户菜单不显示“未登录”。
- 前端测试覆盖本地前台 session 与后台 session 的兜底优先级。
- 前端测试覆盖上下文接口成功后，以接口用户和权限覆盖本地兜底。
- 前端测试覆盖上下文接口 `401/403` 时清理两类 session 并跳转 `/login`。
- 回归前台登录、进入后台、退出登录和前台修改密码流程。

## 风险

- 如果兜底用户权限被误当作真实权限，可能错误展示“进入后台”入口；实现必须仅将本地兜底用于加载期展示，权限仍以接口返回为准。
- 如果 `401/403` 清理过于激进，可能把临时网络错误误判为登出；实现必须只在明确鉴权失败时清理 session。
- 如果只修复加载期闪烁而不处理鉴权失败，持续“未登录”的半登录体验仍会存在。

## 文档同步

本 Change 默认不改变 API、数据库、部署或安全长期文档。若实现阶段调整登录态存储契约、鉴权错误语义或前台路由保护策略，应同步对应长期文档；否则在 trace 中记录“不适用”原因。
