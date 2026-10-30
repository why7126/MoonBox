---
title: 独立 Change 优先级定义与卡片展示追溯记录
status: pending_review
priority: P2
created_at: '2026-10-30 09:37:37'
updated_at: 2026-10-30 09:49:11
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 无来源 Issue 的独立 Change 尚无分级能力，属于新增需求。
lifecycle_stage: plan
iteration: null
openspec_changes: []
requirement_id: REQ-0057-standalone-change-priority
parent_requirement: REQ-0056-requirement-center-change-delivery-cards
related_requirements:
- REQ-0056-requirement-center-change-delivery-cards
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及卡片元数据来源与 API 投影；本次仅记录，不修改采集或请求契约。DB、部署、对象存储和安全权限无本次变更。
  validation: 复用探索中的页面与源码证据；后续检查字段来源、权限与日志脱敏，客户端生成依实际 API 差异确定。
lifecycle:
  captured: '2026-10-30 09:37:37'
  generated: 2026-10-30 09:41:40
  completed: 2026-10-30 09:49:11
  reviewed: null
  approved: null
knowledge_base_refs:
- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
- docs/knowledge-base/retrospectives/sprint-015-retrospective.md
cross_cutting_tags: []
readiness: Partially Ready
prototype_refs:
- path: issues/requirements/plan/REQ-0057-standalone-change-priority/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/plan/REQ-0057-standalone-change-priority/prototype/web/context.md
  role: decomposition-and-contract
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
---

# 独立 Change 优先级定义与卡片展示追溯记录

## 当前摘要

已补齐用户故事、业务流程、验收与 HTML 原型；未评审、未纳入 Sprint、未创建 Change。证据与判重见 capture.md；验收见 acceptance.md，原型拆解见 prototype/web/context.md。

知识库承接：通用原型门禁及 sprint-015 的历史证据/当前准入分离；新增4条 AC-XCUT。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-30 09:49:11 | /req-complete | REQ-0057-standalone-change-priority 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-30 09:41:40 | /req-generate | REQ-0057-standalone-change-priority 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-30 09:37:37 | req.capture | captured | 用户授权，判重后独立记录。 |
