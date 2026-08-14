---
note: workflow-sync — workflow-sync 自动同步 — 26/26 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-002
status: completed
lifecycle_stage: archive
created_at: 2026-08-09 07:26:26
updated_at: 2026-08-14 16:29:34
---

# sprint-002 迭代规划

## 归档关闭记录

- 2026-08-14 16:28:17：`/sprint-archive sprint-002` 完成关闭；26/26 Change 已归档，498/498 任务完成，readiness、环境 ignore 和 stale scan 均通过，Sprint 目录迁移至 `iterations/archive/sprint-002/`。
- 2026-08-14 16:31:49：`/sprint-exps sprint-002` 已生成复盘：[Sprint-002 经验复盘](../../../docs/knowledge-base/retrospectives/sprint-002-retrospective.md)。

## 1. Sprint 目标

- REQ-0009-git-check-pre-push-security-gate
- REQ-0010-admin-user-menu-password-change
- REQ-0012-frontend-requirement-center
- REQ-0013-requirement-center-real-data-integration
- REQ-0014-frontend-user-menu-profile
- REQ-0015-login-password-visibility-toggle
- REQ-0016-unified-account-auth-api
- REQ-0017-admin-space-management
- BUG-0001-admin-web-login-api-proxy-and-spa-fallback
- BUG-0002-homepage-frontend-login-entry-routes-to-admin
- BUG-0003-homepage-start-moonbox-should-open-login-route
- BUG-0004-frontend-user-menu-change-password-not-implemented
- BUG-0009-frontend-admin-sidebar-version-mismatch

### REQ-0009-git-check-pre-push-security-gate 要点

建立 `/git-check` 推送前安全检测命令，默认扫描 staged + tracked 文件，复用 env ignore 校验，阻断真实环境文件、运行时数据、数据库文件、大文件、密钥/Token/连接串、本机绝对路径和不应进入 Git 的本地数据。

### REQ-0010-admin-user-menu-password-change 要点

实现后台管理用户菜单栏“修改密码”能力：以 modal 承载当前密码、新密码和确认新密码校验；后端提供当前用户自助改密接口；修改成功后撤销当前用户全部旧会话并要求重新登录；实现阶段必须执行 admin-modal 横切验收和 1440px 视觉验收。

### REQ-0012-frontend-requirement-center 要点

建设 MoonBox 前台需求中心首版：以 9 阶段 Requirement/Bug 生命周期看板统一管理采集、规划、评审、Sprint、OpenSpec、研发、验收和归档；保留需求目录既有 prototype.html、prototype.png 和 prototype-context.md 的产品原型口径；实现空间切换 Hover 浮层、空间设置弹窗、主题切换、吸顶列头和 MoonBox 前台视觉体系。后续 `/req-opsx` 必须写 UI Skeleton，`/opsx-apply` 必须完成 1440px 视觉验收。

### REQ-0013-requirement-center-real-data-integration 要点

为 MoonBox 前台需求中心接入真实数据：新增需求中心 BFF 聚合接口，首版读取治理文档、registry、OpenSpec 和 Sprint 文件事实源，替换 `initialIssues`、`workspaces`、`currentUser` 静态数据，并补齐真实统计、筛选搜索、空间权限态、加载态、错误态、空态、无权限态和 Mock/API 边界验收。

### REQ-0014-frontend-user-menu-profile 要点

在前台需求中心用户菜单中实现 `rc-*` 个人资料弹窗，仅支持当前用户修改头像和昵称；头像上传复用现有对象存储链路，昵称允许清空并回退用户名，保存成功后直接使用接口返回 user 刷新前台当前用户上下文、用户菜单展示和本地会话缓存。后续 `/req-opsx` 必须写 UI Contract 与 UI Skeleton，`/opsx-apply` 必须完成 media-upload 横切验收和 1440px 用户菜单/弹窗视觉验收。

### REQ-0015-login-password-visibility-toggle 要点

在 Web 登录页密码输入框补齐显示/隐藏切换控件，默认隐藏密码，切换时不清空输入值、不触发表单提交、不改变登录接口、记住我、错误反馈或返回首页语义。后续 `/req-opsx` 必须写登录页密码字段 UI Skeleton，`/opsx-apply` 必须覆盖默认隐藏、显示/隐藏切换、键盘触发、无障碍状态、登录流程回归和 1440px 视觉验收。

### REQ-0016-unified-account-auth-api 要点

统一账号认证与个人中心 API：将登录、退出、当前用户、个人资料、修改密码、头像上传和受保护头像读取统一迁移到 `/api/v1/auth/*`，不保留旧 `/api/v1/admin/auth/*` 路径；前端统一为单一 session 存储，普通前台用户可修改自己的昵称、头像和密码，后台管理接口继续二次授权。后续 `/req-opsx` 必须同步 API 文档、认证标准、OpenAPI/Orval、前后端测试和 media-upload 横切验收。

### REQ-0017-admin-space-management 要点

建设后台管理空间管理模块：覆盖空间列表、申请审批、回收站、空间详情、空间与产品一对一绑定、配额与用量、有效期、冻结恢复、删除回收、永久删除、通知与审计；实现阶段必须承接 admin-list/admin-modal 横切验收、prototype-driven UI Gate、UI Contract、UI Skeleton、1440px 视觉验收、computed style 验收和 Mock/API 边界声明。

### BUG-0001-admin-web-login-api-proxy-and-spa-fallback 要点

修复 Docker Web 管理后台登录 API 误路由与 `/admin` 直达 404：Web nginx 默认采用同源 `/api` 反向代理到后端 `backend:8000`，并提供 SPA fallback；`VITE_API_BASE_URL` 降级为本地 Vite dev 或分域部署可选配置。

### BUG-0002-homepage-frontend-login-entry-routes-to-admin 要点

修复首页「打开第一个项目」和「开启 MoonBox」误入 `/admin` 的前端路由问题：两个首页 CTA 必须打开前台登录页，明确访问 `/admin` 或具备权限的「进入后台」入口才展示管理后台登录页；同步更新首页与后台入口回归测试，避免错误期望继续固化。

### BUG-0003-homepage-start-moonbox-should-open-login-route 要点

修复官网「开启 MoonBox」仍进入 `/#login` hash 视图的问题：统一登录页必须作为 `/login` 独立路由展示，首页主 CTA 和顶部入口均进入 `/login`；`/login` 提交调用既有后台登录 API，成功后进入 `/requirements`；`/admin` 未登录也回到 `/login`，不得展示独立管理后台登录页；需求中心用户菜单不得显示「未登录」，已有后台权限时应显示「进入后台」。

### BUG-0004-frontend-user-menu-change-password-not-implemented 要点

修复前台需求中心用户菜单“修改密码”入口点击无效的问题：点击后必须打开修改密码弹窗，复用既有 `/api/v1/admin/auth/change-password` 安全规则；成功后同时清理 `moonbox.admin.session` 与 `moonbox.frontend.session` 并跳转 `/login`；失败或两次新密码不一致时不得误清理会话；后台修改密码流程必须保持不回归。

### BUG-0009-frontend-admin-sidebar-version-mismatch 要点

修复前台与后台侧边栏版本号不一致的问题：后台用户管理页侧边栏不得继续硬编码 `v1.0.5`，应复用共享产品版本事实源；补充后台版本展示回归测试，并确认前台需求中心与后台用户管理页展示一致。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0009-git-check-pre-push-security-gate | git-check 推送前安全检测命令 | done | 1 人天 | archived `add-git-check-pre-push-security-gate`（2026-08-09 08:18:35） |
| REQ | REQ-0010-admin-user-menu-password-change | 后台管理用户菜单栏密码修改功能 | done | 1 人天 | archived `add-admin-user-menu-password-change`（2026-08-13 22:39:33） |
| REQ | REQ-0011-admin-user-menu-profile | 后台管理用户菜单栏个人资料功能 | done | 1 人天 | archived `add-admin-user-menu-profile`（2026-08-13 22:42:34） |
| REQ | REQ-0012-frontend-requirement-center | MoonBox 前台需求中心 | done | 3 人天 | archived `add-frontend-requirement-center`（2026-08-13 22:45:00） |
| REQ | REQ-0013-requirement-center-real-data-integration | 需求中心真实数据接入 | done | 3 人天 | archived `add-requirement-center-real-data-integration`（2026-08-11 13:49:52） |
| REQ | REQ-0014-frontend-user-menu-profile | 前台用户菜单栏个人资料功能 | done | 1 人天 | archived `add-frontend-user-menu-profile`（2026-08-11 19:56:00） |
| REQ | REQ-0015-login-password-visibility-toggle | 登录页密码显示/隐藏切换功能 | done | 1 人天 | archived `update-login-password-visibility-toggle`（2026-08-11 22:38:00） |
| REQ | REQ-0016-unified-account-auth-api | 统一账号认证与个人中心 API | done | 3 人天 | archived `update-unified-account-auth-api`（2026-08-12 13:13:07） |
| REQ | REQ-0017-admin-space-management | 后台管理实现空间管理模块 | done | 3 人天 | archived `add-admin-space-management`（2026-08-14 16:11:09） |
| BUG | BUG-0001-admin-web-login-api-proxy-and-spa-fallback | Docker Web 管理后台登录 API 误路由且缺少 SPA fallback | done | 1 人天 | archived `fix-admin-web-login-api-proxy-and-spa-fallback`（2026-08-10 08:24:16） |
| BUG | BUG-0002-homepage-frontend-login-entry-routes-to-admin | 首页前台登录入口误跳后台登录页 | done | 1 人天 | archived `fix-homepage-frontend-login-entry-routes-to-admin`（2026-08-10 23:34:40） |
| BUG | BUG-0003-homepage-start-moonbox-should-open-login-route | 官网开启 MoonBox 应进入 /login 独立登录页 | done | 1 人天 | archived `fix-homepage-login-route`（2026-08-11 12:14:08） |
| BUG | BUG-0004-frontend-user-menu-change-password-not-implemented | 前台用户菜单栏修改密码入口未实现 | done | 1 人天 | archived `fix-frontend-user-menu-change-password`（2026-08-12 13:43:11） |
| BUG | BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin | 从后台返回前台时用户菜单显示未登录 | done | 1 人天 | archived `fix-frontend-user-menu-session-state`（2026-08-11 19:05:00） |
| BUG | BUG-0006-frontend-login-needs-real-frontend-auth | 统一登录入口错误绑定后台管理员认证导致前台用户无法登录 | done | 3 人天 | archived `fix-unified-frontend-login-auth`（2026-08-11 23:38:04） |
| BUG | BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port | Docker 媒体上传横切验收依赖固定端口和默认管理员密码 | done | 1 人天 | archived `fix-docker-media-upload-acceptance-gate`（2026-08-12 13:04:04） |
| BUG | BUG-0008-admin-users-self-freeze-delete-not-forbidden | 管理后台登录用户不能冻结和删除自己 | done | 1 人天 | archived `fix-admin-user-self-freeze-delete-protection`（2026-08-12 14:29:42） |
| BUG | BUG-0009-frontend-admin-sidebar-version-mismatch | 前台与后台侧边栏版本号不一致 | done | 1 人天 | archived `fix-frontend-admin-sidebar-version-mismatch`（2026-08-12 14:35:11） |
| BUG | BUG-0010-admin-user-actions-validation-no-feedback | 用户管理编辑保存与确认操作缺少校验反馈 | done | 1 人天 | archived `fix-admin-user-actions-validation-feedback`（2026-08-13 09:53:24） |
| Change | standardize-guided-command-feedback | standardize guided command feedback | archived | 1 人天 | archived `standardize-guided-command-feedback`（2026-08-13 22:51:46） |
| Change | optimize-spec-study-log-first-learning | optimize spec study log first learning | archived | 1 人天 | archived `optimize-spec-study-log-first-learning`（2026-08-09 08:33:08） |
| Change | apply-mintlify-lightweight-governance | apply mintlify lightweight governance | archived | 1 人天 | archived `apply-mintlify-lightweight-governance`（2026-08-09 08:54:59） |
| Change | add-issues-changelog-index | add issues changelog index | archived | 1 人天 | archived `add-issues-changelog-index`（2026-08-13 22:12:16） |
| Change | strengthen-prototype-ui-acceptance | strengthen prototype ui acceptance | archived | 1 人天 | archived `strengthen-prototype-ui-acceptance`（2026-08-13 22:51:12） |
| Change | optimize-issues-changelog-current-state-index | optimize issues changelog current state index | archived | 1 人天 | archived `optimize-issues-changelog-current-state-index`（2026-08-13 21:59:30） |
| Change | optimize-explore-chain-identity | optimize explore chain identity | archived | 1 人天 | archived `optimize-explore-chain-identity`（2026-08-13 21:53:49） |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0009 | git-check 推送前安全检测命令 | P1 | done | archived `add-git-check-pre-push-security-gate`（2026-08-09 08:18:35） |
| REQ-0010 | 后台管理用户菜单栏密码修改功能 | P1 | done | archived `add-admin-user-menu-password-change`（2026-08-13 22:39:33） |
| REQ-0011 | 后台管理用户菜单栏个人资料功能 | P1 | done | archived `add-admin-user-menu-profile`（2026-08-13 22:42:34） |
| REQ-0012 | MoonBox 前台需求中心 | P1 | done | archived `add-frontend-requirement-center`（2026-08-13 22:45:00） |
| REQ-0013 | 需求中心真实数据接入 | P1 | done | archived `add-requirement-center-real-data-integration`（2026-08-11 13:49:52） |
| REQ-0014 | 前台用户菜单栏个人资料功能 | P1 | done | archived `add-frontend-user-menu-profile`（2026-08-11 19:56:00） |
| REQ-0015 | 登录页密码显示/隐藏切换功能 | P1 | done | archived `update-login-password-visibility-toggle`（2026-08-11 22:38:00） |
| REQ-0016 | 统一账号认证与个人中心 API | P1 | done | archived `update-unified-account-auth-api`（2026-08-12 13:13:07） |
| REQ-0017 | 后台管理实现空间管理模块 | P1 | done | archived `add-admin-space-management`（2026-08-14 16:11:09） |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0001 | Docker Web 管理后台登录 API 误路由且缺少 SPA fallback | high | done | archived `fix-admin-web-login-api-proxy-and-spa-fallback`（2026-08-10 08:24:16） |
| BUG-0002 | 首页前台登录入口误跳后台登录页 | high | done | archived `fix-homepage-frontend-login-entry-routes-to-admin`（2026-08-10 23:34:40） |
| BUG-0003 | 官网开启 MoonBox 应进入 /login 独立登录页 | medium | done | archived `fix-homepage-login-route`（2026-08-11 12:14:08） |
| BUG-0004 | 前台用户菜单栏修改密码入口未实现 | medium | done | archived `fix-frontend-user-menu-change-password`（2026-08-12 13:43:11） |
| BUG-0005 | 从后台返回前台时用户菜单显示未登录 | medium | done | archived `fix-frontend-user-menu-session-state`（2026-08-11 19:05:00） |
| BUG-0006 | 统一登录入口错误绑定后台管理员认证导致前台用户无法登录 | high | done | archived `fix-unified-frontend-login-auth`（2026-08-11 23:38:04） |
| BUG-0007 | Docker 媒体上传横切验收依赖固定端口和默认管理员密码 | high | done | archived `fix-docker-media-upload-acceptance-gate`（2026-08-12 13:04:04） |
| BUG-0008 | 管理后台登录用户不能冻结和删除自己 | high | done | archived `fix-admin-user-self-freeze-delete-protection`（2026-08-12 14:29:42） |
| BUG-0009 | 前台与后台侧边栏版本号不一致 | medium | done | archived `fix-frontend-admin-sidebar-version-mismatch`（2026-08-12 14:35:11） |
| BUG-0010 | 用户管理编辑保存与确认操作缺少校验反馈 | high | done | archived `fix-admin-user-actions-validation-feedback`（2026-08-13 09:53:24） |
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `add-git-check-pre-push-security-gate` | REQ-0009-git-check-pre-push-security-gate | archived | archived `add-git-check-pre-push-security-gate`（2026-08-09 08:18:35） |
| `standardize-guided-command-feedback` | — | archived | archived `standardize-guided-command-feedback`（2026-08-13 22:51:46） |
| `optimize-spec-study-log-first-learning` | — | archived | archived `optimize-spec-study-log-first-learning`（2026-08-09 08:33:08） |
| `apply-mintlify-lightweight-governance` | — | archived | archived `apply-mintlify-lightweight-governance`（2026-08-09 08:54:59） |
| `fix-admin-web-login-api-proxy-and-spa-fallback` | BUG-0001-admin-web-login-api-proxy-and-spa-fallback | archived | archived `fix-admin-web-login-api-proxy-and-spa-fallback`（2026-08-10 08:24:16） |
| `add-issues-changelog-index` | — | archived | archived `add-issues-changelog-index`（2026-08-13 22:12:16） |
| `add-admin-user-menu-password-change` | REQ-0010-admin-user-menu-password-change | archived | archived `add-admin-user-menu-password-change`（2026-08-13 22:39:33） |
| `add-admin-user-menu-profile` | REQ-0011-admin-user-menu-profile | archived | archived `add-admin-user-menu-profile`（2026-08-13 22:42:34） |
| `add-frontend-requirement-center` | REQ-0012-frontend-requirement-center | archived | archived `add-frontend-requirement-center`（2026-08-13 22:45:00） |
| `strengthen-prototype-ui-acceptance` | REQ-0012-frontend-requirement-center | archived | archived `strengthen-prototype-ui-acceptance`（2026-08-13 22:51:12） |
| `fix-homepage-frontend-login-entry-routes-to-admin` | BUG-0002-homepage-frontend-login-entry-routes-to-admin | archived | archived `fix-homepage-frontend-login-entry-routes-to-admin`（2026-08-10 23:34:40） |
| `add-requirement-center-real-data-integration` | REQ-0013-requirement-center-real-data-integration | archived | archived `add-requirement-center-real-data-integration`（2026-08-11 13:49:52） |
| `optimize-issues-changelog-current-state-index` | — | archived | archived `optimize-issues-changelog-current-state-index`（2026-08-13 21:59:30） |
| `fix-homepage-login-route` | BUG-0003-homepage-start-moonbox-should-open-login-route | archived | archived `fix-homepage-login-route`（2026-08-11 12:14:08） |
| `fix-frontend-user-menu-change-password` | BUG-0004-frontend-user-menu-change-password-not-implemented | archived | archived `fix-frontend-user-menu-change-password`（2026-08-12 13:43:11） |
| `add-frontend-user-menu-profile` | REQ-0014-frontend-user-menu-profile | archived | archived `add-frontend-user-menu-profile`（2026-08-11 19:56:00） |
| `fix-frontend-user-menu-session-state` | BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin | archived | archived `fix-frontend-user-menu-session-state`（2026-08-11 19:05:00） |
| `update-login-password-visibility-toggle` | REQ-0015-login-password-visibility-toggle | archived | archived `update-login-password-visibility-toggle`（2026-08-11 22:38:00） |
| `fix-unified-frontend-login-auth` | BUG-0006-frontend-login-needs-real-frontend-auth | archived | archived `fix-unified-frontend-login-auth`（2026-08-11 23:38:04） |
| `update-unified-account-auth-api` | REQ-0016-unified-account-auth-api | archived | archived `update-unified-account-auth-api`（2026-08-12 13:13:07） |
| `fix-docker-media-upload-acceptance-gate` | BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port | archived | archived `fix-docker-media-upload-acceptance-gate`（2026-08-12 13:04:04） |
| `fix-admin-user-self-freeze-delete-protection` | BUG-0008-admin-users-self-freeze-delete-not-forbidden | archived | archived `fix-admin-user-self-freeze-delete-protection`（2026-08-12 14:29:42） |
| `fix-frontend-admin-sidebar-version-mismatch` | BUG-0009-frontend-admin-sidebar-version-mismatch | archived | archived `fix-frontend-admin-sidebar-version-mismatch`（2026-08-12 14:35:11） |
| `add-admin-space-management` | REQ-0017-admin-space-management | archived | archived `add-admin-space-management`（2026-08-14 16:11:09） |
| `optimize-explore-chain-identity` | — | archived | archived `optimize-explore-chain-identity`（2026-08-13 21:53:49） |
| `fix-admin-user-actions-validation-feedback` | BUG-0010-admin-user-actions-validation-no-feedback | archived | archived `fix-admin-user-actions-validation-feedback`（2026-08-13 09:53:24） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0009`、`REQ-0010` 已纳入正式范围；BUG：`BUG-0001` 已纳入正式范围。`REQ-0010` 已完成 OpenSpec archive，当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：`REQ-0009`、`REQ-0010` 已回填关联 Change；`REQ-0010` 对应 `add-admin-user-menu-password-change` 已 archived。

## 3. 工作量与容量

| 指标 | 数值 |
|---|---:|
| 容量 | 30 人天 |
| 需求估算 | 15 人天 |
| BUG 修复估算 | 9 人天 |
| Change 估算 | 7 人天 |
| Story Points | 36 |
| 容量占用 | 120.0% |
| Fix 缓冲 | 0 人天 |

容量门禁带风险通过。本 Sprint 当前容量为 30 人天，纳入 BUG-0010 后已估算 36 人天，容量占用 120.0%；达到但未超过 120% 硬阻断线，fix 缓冲为 0 人天。后续继续新增范围必须优先替换或延后低优先级项。

## 4. 里程碑

| 里程碑 | 目标日期 | 说明 |
|---|---|---|
| Sprint 规划完成 | 2026-08-09 07:26:26 | REQ-0009 纳入正式范围 |
| OpenSpec Change 创建 | 2026-08-09 07:26:26 | 执行 `/req-opsx REQ-0009-git-check-pre-push-security-gate` |
| BUG 修复 Change 创建 | 2026-08-09 23:21:33 | 执行 `/bug-opsx BUG-0001-admin-web-login-api-proxy-and-spa-fallback` |
| REQ-0010 Change 创建 | 2026-08-10 09:07:02 | 执行 `/req-opsx REQ-0010-admin-user-menu-password-change` |
| REQ-0012 纳入 Sprint | 2026-08-10 13:05:13 | 执行 `/sprint-propose --req REQ-0012-frontend-requirement-center` |
| REQ-0013 纳入 Sprint | 2026-08-10 22:04:58 | 执行 `/sprint-propose --req REQ-0013-requirement-center-real-data-integration` |
| BUG-0002 纳入 Sprint | 2026-08-10 22:05:42 | 执行 `/sprint-propose --bug BUG-0002-homepage-frontend-login-entry-routes-to-admin` |
| BUG-0003 纳入 Sprint | 2026-08-11 08:36:53 | 执行 `/sprint-propose --bug BUG-0003-homepage-start-moonbox-should-open-login-route` |
| BUG-0004 纳入 Sprint | 2026-08-11 16:20:00 | 执行 `/sprint-propose --bug BUG-0004-frontend-user-menu-change-password-not-implemented` |
| REQ-0014 纳入 Sprint | 2026-08-11 16:19:48 | 执行 `/sprint-propose --req REQ-0014-frontend-user-menu-profile` |
| REQ-0015 纳入 Sprint | 2026-08-11 22:11:53 | 执行 `/sprint-propose --req REQ-0015-login-password-visibility-toggle` |
| REQ-0016 纳入 Sprint | 2026-08-12 10:23:30 | 执行 `/sprint-propose --req REQ-0016-unified-account-auth-api` |
| BUG-0009 纳入 Sprint | 2026-08-12 14:25:06 | 执行 `/sprint-propose --bug BUG-0009-frontend-admin-sidebar-version-mismatch` |
| REQ-0017 纳入 Sprint | 2026-08-12 21:19:32 | 执行 `/sprint-propose --req REQ-0017-admin-space-management` |
| 实现与验证 | 2026-08-23 07:26:26 | 完成命令、脚本、测试和文档同步 |

## 5. 风险

- 敏感内容扫描存在误报风险，需要区分真实值与示例占位符。
- 检测报告自身必须脱敏，避免把发现的密钥、Token、Cookie 或连接串完整打印出来。
- 默认 staged + tracked 范围应保持快速；全仓扫描作为增强能力，避免拖慢常规推送前检查。
- Docker Web 修复同时触达 nginx、Compose、启动脚本和部署文档；必须避免再次把 Vite 构建期变量误写成容器运行期必需配置。
- `/admin` SPA fallback 和 `/api/` 反代需要同时验证，否则可能出现“页面可打开但 API 仍 404”或“API 可用但直达刷新 404”的半修复。
- REQ-0010 同时触达认证接口、密码策略、会话撤销、前端 modal 和安全文档；必须避免只做前端弹窗而遗漏旧 token 失效与审计脱敏验收。
- REQ-0012 是带 prototype 的前台主页面能力，必须避免实现阶段只复刻静态看板而遗漏阶段动作门禁、空间切换 Hover 安全区、空间设置弹窗滚动和 1440px 视觉验收。
- REQ-0013 同时触达后端 BFF、治理文件读取、前端状态容器和安全脱敏；必须避免把本地绝对路径、原始 Markdown、`.env`、日志或内部异常透传给浏览器。
- REQ-0013 依赖 REQ-0012 既有页面骨架，必须避免真实数据接入时破坏已验收的侧边栏、用户菜单、空间切换、主题切换和 9 阶段看板视觉结构。
- BUG-0002 修复必须避免把首页前台 CTA 再次接入后台路由；前台登录 `#login`、明确 `/admin` 和具备权限的「进入后台」入口需要分别回归。
- BUG-0003 修复必须避免继续固化 `#login` hash 登录状态；`/login` 独立路由、首页 CTA、顶部入口、返回首页和登录提交进入 `/requirements` 需要一起回归。
- REQ-0014 同时触达前台用户菜单、当前用户上下文、头像上传和会话缓存；必须避免只更新弹窗局部状态而遗漏菜单展示、刷新后缓存、受保护头像读取和昵称清空回退。
- BUG-0004 修复必须避免只给前台菜单补 toast 或跳后台入口；前台应具备完整修改密码弹窗、既有改密 API 调用、成功后前后台会话清理和失败不清会话回归。
- REQ-0015 必须避免把登录页显隐切换扩大成忘记密码、注册、重置密码或认证策略调整；实现应只改变密码输入框展示状态，并保持登录提交、记住我、错误反馈和 `/login` 路由语义不回归。
- REQ-0016 是破坏性 API 迁移，必须避免保留 `/api/v1/admin/auth/*` 兼容别名或遗漏测试/文档/客户端生成物；同时要避免统一 session 后削弱 `/api/v1/admin/**` 后台授权边界。
- REQ-0017 追加后 Sprint 容量占用达到 113.3%，fix 缓冲为 -4 人天；后续新增范围必须优先替换或延后低优先级项，避免继续扩大已满载 Sprint。
- BUG-0009 修复必须避免只修改后台静态文案而继续保留第二版本事实源；后台侧边栏应复用共享版本入口，并补充后台测试防止版本展示再次分叉。
- REQ-0017 同时覆盖后台列表、申请审批、回收站、详情、多类高风险弹窗、配额、生命周期、通知审计和 prototype；必须避免只实现静态页面而遗漏服务端权限、状态机、阻塞检查、审计和 UI 证据。

## 6. 知识库承接

| 行动项 | 状态 | 处理说明 |
|---|---|---|
| S1-A001 下一 Sprint 规划承接 sprint-001 复盘行动项 | in_sprint | 本规划已读取 sprint-001 复盘，并记录行动项承接/延期 |
| S1-A002 优化 Sprint Fact Sheet 输出字段过滤 | deferred | 与 REQ-0009 无直接依赖，后续治理 Change 承接 |
| S1-A003 增加 Sprint close 陈旧事实自动修复建议 | deferred | 与 REQ-0009 无直接依赖，后续治理 Change 承接 |
| S1-A004 后台页面新增能力统一套用 CRUD 模板与 UI Gate | in_sprint | REQ-0010 与 REQ-0012 均命中 UI Gate；REQ-0012 承接 prototype-driven UI Gate、空间设置弹窗宽度/滚动和 1440px 视觉验收要求 |

## 7. 横切预防清单

- Admin modal 横切重点：REQ-0010 必须引用 `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`；TSX 不得让 `modal-card` 与专属宽度类并存；实现阶段必须验收 computed width、低视口滚动、遮罩滚动和字段/操作区无遮挡。
- 原型驱动 UI Gate：REQ-0010 已提供 `prototype/web/context.md` 与 `prototype/web/prototype.html`；`/req-opsx` 必须写 UI Skeleton，`/opsx-apply` 必须完成 1440px 视觉验收并回填证据。
- REQ-0012 横切重点：必须引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 与 `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`；空间设置弹窗必须验收 computed width、低视口滚动、遮罩滚动和底部操作可访问；Hover 空间切换浮层必须验收 180ms 安全区和一级菜单持续显示。
- REQ-0013 横切重点：必须引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`；`/req-opsx` 必须声明 Mock/API 边界和真实数据 UI Skeleton，`/opsx-apply` 必须覆盖加载态、错误态、空态、筛选无结果态、权限差异态和真实数据首屏 1440px 视觉验收。
- REQ-0014 横切重点：必须引用 `docs/knowledge-base/best-practices/admin-media-upload-chain.md`；`/req-opsx` 必须声明前台 `rc-*` 个人资料弹窗 UI Contract 和 UI Skeleton，`/opsx-apply` 必须覆盖头像上传 `idle -> uploading -> done/failed` 状态机、同会话即时回显、Docker 实际 Web 端口上传读取回显、脚本准备测试身份、保存后 currentUser/菜单/会话缓存刷新和 1440px 弹窗视觉验收。
- Docker Web 横切重点：`/api/` 代理、SPA fallback、部署文档和启动脚本语义必须一致。
- 前台/后台入口横切重点：首页 CTA 属于前台登录入口，后台登录页只允许通过明确 `/admin` 或具备权限的后台入口出现；测试不得继续断言首页 CTA 跳 `/admin`。
- 前台登录路由横切重点：`/login` 必须是可直达、可刷新、可测试的独立前端路由；测试不得继续断言首页 CTA 进入 `#login`。
- 登录页密码显隐横切重点：REQ-0015 必须引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`；`/req-opsx` 必须声明密码字段 UI Skeleton，`/opsx-apply` 必须覆盖 Eye/EyeOff 图标、`button type=\"button\"`、`aria-label`、`aria-pressed`、键盘触发、值不丢失和 1440px computed style 验收。
- 统一认证与头像上传横切重点：REQ-0016 必须引用 `docs/knowledge-base/best-practices/admin-media-upload-chain.md`；`/req-opsx` 必须声明 `/api/v1/auth/*` 唯一路径、不保留旧 `admin/auth`、统一 session 存储、所有登录用户个人资料权限和后台授权边界；`/opsx-apply` 必须覆盖头像上传 `idle -> uploading -> done/failed`、同会话回显、Docker 实际 Web 端口上传读取回显、脚本准备测试身份、旧路径不可用证据、OpenAPI/Orval/API 文档同步和前后端回归测试。
- REQ-0017 横切重点：必须引用 `docs/knowledge-base/best-practices/admin-list-page-consistency.md` 与 `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`；`/req-opsx` 必须写空间管理 UI Contract 与 UI Skeleton，`/opsx-apply` 必须覆盖分页 DOM、fixed toast、设计系统确认弹窗、禁用 `window.confirm`、弹窗 computed width、低视口滚动、空间详情独立卡片布局、1440px 视觉验收和 Mock/API 边界声明。
- 前台账号安全横切重点：BUG-0004 必须复用后台已实现的修改密码安全规则与弹窗交互口径；前台成功路径必须清理前后台会话并回到 `/login`，失败路径必须保留弹窗和错误提示。
- 安全横切重点：不得提交真实 `.env`、密钥、Token、Cookie、Authorization header、数据库连接串、对象存储凭据、真实客户数据或本机绝对路径。
- 命令输出重点：成功路径紧凑，失败路径分级，所有敏感命中必须脱敏。

## 8. 依赖

```text
REQ-0009-git-check-pre-push-security-gate
  ├─ scripts/validate-env-ignore-policy.py
  ├─ .gitignore
  ├─ rules/security.md
  ├─ rules/environment.md
  └─ rules/data-management.md

BUG-0001-admin-web-login-api-proxy-and-spa-fallback
  ├─ src/web/Dockerfile
  ├─ src/web/nginx.conf
  ├─ docker-compose.yml
  ├─ scripts/docker-up.sh
  └─ docs/02-deployment.md

BUG-0002-homepage-frontend-login-entry-routes-to-admin
  ├─ src/web/src/pages/home/Homepage.tsx
  ├─ src/web/src/App.tsx
  ├─ src/web/src/homepage.test.tsx
  └─ src/web/src/admin-auth.test.tsx

BUG-0003-homepage-start-moonbox-should-open-login-route
  ├─ src/web/src/pages/home/Homepage.tsx
  ├─ src/web/src/App.tsx
  ├─ src/web/src/homepage.test.tsx
  └─ src/web/nginx.conf

BUG-0004-frontend-user-menu-change-password-not-implemented
  ├─ src/web/src/pages/catalog/RequirementCenterPage.tsx
  ├─ src/web/src/pages/admin/AdminUserManagementPage.tsx
  ├─ src/web/src/pages/admin/adminAuth.ts
  ├─ src/web/src/requirement-center.test.tsx
  └─ src/web/src/admin-auth.test.tsx

REQ-0010-admin-user-menu-password-change
  ├─ REQ-0005-admin-auth-system
  ├─ src/backend/app/api/v1/admin_auth.py
  ├─ src/backend/app/repositories/admin_auth.py
  ├─ src/web/src/pages/admin/adminAuth.ts
  ├─ src/web/src/pages/admin/AdminUserManagementPage.tsx
  └─ docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md

REQ-0012-frontend-requirement-center
  ├─ issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.html
  ├─ issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.png
  ├─ issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype-context.md
  ├─ docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  └─ docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md

REQ-0013-requirement-center-real-data-integration
  ├─ REQ-0012-frontend-requirement-center
  ├─ issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/context.md
  ├─ issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/prototype/web/prototype.html
  ├─ docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  └─ issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/acceptance.md

REQ-0014-frontend-user-menu-profile
  ├─ REQ-0012-frontend-requirement-center
  ├─ REQ-0011-admin-user-menu-profile
  ├─ issues/requirements/review/REQ-0014-frontend-user-menu-profile/prototype/web/context.md
  ├─ issues/requirements/review/REQ-0014-frontend-user-menu-profile/prototype/web/prototype.html
  └─ docs/knowledge-base/best-practices/admin-media-upload-chain.md

REQ-0017-admin-space-management
  ├─ issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype.html
  ├─ issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype-context.md
  ├─ issues/requirements/review/REQ-0017-admin-space-management/prototype/web/interaction.md
  ├─ docs/knowledge-base/best-practices/admin-list-page-consistency.md
  └─ docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
```

## 9. 发布计划

本 Sprint 完成后应在后续发布说明中记录新增 `/git-check` 推送前安全检测命令及其默认扫描范围，记录 Docker Web 管理后台登录、`/api` 反代和 `/admin` 直达修复，并记录后台管理用户菜单栏自助修改密码能力及其强制重新登录安全策略。
同时记录 MoonBox 前台需求中心首版能力，包括 9 阶段 Requirement/Bug 看板、空间切换、空间设置和原型驱动 UI 验收；REQ-0013 完成后继续记录需求中心真实数据接入、BFF 聚合接口、Mock 数据替换、权限态、加载/错误/空态和安全脱敏边界；REQ-0014 完成后记录前台用户菜单个人资料弹窗、头像上传、昵称回退和当前用户上下文即时刷新能力；REQ-0017 完成后记录后台空间管理、申请审批、回收站、空间详情、配额生命周期、通知审计和原型驱动 UI 验收；BUG-0002 完成后记录首页前台登录入口不再误入后台登录页的体验修复；BUG-0003 完成后记录官网「开启 MoonBox」进入 `/login` 独立登录页的体验修复；BUG-0004 完成后记录前台用户菜单自助修改密码能力及其成功后重新登录策略。

## 10. 关联文档

- `issues/requirements/review/REQ-0009-git-check-pre-push-security-gate/`
- `issues/requirements/archive/REQ-0010-admin-user-menu-password-change/`
- `issues/requirements/review/REQ-0012-frontend-requirement-center/`
- `issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/`
- `issues/requirements/review/REQ-0014-frontend-user-menu-profile/`
- `issues/requirements/review/REQ-0017-admin-space-management/`
- `issues/bugs/review/BUG-0001-admin-web-login-api-proxy-and-spa-fallback/`
- `issues/bugs/review/BUG-0002-homepage-frontend-login-entry-routes-to-admin/`
- `issues/bugs/review/BUG-0003-homepage-start-moonbox-should-open-login-route/`
- `issues/bugs/review/BUG-0004-frontend-user-menu-change-password-not-implemented/`
- `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`
- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/best-practices/admin-list-page-consistency.md`

## 11. 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 09:35:13 | sprint.propose | 纳入 BUG-0010 用户管理编辑保存与确认操作缺少校验反馈，容量估算 S=1 人天，Sprint 容量占用达到 120.0%。 |
| 2026-08-12 21:19:32 | sprint.propose | 纳入 REQ-0017 后台管理实现空间管理模块，容量估算 M=3 人天，承接 admin-list/admin-modal 横切验收与 prototype-driven UI Gate。 |
| 2026-08-12 10:23:30 | sprint.propose | 纳入 REQ-0016 统一账号认证与个人中心 API，容量估算 M=3 人天，承接 media-upload 横切验收与 `/api/v1/auth/*` 破坏性迁移门禁。 |
| 2026-08-11 16:19:48 | sprint.propose | 纳入 REQ-0014 前台用户菜单栏个人资料功能，容量估算 S=1 人天，承接 media-upload 横切验收与前台 `rc-*` 弹窗原型驱动 UI Gate。 |
| 2026-08-11 16:20:00 | sprint.propose | 纳入 BUG-0004 前台用户菜单栏修改密码入口未实现，容量估算 S=1 人天，明确前台改密弹窗、既有 API 调用、前后台会话清理和后台回归边界。 |
| 2026-08-11 08:36:53 | sprint.propose | 纳入 BUG-0003 官网开启 MoonBox 应进入 `/login` 独立登录页，容量估算 S=1 人天，明确前台登录独立路由与 `#login` 回归边界。 |
| 2026-08-10 22:05:42 | sprint.propose | 纳入 BUG-0002 首页前台登录入口误跳后台登录页，容量估算 S=1 人天，明确前台登录与后台入口路由语义隔离回归。 |
| 2026-08-10 22:04:58 | sprint.propose | 纳入 REQ-0013 需求中心真实数据接入，容量估算 M=3 人天，承接 prototype-driven UI Gate 与 Mock/API 边界验收。 |
| 2026-08-10 13:05:13 | sprint.propose | 纳入 REQ-0012 MoonBox 前台需求中心，容量估算 M=3 人天，承接 prototype-driven UI Gate 与 admin-modal 横切预防清单。 |
| 2026-08-10 09:07:02 | sprint.propose | 纳入 REQ-0010 后台管理用户菜单栏密码修改功能，容量估算 S=1 人天，承接 admin-modal 横切预防清单。 |
| 2026-08-09 07:26:26 | sprint.propose | 创建 sprint-002 并纳入 REQ-0009。 |
| 2026-08-09 23:21:33 | sprint.propose | 纳入 BUG-0001 Docker Web 登录 API 误路由与 SPA fallback 修复。 |
