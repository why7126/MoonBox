---
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除 - Trace
status: done
created_at: '2026-09-14 10:26:42'
updated_at: 2026-09-17 08:35:51
recorded_by: product
source: 用户反馈
parent_requirement: REQ-0026-requirement-center-standalone-change-cards
lifecycle_stage: archive
iteration: sprint-007
openspec_changes:
  - change_id: remove-requirement-center-document-drawer-change-attributes
    type: update
    status: archived
related_requirements:
  - REQ-0026-requirement-center-standalone-change-cards
lifecycle:
  captured: '2026-09-14 10:26:42'
  generated: '2026-09-15 23:08:23'
  completed: '2026-09-15 23:11:38'
  reviewed: '2026-09-15 23:16:40'
  approved: '2026-09-15 23:16:40'
knowledge_base_refs: []
cross_cutting_tags: []
knowledge_base_review:
  latest_retrospective: docs/knowledge-base/retrospectives/sprint-005-retrospective.md
  summary: 需求中心同域经验强调事实源优先、文档入口与视觉证据需可验证；本 REQ 已将模块删除、抽屉外入口与 1440px 证据写入验收。
prototype_refs:
  - path: issues/requirements/review/REQ-0036-requirement-center-document-drawer-simplification/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0036-requirement-center-document-drawer-simplification/prototype/web/context.md
    role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: pass
  req_final_consistency: pass
product_data_collection_observability:
  status: not_applicable
  affected_layers:
    - web
  reason: 本需求只调整需求中心 Web 文档抽屉展示与入口组织，计划复用现有文档读取、权限、请求封装、日志审计、行为采集、Task Trace 和对象存储链路；不新增或修改 API、DB、请求日志字段、行为事件、Task Trace、对象存储或客户端请求封装。
  validation: opsx-apply 已完成模块删除、抽屉外 Change 入口、文档读取、权限相关前端回归、1440px/窄视口视觉证据与 computed style 检查；未新增 API、DB、OpenAPI、Orval、请求封装或观测链路。
related_change: remove-requirement-center-document-drawer-change-attributes
priority: P2
---

# 需求中心文档抽屉简化与 Change 属性模块移除 - Trace

## 来源与范围
用户 /req-capture 授权记录；承接本会话 /explore 结论。当前仅采集，未评审、未纳入 Sprint、未创建 Change。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:35:51 | /opsx-archive | Change `remove-requirement-center-document-drawer-change-attributes` 已归档，状态同步完成。 |
| 2026-09-16 08:16:39 | /opsx-modify | Change `remove-requirement-center-document-drawer-change-attributes` 验收返修已同步，后续已完成归档。 |
| 2026-09-15 23:46:17 | /opsx-apply | Change `remove-requirement-center-document-drawer-change-attributes` apply 完成，后续已完成归档。 |
| 2026-09-15 23:44:46 | /opsx-apply | Change `remove-requirement-center-document-drawer-change-attributes` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-15 23:37:28 | /opsx-apply | Change `remove-requirement-center-document-drawer-change-attributes` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-15 23:32:00 | /req-opsx | 创建 OpenSpec Change remove-requirement-center-document-drawer-change-attributes，类型 update；后续已完成 apply 与归档。 |
| 2026-09-15 23:44:29 | /opsx-apply | 实施完成 Change remove-requirement-center-document-drawer-change-attributes；证据见 Change evidence/ui 与 trace 验证记录。 |
| 2026-09-15 23:16:40 | /req-review | 评审通过，状态更新为 approved；下一步进入 Sprint 规划。 |
| 2026-09-15 23:13:41 | /req-complete | REQ-0036-requirement-center-document-drawer-simplification 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-15 23:11:38 | /req-complete | 补齐 user-stories、business-flow、acceptance 与 Web 原型拆解；无管理后台横切标签，状态进入 pending_review。 |
| 2026-09-15 23:09:39 | /req-generate | REQ-0036-requirement-center-document-drawer-simplification 已生成 requirement.md，状态同步为 draft。 |
| 2026-09-15 23:08:23 | /req-generate | 生成 requirement.md，明确直接删除文档抽屉 Change 属性模块，保留抽屉外关联与文档可达性。 |
| 2026-09-14 10:26:42 | /req-capture | 单条记录抽屉简化与关联入口保留，初判 P2，关联已交付父需求。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 08:35:51 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive remove-requirement-center-document-drawer-change-attributes
