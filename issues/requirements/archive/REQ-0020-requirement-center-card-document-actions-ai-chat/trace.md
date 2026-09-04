---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
status: done
priority: P1
created_at: 2026-08-18 09:34:10
updated_at: 2026-09-04 15:29:37
lifecycle_stage: archive
lifecycle:
  captured: 2026-08-18 09:34:10
  generated: 2026-08-18 09:41:25
  completed: 2026-08-18 09:44:53
  reviewed: 2026-08-18 09:51:13
  approved: 2026-08-18 09:51:13
iteration: sprint-003
openspec_changes:
  - change_id: update-requirement-center-card-document-actions-ai-chat
    type: update
    status: archived
related_requirements:
  - REQ-0012-frontend-requirement-center
  - REQ-0013-requirement-center-real-data-integration
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-002-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/context.md
    role: prototype-decomposition
  - path: issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/prototype-preview.svg
    role: static-preview
  - path: issues/requirements/review/REQ-0020-requirement-center-card-document-actions-ai-chat/prototype/web/prototype.png
    role: bitmap-preview
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
related_change: update-requirement-center-card-document-actions-ai-chat
---

# 需求中心卡片文档查看、动作流转与 AI 聊天增强 Trace

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-04 15:29:37 | /opsx-archive | Change `update-requirement-center-card-document-actions-ai-chat` 已归档，状态同步完成。 |
| 2026-09-03 10:31:44 | /opsx-modify | 移除验收中研发/测试/人工验收进度区 CSS 特殊分隔符，改为空格与 `gap` 分隔，并补充无 `Â·` / `·` 的 DOM/computed 证据。 |
| 2026-09-03 10:17:22 | /opsx-modify | 按开发链路必需文档表统一研发中、验收中和已完成卡片文档入口、缺失 Tips、workflow demo 数据；研发/测试/人工验收点击均打开右侧 `tasks.md` 抽屉并按来源聚焦分区。 |
| 2026-08-18 10:56:46 | /opsx-apply | Change `update-requirement-center-card-document-actions-ai-chat` apply 完成，随后进入归档闭环。 |
| 2026-08-18 10:38:27 | /opsx-modify | Change `update-requirement-center-card-document-actions-ai-chat` 验收返修已同步，待复验或 archive。 |
| 2026-08-18 10:20:55 | /opsx-apply | Change `update-requirement-center-card-document-actions-ai-chat` apply 进行中，待补齐剩余验收。 |
| 2026-08-18 09:34:10 | req.capture | 记录需求中心卡片文档查看、阶段动作、AI 聊天、流转反馈与受限验收增强需求。 |
| 2026-08-18 09:41:25 | req.generate | 参考附件 v4.0.9 卡片行为 Patch 生成 requirement.md，状态进入 draft。 |
| 2026-08-18 09:44:53 | req.complete | 补齐 user-stories、business-flow、acceptance 与 prototype/web 原型拆解；读取 prototype-driven-ui-gate 与 sprint-002 复盘，未命中 admin 横切标签。 |
| 2026-08-18 09:51:13 | req.review | 评审通过，确认进入 Sprint 规划前置状态；下一步为 /sprint-propose --req。 |
| 2026-08-18 09:58:34 | req.opsx | 创建 OpenSpec Change `update-requirement-center-card-document-actions-ai-chat`，进入实现准备阶段。 |

- 阶段迁移：plan → review（/req-review --approve）

## 验证记录

| 时间 | 验证 | 结果 |
|---|---|---|
| 2026-09-03 10:17:22 | 前端回归测试 | `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx` 57 tests pass。 |
| 2026-09-03 10:17:22 | 视觉证据 | 已生成 1440px 截图和 DOM/computed 摘要，归档目录为 `openspec/archive/2026-09-04-update-requirement-center-card-document-actions-ai-chat/evidence/20260903-dev-chain-docs-tasks-drawer/`。 |
| 2026-09-03 10:31:44 | 进度区无特殊分隔符 | `computed-progress-gap-no-special-separator-1440.json` 显示 `mojibake=false`、`middleDot=false`，进度区 `gap=8px`，点击人工验收聚焦 `tasks.md` 抽屉的“人工验收进度”。 |
- 2026-09-04 15:29:23 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive update-requirement-center-card-document-actions-ai-chat
