---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡新增 Sprint 已完成与累计数量
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:31:00
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
parent_requirement: REQ-0012-frontend-requirement-center
iteration: sprint-006
openspec_changes:
  - change_id: add-requirement-center-sprint-completion-metrics
    type: add
    status: archived
related_requirements:
  - REQ-0012-frontend-requirement-center
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: '2026-09-14 10:21:15'
  completed: '2026-09-14 14:50:18'
  reviewed: '2026-09-14 14:56:30'
  approved: '2026-09-14 14:56:30'
captured_via: capture
classification_rationale: 用户要求在需求中心指标卡新增 Sprint 数量统计，属于尚未交付的看板指标增强。
readiness: ready
knowledge_base_gate: N/A
knowledge_base_refs:
  - docs/knowledge-base/README.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/archive/REQ-0030-requirement-center-sprint-completion-metrics/prototype/web/context.md
    role: decomposition
  - path: issues/requirements/archive/REQ-0030-requirement-center-sprint-completion-metrics/prototype/web/prototype.html
    role: html-structure
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - usage_events
  reason: 需求中心上下文请求会返回 Sprint 指标，页面加载、手动刷新和空间切换可能产生行为事件；本需求不新增长耗时、多步骤、异步任务或对象存储链路。
  validation: 后续实现阶段需验证请求日志只记录接口、状态码、耗时和脱敏统计摘要；行为事件只记录页面、刷新或空间切换上下文，不记录原始治理文档或内部路径。
related_change: add-requirement-center-sprint-completion-metrics
priority: P1
---

# REQ-0030-requirement-center-sprint-completion-metrics Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录需求中心指标卡 Sprint 数量统计增强，已评审通过、纳入 `sprint-006`，并创建 OpenSpec Change `add-requirement-center-sprint-completion-metrics`。

## Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | requirement、user-stories、business-flow、acceptance、trace 与 prototype/web 已补齐 |
| Knowledge-base gate | N/A | 未命中 admin-list、admin-form、admin-modal、media-upload 横切标签；已读取最近 Sprint 复盘 |
| Prototype Gate | Pass | 原型拆解、UI Skeleton、1440px 深浅主题视觉验收与 REQ 最终一致性检查已完成 |
| 产品数据采集与链路观测 | applicable | 涉及 request_logs 与 usage_events；不涉及 task_traces / task_trace_spans |

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 将写入 acceptance 的 AC 条数 |
|---|---|---:|
| N/A | 无匹配后台横切 best-practice | 0 |

补充参考 `docs/knowledge-base/retrospectives/sprint-005-retrospective.md`：需求中心卡片与指标应事实源优先，UI 验收应覆盖状态组合、1440px、响应式和脱敏错误态。

## 原型资料

- `prototype/web/context.md`：页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- `prototype/web/prototype.html`：Sprint 数量指标卡静态原型，用于后续 UI Contract 与 Skeleton。
- PNG 暂不要求；实现阶段补充 1440px 深浅主题截图与关键响应式截图。

## Apply 实现证据

| 项 | 证据 | 结论 |
|---|---|---|
| 后端/API | `src/backend/app/services/requirement_center.py`、`src/backend/app/schemas/requirement_center.py` | 已新增真实 `sprint_metrics` 聚合，统计 active/archive Sprint 并去重 |
| 前端 UI | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/styles/globals.css` | 指标区已展示 Sprint 已完成/累计项目级总览 |
| API/客户端 | `docs/03-api-index.md`、`src/web/openapi.json`、`src/web/src/api/generated/governance.ts` | 已同步 API 文档、OpenAPI 和 Orval 类型 |
| 视觉 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-visual-evidence.json` | 1440 深浅主题、1024、390 均 ready 且无溢出 |
| 筛选不变 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/req-0030-filter-invariant.json` | 搜索筛选前后 Sprint 指标文本一致 |
| 返修视觉 | `openspec/archive/2026-09-17-add-requirement-center-sprint-completion-metrics/evidence/modify-20260914-metrics-tooltip/req-0030-modify-visual-evidence.json` | 指标卡高度压缩、统一 tooltip、Sprint 文案与完成比例指标已验证 |
| 脱敏 | `tests/integration/api/test_requirement_center.py` | invalid sprint.yaml 仅返回 `sprint_metrics_partial`，不暴露临时路径或 `/Users/` |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:30:49 | /opsx-archive | Change `add-requirement-center-sprint-completion-metrics` 已归档，状态同步完成。 |
| 2026-09-14 18:29:33 | /opsx-modify | Change `add-requirement-center-sprint-completion-metrics` 验收返修已同步，已完成复验并归档。 |
| 2026-09-14 15:36:30 | /opsx-apply | Change `add-requirement-center-sprint-completion-metrics` apply 完成，已归档。 |
| 2026-09-14 18:26:44 | /opsx-modify | 按验收反馈完成指标卡高度、统一 tooltip、需求/Bug/独立 Change 已完成/总体、Sprint 文案返修。 |
| 2026-09-14 15:19:01 | /opsx-apply | Change `add-requirement-center-sprint-completion-metrics` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 15:33:36 | /opsx-apply | 实现、测试、视觉证据与 REQ/Change trace 回填完成；等待 workflow sync apply 终态同步。 |
| 2026-09-14 14:53:14 | /req-complete | REQ-0030-requirement-center-sprint-completion-metrics 已完成文档补齐，状态曾同步为待评审，后续已完成归档。 |
| 2026-09-14 14:56:30 | /req-review | 评审通过，状态从 pending_review 更新为 approved；下一步进入 Sprint 规划。 |
| 2026-09-14 15:07:31 | /req-opsx | 创建 OpenSpec Change `add-requirement-center-sprint-completion-metrics`，已完成创建并最终归档。 |
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 P1；按指标卡独立验收闭环拆分为单条 REQ。 |
| 2026-09-14 10:21:15 | /req-generate | 生成 requirement.md，状态从 captured 更新为 draft。 |

- 阶段迁移：plan → review（/req-review）
- 2026-09-17 08:30:49 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-requirement-center-sprint-completion-metrics
