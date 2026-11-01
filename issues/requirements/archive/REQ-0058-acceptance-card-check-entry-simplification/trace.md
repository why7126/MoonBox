---
requirement_id: REQ-0058-acceptance-card-check-entry-simplification
status: done
priority: P2
created_at: '2026-10-31 23:08:26'
updated_at: 2026-11-01 00:26:32
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 调整已交付检查入口的展示位置，保留检查能力，属于交互改进需求。
lifecycle_stage: archive
iteration: sprint-018
openspec_changes:
- change_id: update-acceptance-card-check-entry
  type: update
  status: archived
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0071-change-summary-acceptance-check-entry-missing
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  reason: 仅删除卡片JSX，不新增请求或日志事件；API、DB、request_logs、usage_events、Task Trace、请求封装、部署、存储及权限契约均不变。
  validation: AC-001至AC-004的5项前端回归与隔离实际前后端检查通过；无客户端生成变化。
  standard_ref: docs/standards/product-data-collection-observability.md
title: 验收中卡片检查入口展示简化追溯记录
lifecycle:
  captured: '2026-10-31 23:08:26'
  generated: '2026-10-31 23:10:48'
  completed: '2026-10-31 23:13:54'
  reviewed: '2026-10-31 23:16:00'
  approved: '2026-10-31 23:16:00'
knowledge_base_refs:
- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
- docs/knowledge-base/retrospectives/sprint-017-retrospective.md
cross_cutting_tags: []
readiness: Ready
prototype_refs:
- path: prototype/web/prototype.html
  role: html-structure
- path: prototype/web/context.md
  role: decomposition-and-contract
prototype_gate:
  decomposition: done
  ui_skeleton: not_applicable
  visual_acceptance_1440: passed
  req_final_consistency: passed
related_change: update-acceptance-card-check-entry
---

# 验收中卡片检查入口展示简化追溯记录

## 当前摘要
已评审并纳入sprint-018；当前Change完成局部删除、回归及用户授权隔离实例1440/390视觉验收，不新增弹窗。真实证据见Change verification.md及evidence/acceptance/real-card-visual-review.md。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-11-01 00:26:32 | /opsx-archive | Change `update-acceptance-card-check-entry` 已归档，状态同步完成。 |
| 2026-11-01 00:23:06 | /opsx-accept | Change `update-acceptance-card-check-entry` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-11-01 00:22:53 | /opsx-apply | Change `update-acceptance-card-check-entry` apply 完成，待 archive。 |
| 2026-10-31 23:35:07 | /opsx-apply | Change `update-acceptance-card-check-entry` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-31 23:26:22 | /opsx-apply | Change `update-acceptance-card-check-entry` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-31 23:14:08 | /req-complete | REQ-0058-acceptance-card-check-entry-simplification 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-31 23:10:48 | /req-generate | REQ-0058-acceptance-card-check-entry-simplification 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-31 23:08:26 | capture | captured | 用户确认新建关联项，保留历史交付 |
| 2026-10-31 23:10:48 | req.generate | draft | 生成需求文档，保留检查与归档门禁 |
| 2026-10-31 23:13:54 | req.complete | pending_review | 原型拆解、2条通用横切AC；承接Sprint017证据分层，视觉待实现 |
| 2026-10-31 23:16:00 | req.review | approved | 范围与检查入口方案通过；视觉门禁留待实现 |

- 阶段迁移：plan → review（/req-review）
- 2026-11-01 00:26:32 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive update-acceptance-card-check-entry
