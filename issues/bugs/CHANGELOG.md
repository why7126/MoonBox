---
purpose: 缺陷当前态看板索引
content: 每个 BUG 一行记录当前状态、下一步和事实源路径
created_at: 2026-08-10 08:59:32
updated_at: 2026-10-14 17:43:06
owner: MoonBox 产品团队
---

# 缺陷当前态看板索引

本文件用于快速浏览 BUG 当前状态、阶段、关联 Sprint、关联 Change、下一步和事实源路径。

完整事实源仍以各 BUG 目录内 `trace.md`、`issues/bugs/_registry.yaml`、OpenSpec Change、Sprint 四件套和正式规格为准；本文件只做目录级看板入口，不记录完整生命周期流水。

## 维护规则

- 每个 BUG 保留一行当前态快照；状态、阶段、严重等级、关联 Sprint、关联 Change 或下一步变化时更新对应行。
- 新建 BUG 时新增行；归档后保留行，并将下一步写为“无”或归档后的复盘建议。
- 不复制 `trace.md` 的完整变更记录、复现日志原文、截图个人信息、根因全文或 workaround 全文。
- 普通文案润色、格式调整、错别字修复、非状态性验收措辞调整 MAY 不更新本文件。
- 如本文件与事实源不一致，必须以事实源为准，并通过 Workflow Sync 或 `trace.fix` 类治理动作修正快照。

## 安全边界

本文件不得写入用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。

## 当前态看板

| BUG | 标题 | 严重等级 | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |
|---|---|---|---|---|---|---|---|---|---|
| BUG-0042-chat-archive-issue-promote-retest-2 | Chat 关联 Issue 首次归档复验夹具 | low | done | archive | sprint-009 | fix-chat-archive-issue-promote-retest-2 | 2026-10-12 14:14:21 | 无 | `issues/bugs/archive/BUG-0042-chat-archive-issue-promote-retest-2/trace.md` |
| BUG-0041-chat-archive-issue-promote-retest | Chat 关联 Issue 首次归档复验夹具 | low | done | archive | sprint-009 | fix-chat-archive-issue-promote-retest | 2026-10-12 13:36:44 | 无 | `issues/bugs/archive/BUG-0041-chat-archive-issue-promote-retest/trace.md` |
| BUG-0040-chat-archive-issue-promote-fixture | Chat 首次归档关联 Issue 迁移验收夹具 | low | done | archive | sprint-009 | fix-chat-archive-issue-promote-fixture | 2026-10-12 12:00:01 | 无 | `issues/bugs/archive/BUG-0040-chat-archive-issue-promote-fixture/trace.md` |
| BUG-0039-standalone-change-sprint-membership-false-warning | 需求中心纯 Change 卡片误报缺少 Sprint 归属 | medium | captured | plan | 无 | 无 | 2026-10-11 10:02:20 | `/bug-generate BUG-0039-standalone-change-sprint-membership-false-warning` | `issues/bugs/plan/BUG-0039-standalone-change-sprint-membership-false-warning/trace.md` |
| BUG-0038-sprint-009-missing-from-board | 需求看板未显示已存在的 sprint-009 迭代 | medium | enriching | plan | 无 | 无 | 2026-10-11 10:12:00 | 补证运行绑定与快照后继续 `/bug-complete BUG-0038-sprint-009-missing-from-board` | `issues/bugs/plan/BUG-0038-sprint-009-missing-from-board/trace.md` |
| BUG-0037-change-status-projection-unknown | 需求看板将端口迁移 Change 误判为状态异常 | medium | pending_review | plan | 无 | 无 | 2026-10-11 10:12:48 | `/bug-review BUG-0037-change-status-projection-unknown` | `issues/bugs/plan/BUG-0037-change-status-projection-unknown/trace.md` |
| BUG-0036-bug | 需求中心 Bug 生成治理链路验收隔离夹具 | low | draft | plan | 无 | 无 | 2026-10-12 17:04:50 | `/bug-complete BUG-0036-bug` | `issues/bugs/plan/BUG-0036-bug/trace.md` |
| BUG-0035-requirement-center-acceptance-readiness-projection | 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失 | medium | done | archive | sprint-009 | fix-requirement-center-acceptance-readiness-projection | 2026-10-13 08:26:13 | 无 | `issues/bugs/archive/BUG-0035-requirement-center-acceptance-readiness-projection/trace.md` |
| BUG-0034-chat-standalone-archive-scope-tool-path | 产品内纯治理 Change 归档因权限与命令路径缺失失败 | high | done | archive | sprint-009 | fix-chat-standalone-archive-scope-tool-path | 2026-10-13 18:51:48 | 无 | `issues/bugs/archive/BUG-0034-chat-standalone-archive-scope-tool-path/trace.md` |
| BUG-0033-opsx-apply-governance-scope-source-readonly | 产品内执行 opsx-apply 误授治理写权限导致源码只读 | high | done | archive | sprint-008 | fix-opsx-apply-governance-scope-source-readonly | 2026-10-12 23:44:14 | 无 | `issues/bugs/archive/BUG-0033-opsx-apply-governance-scope-source-readonly/trace.md` |
| BUG-0032-chat-session-deletion-precheck-blocked | 删除会话预检提示工作区状态不可确认且确认按钮不可用 | high | captured | plan | 无 | 无 | 2026-10-05 23:23:18 | `/bug-generate BUG-0032-chat-session-deletion-precheck-blocked` | `issues/bugs/plan/BUG-0032-chat-session-deletion-precheck-blocked/trace.md` |
| BUG-0031-requirement-card-chat-skill-token-missing | 需求卡片跳转 Chat 后治理技能未显示为标签 | medium | captured | plan | 无 | 无 | 2026-10-05 23:15:20 | `/bug-generate BUG-0031-requirement-card-chat-skill-token-missing` | `issues/bugs/plan/BUG-0031-requirement-card-chat-skill-token-missing/trace.md` |
| BUG-0030-chat-assistant-output-missing-from-conversation | Chat 工作台已有助手输出事件但对话正文为空 | high | done | archive | sprint-009 | fix-chat-assistant-output-missing-from-conversation | 2026-10-09 10:34:57 | 无 | `issues/bugs/archive/BUG-0030-chat-assistant-output-missing-from-conversation/trace.md` |
| BUG-0029-chat-workbench-nonempty-page-scroll | Chat 工作台非空白对话出现页面级滚动条及底部布局异常 | medium | done | archive | sprint-008 | fix-chat-workbench-nonempty-page-scroll | 2026-10-12 23:01:39 | 无 | `issues/bugs/archive/BUG-0029-chat-workbench-nonempty-page-scroll/trace.md` |
| BUG-0028-requirement-center-card-owner-raw-user-id | 需求中心 Capture 卡片直接显示内部用户标识 | medium | approved | review | 无 | 无 | 2026-10-09 23:22:31 | `/sprint-propose --bug BUG-0028-requirement-center-card-owner-raw-user-id` | `issues/bugs/review/BUG-0028-requirement-center-card-owner-raw-user-id/trace.md` |
| BUG-0027-page-scroll-bottom-light-background-exposed | 页面向上滑动时底部露出浅色背景 | medium | done | archive | sprint-008 | fix-page-scroll-root-background-exposed | 2026-10-05 21:16:26 | 无 | `issues/bugs/archive/BUG-0027-page-scroll-bottom-light-background-exposed/trace.md` |
| BUG-0026-chat-platform-opsx-archive-source-permission | Chat 平台无法归档 source 工作区 Change 且状态未知 | high | done | archive | sprint-008 | fix-chat-platform-opsx-archive-source-permission | 2026-10-12 14:27:28 | 无 | `issues/bugs/archive/BUG-0026-chat-platform-opsx-archive-source-permission/trace.md` |
| BUG-0025-requirement-center-command-chain-write-gap | 需求中心看板展示完整治理命令链但多数命令未接入真实写入 | medium | done | archive | sprint-008 | fix-requirement-center-command-chain-write-gap | 2026-10-14 17:43:06 | 无 | `issues/bugs/archive/BUG-0025-requirement-center-command-chain-write-gap/trace.md` |
| BUG-0024-login-expired-refresh-not-redirect-login | 登录失效时，页面刷新也没有重新定位到登录页 | medium | done | archive | sprint-008 | fix-chat-auth-expired-redirect-login | 2026-10-04 23:50:45 | 无 | `issues/bugs/archive/BUG-0024-login-expired-refresh-not-redirect-login/trace.md` |
| BUG-0023-requirement-center-acceptance-progress-task-classification | 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务 | medium | done | archive | sprint-007 | fix-requirement-center-acceptance-progress-task-classification | 2026-09-17 10:24:39 | 无 | `issues/bugs/archive/BUG-0023-requirement-center-acceptance-progress-task-classification/trace.md` |
| BUG-0022-requirement-center-html-preview-auth-lost | 需求中心卡片 HTML 预览直开受保护接口导致认证失败 | medium | done | archive | sprint-006 | fix-requirement-center-html-preview-auth-lost | 2026-09-14 18:20:45 | 无 | `issues/bugs/archive/BUG-0022-requirement-center-html-preview-auth-lost/trace.md` |
| BUG-0021-requirement-center-bug-card-severity-display | 需求中心 BUG 卡片显示优先级 P 值而非严重性 | medium | done | archive | sprint-006 | fix-requirement-center-bug-card-severity-display | 2026-09-14 14:44:39 | 无 | `issues/bugs/archive/BUG-0021-requirement-center-bug-card-severity-display/trace.md` |
| BUG-0020-req-complete-status-projection-drift | req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移 | medium | done | archive | sprint-006 | fix-req-complete-status-projection-drift | 2026-09-14 13:12:02 | 无 | `issues/bugs/archive/BUG-0020-req-complete-status-projection-drift/trace.md` |
| BUG-0019-requirement-center-issue-title-overridden | 需求中心阶段业务标题来源与文档中文标题校验 | medium | done | archive | sprint-007 | fix-requirement-center-stage-business-titles | 2026-09-29 14:18:37 | 无 | `issues/bugs/archive/BUG-0019-requirement-center-issue-title-overridden/trace.md` |
| BUG-0018-standalone-change-acceptance-source-unverified | 独立 Change 卡片误报验收来源待核实 | medium | done | archive | sprint-006 | fix-standalone-change-acceptance-source | 2026-09-17 08:12:48 | 无 | `issues/bugs/archive/BUG-0018-standalone-change-acceptance-source-unverified/trace.md` |
| BUG-0017-compose-container-name-suffix-one | 容器名不应自动追加 -1 后缀 | medium | done | archive | sprint-007 | fix-compose-container-name-suffix-one | 2026-09-17 08:12:08 | 无 | `issues/bugs/archive/BUG-0017-compose-container-name-suffix-one/trace.md` |
| BUG-0016-capture | 需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载 | medium | done | archive | sprint-005 | fix-requirement-center-loading-and-errors | 2026-09-14 08:59:14 | 无 | `issues/bugs/archive/BUG-0016-capture/trace.md` |
| BUG-0015-requirement-center-apply-start-stage-not-synced | 研发启动后需求中心卡片仍停留待开发，缺少 apply 启动状态同步 | medium | done | archive | sprint-005 | fix-requirement-center-apply-lifecycle-sync | 2026-09-14 08:59:57 | 无 | `issues/bugs/archive/BUG-0015-requirement-center-apply-start-stage-not-synced/trace.md` |
| BUG-0014-requirement-center-capture-not-persisted | 需求中心新建 Capture 仅创建前端临时卡片，未持久化 REQ/BUG 目录、文档、注册表与索引 | high | done | archive | sprint-005 | fix-requirement-center-capture-persistence | 2026-09-14 08:50:34 | 无 | `issues/bugs/archive/BUG-0014-requirement-center-capture-not-persisted/trace.md` |
| BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift | Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整 | medium | done | archive | sprint-003 | fix-workflow-sync-bug-sprint-propose-drift | 2026-08-15 12:29:57 | 无 | `issues/bugs/archive/BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift/trace.md` |
| BUG-0012-requirement-registry-changelog-req0017-archive-drift | REQ-0017 需求索引仍指向 review 路径但真实目录已归档 | medium | done | archive | sprint-003 | fix-requirement-registry-changelog-req0017-archive-drift | 2026-08-15 11:49:47 | 无 | `issues/bugs/archive/BUG-0012-requirement-registry-changelog-req0017-archive-drift/trace.md` |
| BUG-0011-admin-user-list-enum-time-display-unclear | 用户管理列表枚举标签与时间字段展示不清晰 | medium | done | archive | sprint-003 | fix-admin-user-list-enum-time-display | 2026-08-15 10:13:39 | 无 | `issues/bugs/archive/BUG-0011-admin-user-list-enum-time-display-unclear/trace.md` |
| BUG-0010-admin-user-actions-validation-no-feedback | 用户管理编辑保存与确认操作缺少校验反馈 | high | done | archive | sprint-002 | fix-admin-user-actions-validation-feedback | 2026-08-13 22:49:07 | 无 | `issues/bugs/archive/BUG-0010-admin-user-actions-validation-no-feedback/trace.md` |
| BUG-0009-frontend-admin-sidebar-version-mismatch | 前台与后台侧边栏版本号不一致 | medium | done | archive | sprint-002 | fix-frontend-admin-sidebar-version-mismatch | 2026-08-13 22:40:16 | 无 | `issues/bugs/archive/BUG-0009-frontend-admin-sidebar-version-mismatch/trace.md` |
| BUG-0008-admin-users-self-freeze-delete-not-forbidden | 管理后台登录用户不能冻结和删除自己 | high | done | archive | sprint-002 | fix-admin-user-self-freeze-delete-protection | 2026-08-13 22:41:26 | 无 | `issues/bugs/archive/BUG-0008-admin-users-self-freeze-delete-not-forbidden/trace.md` |
| BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port | Docker 媒体上传横切验收依赖固定端口和默认管理员密码 | high | done | archive | sprint-002 | fix-docker-media-upload-acceptance-gate | 2026-08-13 22:51:12 | 无 | `issues/bugs/archive/BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port/trace.md` |
| BUG-0006-frontend-login-needs-real-frontend-auth | 前台登录入口缺少真正前台用户认证能力 | high | done | archive | sprint-002 | fix-unified-frontend-login-auth | 2026-08-13 22:51:29 | 无 | `issues/bugs/archive/BUG-0006-frontend-login-needs-real-frontend-auth/trace.md` |
| BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin | 从后台返回前台时用户菜单显示未登录 | medium | done | archive | sprint-002 | fix-frontend-user-menu-session-state | 2026-08-13 22:45:09 | 无 | `issues/bugs/archive/BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin/trace.md` |
| BUG-0004-frontend-user-menu-change-password-not-implemented | 前台用户菜单栏修改密码入口未实现 | medium | done | archive | sprint-002 | fix-frontend-user-menu-change-password | 2026-08-13 22:48:26 | 无 | `issues/bugs/archive/BUG-0004-frontend-user-menu-change-password-not-implemented/trace.md` |
| BUG-0003-homepage-start-moonbox-should-open-login-route | 官网开启 MoonBox 应进入 /login 独立登录页 | medium | done | archive | sprint-002 | fix-homepage-login-route | 2026-08-13 22:49:27 | 无 | `issues/bugs/archive/BUG-0003-homepage-start-moonbox-should-open-login-route/trace.md` |
| BUG-0002-homepage-frontend-login-entry-routes-to-admin | 首页前台登录入口误跳后台登录页 | high | done | archive | sprint-002 | fix-homepage-frontend-login-entry-routes-to-admin | 2026-08-13 23:04:21 | 无 | `issues/bugs/archive/BUG-0002-homepage-frontend-login-entry-routes-to-admin/trace.md` |
| BUG-0001-admin-web-login-api-proxy-and-spa-fallback | Docker Web 管理后台登录 API 误路由且缺少 SPA fallback | high | done | archive | sprint-002 | fix-admin-web-login-api-proxy-and-spa-fallback | 2026-08-13 22:45:09 | 无 | `issues/bugs/archive/BUG-0001-admin-web-login-api-proxy-and-spa-fallback/trace.md` |

- 2026-10-12：BUG-0042-chat-archive-issue-promote-retest-2，用户授权的 BUG-0026 AC-001 第三份独立虚拟复验样本；与 BUG-0041-chat-archive-issue-promote-retest 相似但首次归档需新 Change，当前在 sprint-009 验收中。
