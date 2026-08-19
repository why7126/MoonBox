---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
status: in_sprint
priority: P1
created_at: 2026-08-18 09:34:10
updated_at: 2026-08-18 10:56:46
lifecycle_stage: review
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
    status: applied
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
| 2026-08-18 10:56:46 | /opsx-apply | Change `update-requirement-center-card-document-actions-ai-chat` apply 完成，待 archive。 |
| 2026-08-18 10:38:27 | /opsx-modify | Change `update-requirement-center-card-document-actions-ai-chat` 验收返修已同步，待复验或 archive。 |
| 2026-08-18 10:20:55 | /opsx-apply | Change `update-requirement-center-card-document-actions-ai-chat` apply 进行中，待补齐剩余验收。 |
| 2026-08-18 09:34:10 | req.capture | 记录需求中心卡片文档查看、阶段动作、AI 聊天、流转反馈与受限验收增强需求。 |
| 2026-08-18 09:41:25 | req.generate | 参考附件 v4.0.9 卡片行为 Patch 生成 requirement.md，状态进入 draft。 |
| 2026-08-18 09:44:53 | req.complete | 补齐 user-stories、business-flow、acceptance 与 prototype/web 原型拆解；读取 prototype-driven-ui-gate 与 sprint-002 复盘，未命中 admin 横切标签。 |
| 2026-08-18 09:51:13 | req.review | 评审通过，确认进入 Sprint 规划前置状态；下一步为 /sprint-propose --req。 |
| 2026-08-18 09:58:34 | req.opsx | 创建 OpenSpec Change `update-requirement-center-card-document-actions-ai-chat`，状态为 proposed。 |

- 阶段迁移：plan → review（/req-review --approve）
