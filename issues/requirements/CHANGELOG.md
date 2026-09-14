---
purpose: 需求当前态看板索引
content: 每个 REQ 一行记录当前状态、下一步和事实源路径
created_at: 2026-08-10 08:59:32
updated_at: 2026-09-14 09:07:45
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
| REQ-0035-chat-agent-model-reasoning-selector | 聊天框新增 Agent、模型和推理程序选择 | captured | plan | P1 | 无 | 无 | 2026-09-14 09:07:45 | `/req-generate REQ-0035-chat-agent-model-reasoning-selector` | `issues/requirements/plan/REQ-0035-chat-agent-model-reasoning-selector/trace.md` |
| REQ-0034-requirement-center-default-current-iteration-cards | 需求中心默认只显示当前迭代卡片 | captured | plan | P1 | 无 | 无 | 2026-09-14 09:07:45 | `/req-generate REQ-0034-requirement-center-default-current-iteration-cards` | `issues/requirements/plan/REQ-0034-requirement-center-default-current-iteration-cards/trace.md` |
| REQ-0033-requirement-center-filter-multiselect-search | 需求中心筛选下拉框支持复选搜索多选与排序优化 | captured | plan | P1 | 无 | 无 | 2026-09-14 09:07:45 | `/req-generate REQ-0033-requirement-center-filter-multiselect-search` | `issues/requirements/plan/REQ-0033-requirement-center-filter-multiselect-search/trace.md` |
| REQ-0032-requirement-center-sprint-dropdown-status | 需求中心 Sprint 下拉列表新增状态展示 | captured | plan | P2 | 无 | 无 | 2026-09-14 09:07:45 | `/req-generate REQ-0032-requirement-center-sprint-dropdown-status` | `issues/requirements/plan/REQ-0032-requirement-center-sprint-dropdown-status/trace.md` |
| REQ-0031-requirement-center-current-iteration-capacity | 需求中心显示当前迭代容量已使用与总容量 | captured | plan | P1 | 无 | 无 | 2026-09-14 09:07:44 | `/req-generate REQ-0031-requirement-center-current-iteration-capacity` | `issues/requirements/plan/REQ-0031-requirement-center-current-iteration-capacity/trace.md` |
| REQ-0030-requirement-center-sprint-completion-metrics | 需求中心指标卡新增 Sprint 已完成与累计数量 | captured | plan | P1 | 无 | 无 | 2026-09-14 09:07:44 | `/req-generate REQ-0030-requirement-center-sprint-completion-metrics` | `issues/requirements/plan/REQ-0030-requirement-center-sprint-completion-metrics/trace.md` |
| REQ-0029-capture-multimodal-candidate-review | 新建 Capture 支持图文 AI 整理、候选审阅与确认后幂等批量采集 | captured | plan | P1 | 无 | 无 | 2026-09-14 08:40:20 | `/req-generate REQ-0029-capture-multimodal-candidate-review` | `issues/requirements/plan/REQ-0029-capture-multimodal-candidate-review/trace.md` |
| REQ-0028-chat-skill-codex | Chat工作台支持多图片输入与仓库Skill快速引用，对话区以提供的Codex截图为基线，保留现有轨迹详情及权限边界；关 | P1 | captured | plan | 无 | 无 | 2026-09-13 23:48:20 | `/req-generate REQ-0028-chat-skill-codex` | `issues/requirements/plan/REQ-0028-chat-skill-codex/trace.md` |
| REQ-0027-capture | Capture 部署验收：需求持久化 | P1 | captured | plan | 无 | 无 | 2026-09-12 21:11:40 | `/req-generate REQ-0027-capture` | `issues/requirements/plan/REQ-0027-capture/trace.md` |
| REQ-0026-requirement-center-standalone-change-cards | 需求中心 Change 可见性与关联追溯 | done | archive | P1 | sprint-005 | add-requirement-center-change-visibility | 2026-09-14 08:45:04 | 无 | `issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/trace.md` |
| REQ-0025-chat-workbench | Chat 工作台与 Codex 持续对话执行 | done | archive | P1 | sprint-004 | add-chat-workbench-codex | 2026-09-14 00:07:19 | 无 | `issues/requirements/archive/REQ-0025-chat-workbench/trace.md` |
| REQ-0024-markdown-editor-human-edit-permission-matrix | Markdown 编辑器按治理阶段扩展人工编辑权限矩阵 | done | archive | P1 | sprint-004 | update-markdown-editor-human-edit-permission-matrix | 2026-09-14 00:07:19 | 无 | `issues/requirements/archive/REQ-0024-markdown-editor-human-edit-permission-matrix/trace.md` |
| REQ-0023-product-workbench-modern-ops-visual-system | MoonBox 产品工作台全面升级为现代 Ops 视觉系统 | done | archive | P1 | sprint-004 | update-product-workbench-modern-ops-visual-system | 2026-09-13 23:48:14 | 无 | `issues/requirements/archive/REQ-0023-product-workbench-modern-ops-visual-system/trace.md` |
| REQ-0022-local-project-import-product-iteration | 本地项目绑定与 Chat、需求中心迭代闭环 | done | archive | P1 | sprint-005 | add-local-project-governance-loop | 2026-09-14 09:00:37 | 无 | `issues/requirements/archive/REQ-0022-local-project-import-product-iteration/trace.md` |
| REQ-0021-markdown-editor-vditor-enhancement | Markdown 文档 Vditor 增强编辑器 | done | archive | P1 | sprint-003 | update-markdown-editor-vditor-enhancement | 2026-09-04 15:29:23 | 无 | `issues/requirements/archive/REQ-0021-markdown-editor-vditor-enhancement/trace.md` |
| REQ-0020-requirement-center-card-document-actions-ai-chat | 需求中心卡片文档查看、动作流转与 AI 聊天增强 | done | archive | P1 | sprint-003 | update-requirement-center-card-document-actions-ai-chat | 2026-09-04 15:30:02 | 无 | `issues/requirements/archive/REQ-0020-requirement-center-card-document-actions-ai-chat/trace.md` |
| REQ-0019-space-creation-join-application-flow | 前台创建空间流程 | done | archive | P1 | sprint-003 | add-space-creation-join-application-flow | 2026-08-27 08:10:14 | 无 | `issues/requirements/archive/REQ-0019-space-creation-join-application-flow/trace.md` |
| REQ-0018-frontend-space-switcher-real-data | 前台空间切换列表真实数据接入 | done | archive | P1 | sprint-003 | update-frontend-space-switcher-real-data | 2026-08-27 08:07:15 | 无 | `issues/requirements/archive/REQ-0018-frontend-space-switcher-real-data/trace.md` |
| REQ-0017-admin-space-management | 后台管理实现空间管理模块 | done | archive | P1 | sprint-002 | add-admin-space-management | 2026-08-14 16:20:58 | 无 | `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` |
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
| REQ-0000-build-test-standard | 建立 Testing Governance | done | archive | P0 | sprint-000 | build-test-framework | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-test-standard/trace.md` |
| REQ-0000-build-design-system | 建立 Design System | done | archive | P0 | sprint-000 | build-design-system | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-design-system/trace.md` |
| REQ-0000-build-api-standard | 建立 API Governance | done | archive | P0 | sprint-000 | build-api-standard | 2026-07-29 22:55:00 | 无 | `issues/requirements/archive/REQ-0000-build-api-standard/trace.md` |
