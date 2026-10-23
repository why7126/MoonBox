---
requirement_id: REQ-0050-controlled-rule-replacement-proof
title: 规则修改说明与安全归档追溯记录
status: in_sprint
priority: P1
lifecycle_stage: review
created_at: '2026-10-22 12:57:38'
updated_at: '2026-10-23 08:19:22'
owner: 产品团队
source: 用户反馈与同会话 explore
captured_via: req-capture
related_requirements:
- REQ-0047-governance-command-durable-recovery
related_bugs:
- BUG-0063-compatible-requirement-successor-blocked
- BUG-0062-archive-requirement-scope-conflict
iteration: sprint-013
openspec_changes:
- change_id: add-controlled-rule-replacement-proof
  type: add
  status: applied
lifecycle:
  captured: '2026-10-22 12:57:38'
  generated: 2026-10-22 12:59:54
  completed: 2026-10-22 13:11:40
  reviewed: '2026-10-22 13:13:58'
  approved: '2026-10-22 13:13:58'
knowledge_base_refs:
- docs/knowledge-base/best-practices/admin-media-upload-chain.md
- docs/knowledge-base/best-practices/governance-recovery-archive-evidence.md
- docs/knowledge-base/incidents/20261022-compatible-requirement-successor.md
- docs/knowledge-base/retrospectives/sprint-011-retrospective.md
cross_cutting_tags:
- media-upload
prototype_refs:
- path: issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/prototype/web/context.md
  role: ui-contract
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
product_data_collection_observability:
  status: applicable
  affected_layers:
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  - authorization_audit
  - governance_archive
  reason: 可信授权、首次启用和恢复跨用户动作与治理阶段；链路字段仅观测，不替代授权。
  validation: AC-003/004/019/020；授权 API、五张持久表、独立审计及遥测故障隔离已验证，证据见 Change verification.md。
related_change: add-controlled-rule-replacement-proof
---

# 规则修改说明与安全归档追溯记录

## 来源与关联

用户在只读探索后明确执行 req-capture，独立记录受控规则替代能力。关联 REQ-0047 与 BUG-0063、BUG-0062-archive-requirement-scope-conflict；不修改其历史交付和当前归档阻断。采集时未创建 PRD；现已补齐需求文档与原型且评审通过进入 approved，已纳入sprint-013并关联add-controlled-rule-replacement-proof；当前实现和隔离证据见后续实施记录。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-22 20:16:06 | /opsx-modify | Change `add-controlled-rule-replacement-proof` 验收返修已同步，待复验或 archive。 |
| 2026-10-22 17:50:48 | /opsx-accept | Change `add-controlled-rule-replacement-proof` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-22 17:50:13 | /opsx-apply | Change `add-controlled-rule-replacement-proof` apply 完成，待 archive。 |
| 2026-10-22 14:10:31 | /opsx-apply | Change `add-controlled-rule-replacement-proof` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-22 13:36:07 | /opsx-apply | Change `add-controlled-rule-replacement-proof` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-22 13:11:40 | /req-complete | pending_review | REQ-0050-controlled-rule-replacement-proof 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-22 12:59:54 | /req-generate | draft | REQ-0050-controlled-rule-replacement-proof 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-22 12:57:38 | req.capture | captured | 创建单条受控规则替代需求，首版限定规则例外扩展。 |

## 完善结果与知识库报告

| 标签/领域 | 引用 | 验收映射 |
|---|---|---|
| media-upload | admin-media-upload-chain.md | AC-XCUT-001—004，共4项 |
| 治理恢复与兼容边界 | governance-recovery-archive-evidence.md、20261022-compatible-requirement-successor.md | AC-010—015、018 |
| Sprint-011复盘 | sprint-011-retrospective.md | AC-007、015、019 |

文档就绪：Ready for review；原型门禁Partially Ready，结构拆解已完成，PNG暂不要求，Skeleton/真实视觉与样式证据待实施。20项功能、4项横切、4项原型AC均未执行。第10节策略已获需求评审通过，未授予实际审批或归档权限。无额外Issue/Change。当前只修改REQ文档，API/DB/部署/安全实现与客户端无变更。

## 评审结果

通过，见review.md。需求批准不等于具体替代或策略首次启用授权；20+4+4项验收仍未执行，UI Skeleton及真实视觉保持pending。后续先纳入Sprint，再创建Change，设计与验收继续落实可信引导器和并发提交边界。
- 阶段迁移：plan → review（/req-review）

## 当前实施一致性

规则替代审阅、可信授权、首次启用和统一归档控制器已实现。真实附件拒绝保留、隔离成功归档、签名器故障与 API 重启原操作恢复、精确机制规格转换均有证据。业务流程、用户故事和原型仍为有效目标，实际 API/DB/部署变化见 Change design.md/verification.md。历史 req-complete/review 记录保留当时状态。正式 BUG-0063 与 sprint-012 未写入。
