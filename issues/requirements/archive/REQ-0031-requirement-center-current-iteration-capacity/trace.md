---
requirement_id: REQ-0031-requirement-center-current-iteration-capacity
title: 需求中心显示当前迭代容量已使用与总容量
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:32:20
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
parent_requirement: REQ-0012-frontend-requirement-center
iteration: sprint-006
openspec_changes:
  - change_id: add-requirement-center-current-iteration-capacity
    type: add
    status: archived
related_requirements:
  - REQ-0012-frontend-requirement-center
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: '2026-09-14 10:21:33'
  completed: '2026-09-14 14:50:31'
  reviewed: '2026-09-14 14:56:49'
  approved: '2026-09-14 14:56:49'
captured_via: capture
classification_rationale: 用户要求显示当前迭代容量和 2 个当前迭代的容量汇总，属于需求中心 Sprint 容量可视化新能力。
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/review/REQ-0031-requirement-center-current-iteration-capacity/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0031-requirement-center-current-iteration-capacity/prototype/web/context.md
    role: prototype-decomposition
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
  reason: 需求中心新增当前迭代容量展示，预计涉及 Web 展示、当前迭代筛选或刷新行为，以及后端容量聚合请求摘要。
  validation: req-complete 已补齐行为事件、请求日志、容量异常降级和敏感信息不入日志验收项；OpenSpec 阶段需继续同步 API/OpenAPI/客户端类型与测试。
related_change: add-requirement-center-current-iteration-capacity
priority: P1
---

# REQ-0031-requirement-center-current-iteration-capacity Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录需求中心当前迭代容量展示能力，已评审通过并纳入 sprint-006，已创建并完成 OpenSpec Change，当前执行 `/opsx-archive` 归档收口。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:32:20 | /opsx-archive | Change `add-requirement-center-current-iteration-capacity` 已归档，状态同步完成。 |
| 2026-09-17 08:31:24 | /opsx-archive | 归档前完成 REQ 最终一致性检查：`requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、Mock/API 边界、容量口径及 UI 返修证据一致。 |
| 2026-09-14 18:26:58 | /opsx-modify | Change `add-requirement-center-current-iteration-capacity` 验收返修已同步，已完成复验并归档。 |
| 2026-09-14 15:37:45 | /opsx-apply | Change `add-requirement-center-current-iteration-capacity` apply 完成，已归档。 |
| 2026-09-14 15:37:38 | /opsx-apply | Change `add-requirement-center-current-iteration-capacity` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:12:00 | /req-opsx | 创建 OpenSpec Change `add-requirement-center-current-iteration-capacity`，已完成创建并最终归档。 |
| 2026-09-14 14:56:49 | /req-review | 评审通过，状态从 pending_review 更新为 approved；下一步进入 Sprint 规划，不直接创建 OpenSpec Change。 |
| 2026-09-14 14:52:56 | /req-complete | REQ-0031-requirement-center-current-iteration-capacity 已完成文档补齐，状态曾同步为待评审，后续已完成归档。 |
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 P1；因容量展示与 Sprint 统计指标验收口径不同，独立拆分。 |
| 2026-09-14 10:21:33 | /req-generate | 生成 requirement.md，状态从 captured 更新为 draft；补充当前迭代容量展示、多当前迭代、容量异常与观测影响说明。 |
| 2026-09-14 14:50:31 | /req-complete | 补齐 user-stories、business-flow、acceptance 与 prototype/web；状态更新为 pending_review。Knowledge-base 判定无管理端横切标签，承接 prototype-driven-ui-gate 与 sprint-005 需求中心事实源优先、容量风险前置经验。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 08:32:20 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-requirement-center-current-iteration-capacity
