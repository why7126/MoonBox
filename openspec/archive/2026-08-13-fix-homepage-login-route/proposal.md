---
change_id: fix-homepage-login-route
type: fix
status: applied
created_at: 2026-08-11 08:41:00
updated_at: 2026-08-13 00:00:00
owner: MoonBox 产品团队
source_bug: BUG-0003-homepage-start-moonbox-should-open-login-route
sprint: sprint-002
---

# 修复官网登录独立路由

## 背景原因

`BUG-0003-homepage-start-moonbox-should-open-login-route` 已确认：官网首页点击「开启 MoonBox」后进入 `/#login` hash 视图，而不是 `/login` 独立登录页。

这会削弱前台登录页的 URL 语义，影响直接访问、刷新、收藏、分享和测试治理。当前部署侧已有 SPA fallback，主要问题在 Web 前端路由建模与首页 CTA 行为。

## 变更内容

- 将前台登录页建模为 `/login` 独立前端路由。
- 首页「开启 MoonBox」和「打开第一个项目」必须进入 `/login`，不得继续进入 `#login`。
- 直接访问或刷新 `/login` 时展示前台登录页，不展示官网首页主视图或管理后台登录页。
- 登录页返回首页后 URL 回到 `/`。
- `/login` 作为统一登录页，提交时调用既有后台登录 API，成功后建立后台 session 与前台进入态并进入 `/requirements`。
- `/admin` 未登录时不再展示独立管理后台登录页，统一回到 `/login`。
- `/requirements` 使用前台登录 session 作为前端路由保护；未建立前台 session 时回到 `/login`，不得显示管理后台登录页。
- 已存在后台 admin session 时，需求中心仍应识别后台用户与 `can_access_admin`，用户菜单可展示「进入后台」。
- 更新前端路由与首页登录相关测试，避免继续固化 `#login` 期望。

## 非目标范围

- 不新增真实前台认证 API。
- 不调整管理后台 `/admin` 登录保护逻辑。
- 不修改数据库、对象存储、权限模型或部署反向代理配置。
- 不新增新的认证 API、数据库表或服务端权限模型。

## 回滚计划

如修复导致 `/login` 路由不可用或前台登录视图无法展示，可回滚本 Change 中的前端路由与测试改动，恢复原 `#login` hash 状态入口；同时保留 BUG 和 Change trace，记录回滚原因，并重新评估 `/login` 路由实现方案。

## 影响范围

- Web 前端：`src/web/src/App.tsx`、`src/web/src/pages/home/Homepage.tsx`、相关测试。
- 规格：`web-catalog-homepage`、`web-catalog-login-page`。
- 文档：本 BUG/Change trace 与 Sprint scope。
