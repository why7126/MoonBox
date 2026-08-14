---
purpose: 需求当前态看板索引
content: 每个 REQ 一行记录当前状态、下一步和事实源路径
created_at: 2026-08-10 08:59:32
updated_at: 2026-08-13 22:46:27
owner: MoonBox 产品团队
---

# 需求当前态看板索引

本文件用于快速浏览 REQ 当前状态、阶段、关联 Sprint、关联 Change、下一步和事实源路径。

完整事实源仍以各 REQ 目录内 `trace.md`、`issues/requirements/_registry.yaml`、OpenSpec Change、Sprint 四件套和正式规格为准；本文件只做目录级看板入口，不记录完整生命周期流水。

## 维护规则

- 每个 REQ 保留一行当前态快照；状态、阶段、关联 Sprint、关联 Change 或下一步变化时更新对应行。
- 新建 REQ 时新增行；归档后保留行，并将下一步写为“无”或归档后的复盘建议。
- 不复制 `trace.md` 的完整变更记录、验收全文、UI 证据清单或实现细节。
- 普通文案润色、格式调整、错别字修复、非状态性验收措辞调整 MAY 不更新本文件。
- 如本文件与事实源不一致，必须以事实源为准，并通过 Workflow Sync 或 `trace.fix` 类治理动作修正快照。

## 安全边界

本文件不得写入用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。

## 当前态看板

| REQ | 标题 | 当前状态 | 阶段 | 优先级 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |
|---|---|---|---|---|---|---|---|---|---|
| REQ-0017-admin-space-management | 后台管理实现空间管理模块 | in_sprint | review | P1 | sprint-002 | add-admin-space-management | 2026-08-12 21:26:00 | `/opsx-apply REQ-0017-admin-space-management` | `issues/requirements/review/REQ-0017-admin-space-management/trace.md` |
| REQ-0016-unified-account-auth-api | 统一账号认证与个人中心 API | done | archive | P1 | sprint-002 | update-unified-account-auth-api | 2026-08-13 22:49:12 | 无 | `issues/requirements/archive/REQ-0016-unified-account-auth-api/trace.md` |
| REQ-0015-login-password-visibility-toggle | 登录页密码显示/隐藏切换功能 | done | archive | P1 | sprint-002 | update-login-password-visibility-toggle | 2026-08-13 22:46:27 | 无 | `issues/requirements/archive/REQ-0015-login-password-visibility-toggle/trace.md` |
| REQ-0014-frontend-user-menu-profile | 前台用户菜单栏个人资料功能 | done | archive | P1 | sprint-002 | add-frontend-user-menu-profile | 2026-08-13 22:43:34 | 无 | `issues/requirements/archive/REQ-0014-frontend-user-menu-profile/trace.md` |
| REQ-0013-requirement-center-real-data-integration | 需求中心真实数据接入 | done | archive | P1 | sprint-002 | add-requirement-center-real-data-integration | 2026-08-13 22:44:59 | 无 | `issues/requirements/archive/REQ-0013-requirement-center-real-data-integration/trace.md` |
| REQ-0012-frontend-requirement-center | MoonBox 前台需求中心 | in_sprint | review | P1 | sprint-002 | add-frontend-requirement-center | 2026-08-10 19:56:19 | `/opsx-archive REQ-0012-frontend-requirement-center` | `issues/requirements/review/REQ-0012-frontend-requirement-center/trace.md` |
| REQ-0011-admin-user-menu-profile | 后台管理用户菜单栏个人资料功能 | done | archive | P1 | sprint-002 | add-admin-user-menu-profile | 2026-08-13 22:53:31 | 无 | `issues/requirements/archive/REQ-0011-admin-user-menu-profile/trace.md` |
| REQ-0010-admin-user-menu-password-change | 后台管理用户菜单栏密码修改功能 | done | archive | P1 | sprint-002 | add-admin-user-menu-password-change | 2026-08-14 08:45:06 | 无 | `issues/requirements/archive/REQ-0010-admin-user-menu-password-change/trace.md` |
| REQ-0009-git-check-pre-push-security-gate | git-check 推送前安全检测命令 | done | archive | P1 | sprint-002 | add-git-check-pre-push-security-gate | 2026-08-14 08:52:06 | 无 | `issues/requirements/archive/REQ-0009-git-check-pre-push-security-gate/trace.md` |
| REQ-0008-prototype-driven-page-acceptance-gate | 原型驱动页面开发验收门禁 | done | archive | P1 | sprint-001 | enforce-prototype-driven-ui-gate | 2026-08-08 20:49:11 | 无 | `issues/requirements/archive/REQ-0008-prototype-driven-page-acceptance-gate/trace.md` |
| REQ-0007-admin-user-first-login-activation | 后台用户首次登录激活与冻结前状态恢复 | done | archive | P1 | sprint-001 | update-admin-user-first-login-activation | 2026-08-08 20:38:28 | 无 | `issues/requirements/archive/REQ-0007-admin-user-first-login-activation/trace.md` |
| REQ-0006-admin-crud-list-template | 管理后台页面组件化与 CRUD 列表页模板体系 | done | archive | P1 | sprint-001 | add-admin-crud-list-template | 2026-08-08 20:14:46 | 无 | `issues/requirements/archive/REQ-0006-admin-crud-list-template/trace.md` |
| REQ-0005-admin-auth-system | 管理后台登录认证系统 | done | archive | P1 | sprint-001 | add-admin-auth-system | 2026-08-07 23:23:55 | 无 | `issues/requirements/archive/REQ-0005-admin-auth-system/trace.md` |
| REQ-0004-admin-user-management | 管理后台用户管理系统 | done | archive | P1 | sprint-001 | add-admin-user-management | 2026-08-07 22:06:39 | 无 | `issues/requirements/archive/REQ-0004-admin-user-management/trace.md` |
| REQ-0003-database-compatibility | 数据库双环境兼容 | done | archive | P1 | sprint-001 | add-database-compatibility | 2026-07-30 08:58:57 | 无 | `issues/requirements/archive/REQ-0003-database-compatibility/trace.md` |
| REQ-0002-login-page | 登录页功能 | done | archive | P1 | sprint-001 | add-login-page | 2026-07-30 08:04:01 | 无 | `issues/requirements/archive/REQ-0002-login-page/trace.md` |
| REQ-0001-homepage | 首页功能 | done | archive | P1 | sprint-001 | add-homepage-brand-visual | 2026-07-30 08:04:01 | 无 | `issues/requirements/archive/REQ-0001-homepage/trace.md` |
| REQ-0000-build-test-standard | 建立 Testing Governance | done | archive | P1 | sprint-000 | build-test-framework | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-test-standard/trace.md` |
| REQ-0000-build-design-system | 建立 Design System | done | archive | P1 | sprint-000 | build-design-system | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-design-system/trace.md` |
| REQ-0000-build-api-standard | 建立 API Governance | done | archive | P1 | sprint-000 | build-api-standard | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-api-standard/trace.md` |
