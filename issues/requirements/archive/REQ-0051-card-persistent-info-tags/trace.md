---
title: 需求中心卡片常驻根因状态与开发人天标签追溯记录
requirement_id: REQ-0051-card-persistent-info-tags
status: done
priority: P2
created_at: '2026-10-22 13:37:33'
updated_at: 2026-10-22 20:02:47
owner: 产品团队
source: 用户反馈与同会话 explore 确认
lifecycle_stage: archive
captured_via: req-capture
parent_requirement: null
iteration: sprint-013
openspec_changes:
- change_id: add-card-persistent-info-tags
  type: add
  status: archived
related_requirements:
- REQ-0031-requirement-center-current-iteration-capacity
- REQ-0020-requirement-center-card-document-actions-ai-chat
lifecycle:
  captured: '2026-10-22 13:37:33'
  generated: '2026-10-22 13:39:44'
  completed: '2026-10-22 13:44:14'
  reviewed: '2026-10-22 13:46:24'
  approved: '2026-10-22 13:46:24'
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - usage_events
  - request_logs
  reason: 卡片数据投影及根因文档点击涉及 Web 与 API；复用既有行为与请求链路，具体事件映射在 PRD 明确。
  na_reason: 本需求不新增长任务或 Agent Workflow，task_traces 与 task_trace_spans 暂不适用；不涉及对象存储写入、数据库结构或保留周期变更。
  validation: 后续验证真实字段映射、文档点击链路和权限、缺失及失败态；本次仅校验采集文档和工作流同步。
knowledge_base_refs:
- docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
- docs/knowledge-base/incidents/20260912-requirement-center-read-performance.md
- docs/knowledge-base/retrospectives/sprint-011-retrospective.md
cross_cutting_tags:
- frontend-kanban
- document-read
- prototype-driven-ui
prototype_refs:
- path: issues/requirements/review/REQ-0051-card-persistent-info-tags/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/review/REQ-0051-card-persistent-info-tags/prototype/web/context.md
  role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
related_change: add-card-persistent-info-tags
---

# 需求中心卡片常驻根因状态与开发人天标签追溯记录

## 来源与状态

用户已完成 explore 选择并明确执行 req-capture。当前需求已纳入 sprint-013，估算3人天；已创建 add-card-persistent-info-tags，实现与验收尚未开始。

## 重复检查

已检查需求 CHANGELOG 与注册表，并聚焦读取相关 capture。

| 相关需求 | 状态 | 区别与结论 |
|---|---|---|
| REQ-0031-requirement-center-current-iteration-capacity | done / archive | 展示 Sprint 总容量；本次展示单卡人天及根因状态，交付与验收目标独立，仅背景相关。 |
| REQ-0020-requirement-center-card-document-actions-ai-chat | done / archive | 提供文档抽屉与动作能力；本次新增跨阶段信息标签，复用其文档入口，不重复建设原能力。 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-22 20:02:47 | /opsx-archive | Change `add-card-persistent-info-tags` 已归档，状态同步完成。 |
| 2026-10-22 19:05:01 | /opsx-modify | Change `add-card-persistent-info-tags` 验收返修已同步，待复验或 archive。 |
| 2026-10-22 18:27:51 | /opsx-accept | Change `add-card-persistent-info-tags` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-22 18:25:56 | /opsx-apply | Change `add-card-persistent-info-tags` apply 完成，待 archive。 |
| 2026-10-22 14:21:54 | /opsx-apply | Change `add-card-persistent-info-tags` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-22 14:05:23 | /opsx-apply | Change `add-card-persistent-info-tags` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-22 13:44:50 | /req-complete | REQ-0051-card-persistent-info-tags 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-22 13:39:47 | /req-generate | REQ-0051-card-persistent-info-tags 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-22 13:37:33 | req.capture | captured | 记录用户已确认的两类常驻标签、根因点击与排序规则，优先级初判 P2。 |
| 2026-10-22 13:39:44 | req.generate | draft | 生成 PRD，明确根因状态映射、人天来源、跨阶段展示及异常边界。 |
| 2026-10-22 13:44:14 | req.complete | pending_review | 补齐用户故事、流程、18 项验收与原型拆解；兼容根因双字段，明确人天去重和缺失处理。 |
| 2026-10-22 13:46:24 | req.review | approved | 用户明确批准；范围、18 项 AC、原型策略与观测声明核对通过；实现阶段视觉门禁保留。 |

## 下一步

`/opsx-apply REQ-0051-card-persistent-info-tags`。

## 就绪与知识库检查

文档齐备，Readiness 为 Partially Ready：产品 UI Skeleton 和视觉证据留待实现阶段，不伪造通过。知识库检查 Pass，新增 3 项 AC-XCUT、4 项 AC-PROTOTYPE。管理端四类标签均不适用，已记录具体原因。Sprint-011 的当前事实与历史证据区分、读取性能事故的权限及缓存边界已转为验收项，不宣称关闭原行动项。
- 阶段迁移：plan → review（/req-review）

## 实施一致性核对（2026-10-22）

标签顺序、人天只读提示及共享根因抽屉已按Change设计实现，九阶段×双视口×双主题隔离证据已采集。API与OpenAPI/Orval、公开手册已同步；数据规则与本需求子文档一致。本地业务观察及隔离真实服务跨阶段、更新、删除、切换和撤权观察已补齐，逐AC结果由当前验收报告签认；证据入口为 openspec/archive/2026-10-22-add-card-persistent-info-tags/evidence/acceptance/implementation-review.md。
- 2026-10-22 20:02:47 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-card-persistent-info-tags
