---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:27:16
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
parent_requirement: REQ-0012-frontend-requirement-center
iteration: sprint-006
openspec_changes:
  - change_id: add-requirement-center-default-current-iteration-cards
    type: requirement
    status: archived
    created_at: 2026-09-14 15:20:35
related_requirements:
  - REQ-0012-frontend-requirement-center
  - REQ-0013-requirement-center-real-data-integration
  - REQ-0026-requirement-center-standalone-change-cards
  - REQ-0030-requirement-center-sprint-completion-metrics
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: 2026-09-14 10:22:15
  completed: 2026-09-14 14:56:26
  reviewed: 2026-09-14 15:06:22
  approved: 2026-09-14 15:06:22
captured_via: capture
classification_rationale: 用户要求需求中心默认列表范围调整为当前迭代，属于默认展示策略增强。
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/context.md
    role: decomposition
  - path: issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/prototype.html
    role: html-structure
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 默认当前迭代范围影响需求中心页面加载、筛选切换、重置筛选、手动刷新和空间/项目切换；若后端聚合接口参与当前迭代识别，需要请求日志记录安全摘要。
  validation: opsx-modify 已验证本次返修仅调整前端 Sprint 多选默认状态和文档口径，无新增 API/OpenAPI/客户端生成变更；行为事件仍仅需记录脱敏筛选上下文。
readiness:
  status: ready
  knowledge_base_gate: N/A
  prototype_gate: pass
related_change: add-requirement-center-default-current-iteration-cards
priority: P1
---

# REQ-0034-requirement-center-default-current-iteration-cards Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录需求中心默认展示策略调整，未评审、未纳入 Sprint、未创建 OpenSpec Change。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:27:16 | /opsx-archive | Change `add-requirement-center-default-current-iteration-cards` 已归档，状态同步完成。 |
| 2026-09-17 08:26:26 | /opsx-archive | 归档前确认 REQ requirement、acceptance、trace、prototype context 与 Change design、spec delta、视觉证据和 Mock/API 边界一致。 |
| 2026-09-14 23:55:00 | /opsx-modify | 根据验收反馈将默认 Sprint 多选扩展为当前 Sprint + 未纳入 Sprint，补测试与文档。 |
| 2026-09-14 18:28:41 | /opsx-modify | Change `add-requirement-center-default-current-iteration-cards` 验收返修已同步，待复验或 archive。 |
| 2026-09-14 18:20:00 | /opsx-modify | 根据验收反馈移除独立范围筛选和筛选下方提示模块，改为通过 Sprint 多选默认选中当前 Sprint 表达当前迭代；测试 90 条通过。 |
| 2026-09-14 15:54:38 | /opsx-apply | Change `add-requirement-center-default-current-iteration-cards` apply 完成，待 archive。 |
| 2026-09-14 15:54:33 | /opsx-apply | Change `add-requirement-center-default-current-iteration-cards` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:54:28 | /opsx-apply | Change `add-requirement-center-default-current-iteration-cards` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:06:22 | /req-review | 评审通过，状态从 pending_review 更新为 approved；下一步纳入 Sprint。 |
| 2026-09-14 14:59:08 | /req-complete | REQ-0034-requirement-center-default-current-iteration-cards 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 14:56:26 | /req-complete | 补齐 user-stories、business-flow、acceptance 与 prototype/web 原型拆解；状态更新为 pending_review。知识库判定无 admin 横切标签，引用 prototype-driven-ui-gate 与 sprint-005 需求中心事实源优先经验。 |
| 2026-09-14 10:22:15 | /req-generate | 生成 requirement.md，状态从 captured 更新为 draft。 |
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 P1；默认展示策略会影响需求中心入口体验，独立拆分。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 08:27:16 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-requirement-center-default-current-iteration-cards
