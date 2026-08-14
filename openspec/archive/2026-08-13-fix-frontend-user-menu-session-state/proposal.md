---
change_id: fix-frontend-user-menu-session-state
type: fix
status: proposed
created_at: 2026-08-11 18:55:00
updated_at: 2026-08-11 18:55:00
owner: MoonBox 产品团队
source_bug: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
sprint: sprint-002
---

# 修复前台用户菜单登录态显示

## 背景

`BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin` 已确认：用户从后台返回前台需求中心时，前台用户菜单会短暂或持续显示“未登录”。

该问题会造成登录态展示与真实会话不一致，影响用户对账号状态、后台入口权限和会话是否失效的判断。缺陷根因在于前台路由、前台展示 session 和后台鉴权 token 分属不同状态源，需求中心加载上下文前直接使用“未登录”兜底，鉴权失败时也没有统一清理半登录状态。

## 变更内容

- 前台需求中心用户菜单加载期间必须使用本地前台 session 或后台 session 中的已知用户作为稳定兜底，不得显示“未登录”。
- 需求中心上下文接口成功返回后，以接口返回的当前用户、头像和后台访问权限为准。
- 需求中心上下文接口返回 `401/403` 时，必须清理 `moonbox.frontend.session` 与 `moonbox.admin.session`，并跳转 `/login` 或展示一致的登录失效处理。
- 补充前台路由、用户菜单和鉴权失败回归测试。

## 不在范围

- 不新增登录、刷新 token 或权限 API。
- 不改变后端会话有效期、密码策略、角色模型或数据库结构。
- 不调整需求中心看板数据聚合规则。
- 不改变后台用户菜单已实现的修改密码和个人资料能力。

## 回滚计划

如修复导致前台需求中心无法进入、用户菜单权限误显或合法会话被误清理，可回滚本 Change 中的前端 session 兜底、鉴权失败清理和测试变更，恢复当前依赖接口上下文渲染用户菜单的行为；同时保留 BUG 与 Change trace，记录回滚原因并重新评估 session 状态源。

## 影响范围

- Web 前端：`src/web/src/App.tsx`、`src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/pages/home/frontendSession.ts`、相关前端测试。
- 规格：`web-catalog-requirement-center`。
- 文档追溯：BUG trace、Sprint scope、Change trace。
