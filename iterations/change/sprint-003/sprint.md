---
note: workflow-sync — workflow-sync 自动同步 — 12/18 Change archived；6 applied；Sprint `planning`
sprint_id: sprint-003
status: planning
lifecycle_stage: change
created_at: 2026-08-14 17:00:00
updated_at: 2026-08-19 12:23:54
---

# sprint-003 迭代规划

## 1. Sprint 目标

建立证据化根因分析治理：让问题排查、BUG 完善、验收返修和 BUG 来源实现先形成可复核证据链；证据不足时输出人工补证操作步骤，补证完成后再确认根因。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0018-frontend-space-switcher-real-data | 前台空间切换列表真实数据接入 | in_sprint | 3 人天 | apply 18/18；待 archive `update-frontend-space-switcher-real-data` |
| REQ | REQ-0019-space-creation-join-application-flow | 前台创建空间流程 | in_sprint | 3 人天 | apply 18/18；待 archive `add-space-creation-join-application-flow` |
| REQ | REQ-0020-requirement-center-card-document-actions-ai-chat | 需求中心卡片文档查看、动作流转与 AI 聊天增强 | in_sprint | 3 人天 | apply 26/26；待 archive `update-requirement-center-card-document-actions-ai-chat` |
| REQ | REQ-0021-markdown-editor-vditor-enhancement | Markdown 文档 Vditor 增强编辑器 | in_sprint | 3 人天 | apply 23/23；待 archive `update-markdown-editor-vditor-enhancement` |
| BUG | BUG-0011-admin-user-list-enum-time-display-unclear | 用户管理列表枚举标签与时间字段展示不清晰 | done | 1 人天 | archived `fix-admin-user-list-enum-time-display`（2026-08-15 10:04:45） |
| BUG | BUG-0012-requirement-registry-changelog-req0017-archive-drift | REQ-0017 需求索引仍指向 review 路径但真实目录已归档 | done | 1 人天 | archived `fix-requirement-registry-changelog-req0017-archive-drift`（2026-08-15 11:12:00） |
| BUG | BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift | Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整 | done | 1 人天 | archived `fix-workflow-sync-bug-sprint-propose-drift`（2026-08-15 12:29:13） |
| Change | establish-root-cause-evidence-governance | establish root cause evidence governance | archived | 1 人天 | archived `establish-root-cause-evidence-governance`（2026-08-14 22:33:06） |
| Change | establish-command-execution-review-hook | establish command execution review hook | archived | 1 人天 | archived `establish-command-execution-review-hook`（2026-08-15 09:29:46） |
| Change | add-command-execution-review-hook-skill-coverage | add command execution review hook skill coverage | archived | 1 人天 | archived `add-command-execution-review-hook-skill-coverage`（2026-08-15 09:49:59） |
| Change | optimize-req-generate-changelog-sync | optimize req generate changelog sync | archived | 1 人天 | archived `optimize-req-generate-changelog-sync`（2026-08-15 10:49:27） |
| Change | add-opsx-modify-req-subdoc-sweep | add opsx modify req subdoc sweep | archived | 1 人天 | archived `add-opsx-modify-req-subdoc-sweep`（2026-08-15 23:59:59） |
| Change | add-opsx-modify-ui-screenshot-comparison-gate | add opsx modify ui screenshot comparison gate | archived | 1 人天 | archived `add-opsx-modify-ui-screenshot-comparison-gate`（2026-08-15 13:22:00） |
| Change | add-overlay-exit-lightweight-selection-rule | add overlay exit lightweight selection rule | archived | 1 人天 | archived `add-overlay-exit-lightweight-selection-rule`（2026-08-15 15:24:58） |
| Change | add-overlay-click-capture-stop-propagation-rule | add overlay click capture stop propagation rule | archived | 1 人天 | archived `add-overlay-click-capture-stop-propagation-rule`（2026-08-15 16:41:16） |
| Change | add-guided-feedback-dialog-copy-hierarchy | add guided feedback dialog copy hierarchy | applied | 1 人天 | apply 5/5；待 archive `add-guided-feedback-dialog-copy-hierarchy` |
| Change | add-visual-evidence-temp-dir-governance | add visual evidence temp dir governance | archived | 1 人天 | archived `add-visual-evidence-temp-dir-governance`（2026-08-18 10:09:48） |
| Change | apply-deepseek-harness-governance-learnings | apply deepseek harness governance learnings | applied | 1 人天 | apply 12/12；待 archive `apply-deepseek-harness-governance-learnings` |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0018 | 前台空间切换列表真实数据接入 | P1 | in_sprint | apply 18/18；待 archive `update-frontend-space-switcher-real-data` |
| REQ-0019 | 前台创建空间流程 | P1 | in_sprint | apply 18/18；待 archive `add-space-creation-join-application-flow` |
| REQ-0020 | 需求中心卡片文档查看、动作流转与 AI 聊天增强 | P1 | in_sprint | apply 26/26；待 archive `update-requirement-center-card-document-actions-ai-chat` |
| REQ-0021 | Markdown 文档 Vditor 增强编辑器 | P1 | in_sprint | apply 23/23；待 archive `update-markdown-editor-vditor-enhancement` |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0011 | 用户管理列表枚举标签与时间字段展示不清晰 | medium | done | archived `fix-admin-user-list-enum-time-display`（2026-08-15 10:04:45） |
| BUG-0012 | REQ-0017 需求索引仍指向 review 路径但真实目录已归档 | medium | done | archived `fix-requirement-registry-changelog-req0017-archive-drift`（2026-08-15 11:12:00） |
| BUG-0013 | Workflow Sync 对 BUG sprint.propose 的 CHANGELOG/iteration 派生刷新不完整 | medium | done | archived `fix-workflow-sync-bug-sprint-propose-drift`（2026-08-15 12:29:13） |
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `establish-root-cause-evidence-governance` | — | archived | archived `establish-root-cause-evidence-governance`（2026-08-14 22:33:06） |
| `fix-admin-user-list-enum-time-display` | BUG-0011-admin-user-list-enum-time-display-unclear | archived | archived `fix-admin-user-list-enum-time-display`（2026-08-15 10:04:45） |
| `establish-command-execution-review-hook` | — | archived | archived `establish-command-execution-review-hook`（2026-08-15 09:29:46） |
| `add-command-execution-review-hook-skill-coverage` | — | archived | archived `add-command-execution-review-hook-skill-coverage`（2026-08-15 09:49:59） |
| `optimize-req-generate-changelog-sync` | — | archived | archived `optimize-req-generate-changelog-sync`（2026-08-15 10:49:27） |
| `update-frontend-space-switcher-real-data` | REQ-0018-frontend-space-switcher-real-data | applied | apply 18/18；待 archive `update-frontend-space-switcher-real-data` |
| `add-space-creation-join-application-flow` | REQ-0019-space-creation-join-application-flow | applied | apply 18/18；待 archive `add-space-creation-join-application-flow` |
| `fix-requirement-registry-changelog-req0017-archive-drift` | BUG-0012-requirement-registry-changelog-req0017-archive-drift | archived | archived `fix-requirement-registry-changelog-req0017-archive-drift`（2026-08-15 11:12:00） |
| `fix-workflow-sync-bug-sprint-propose-drift` | BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift | archived | archived `fix-workflow-sync-bug-sprint-propose-drift`（2026-08-15 12:29:13） |
| `add-opsx-modify-req-subdoc-sweep` | — | archived | archived `add-opsx-modify-req-subdoc-sweep`（2026-08-15 23:59:59） |
| `add-opsx-modify-ui-screenshot-comparison-gate` | — | archived | archived `add-opsx-modify-ui-screenshot-comparison-gate`（2026-08-15 13:22:00） |
| `add-overlay-exit-lightweight-selection-rule` | — | archived | archived `add-overlay-exit-lightweight-selection-rule`（2026-08-15 15:24:58） |
| `add-overlay-click-capture-stop-propagation-rule` | — | archived | archived `add-overlay-click-capture-stop-propagation-rule`（2026-08-15 16:41:16） |
| `add-guided-feedback-dialog-copy-hierarchy` | — | applied | apply 5/5；待 archive `add-guided-feedback-dialog-copy-hierarchy` |
| `update-requirement-center-card-document-actions-ai-chat` | REQ-0020-requirement-center-card-document-actions-ai-chat | applied | apply 26/26；待 archive `update-requirement-center-card-document-actions-ai-chat` |
| `add-visual-evidence-temp-dir-governance` | — | archived | archived `add-visual-evidence-temp-dir-governance`（2026-08-18 10:09:48） |
| `update-markdown-editor-vditor-enhancement` | REQ-0021-markdown-editor-vditor-enhancement | applied | apply 23/23；待 archive `update-markdown-editor-vditor-enhancement` |
| `apply-deepseek-harness-governance-learnings` | — | applied | apply 12/12；待 archive `apply-deepseek-harness-governance-learnings` |
<!-- workflow-sync:scope-changes:end -->

REQ：无 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 0 个范围项关联 Change，另有 1 个纯 Change；5 archived，1 applied，2 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 验收重点

- 根因状态模型与证据链规则可被人读文档和脚本共同执行。
- 人工补证必须给出操作步骤、返回字段、脱敏要求和返回格式。
- `/explore`、`/bug-explore`、`/bug-complete`、`/opsx-apply`、`/opsx-modify` 均接入门禁。
- 测试、日志、安全和 UI 验收规范均要求证据回扣。

## 4. 风险与缓冲

- 本 Sprint 已包含 BUG-0011 的 Web 管理后台 UI 修复；业务影响仅限用户管理列表展示，不触碰 API、DB、客户端生成物或 Docker Compose。
- 证据脚本先做结构化校验，复杂语义仍由人工和 AI 基于证据判断。
