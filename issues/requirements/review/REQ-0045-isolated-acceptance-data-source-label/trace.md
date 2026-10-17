---
requirement_id: REQ-0045-isolated-acceptance-data-source-label
title: 隔离验收环境在需求中心显示数据源标识追溯记录
status: approved
created_at: '2026-10-11 10:20:11'
updated_at: 2026-10-11 10:37:48
owner: 产品团队
source: 用户反馈
lifecycle_stage: review
captured_via: req-capture
priority: P2
iteration: null
openspec_changes: []
related_requirements: []
lifecycle:
  captured: '2026-10-11 10:20:11'
  generated: '2026-10-11 10:26:58'
  completed: '2026-10-11 10:32:37'
  reviewed: '2026-10-11 10:36:36'
  approved: '2026-10-11 10:36:36'
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, request_logs]
  standard_ref: docs/standards/product-data-collection-observability.md
  reason: 页面标识需要后端向 Web 返回可信环境与快照摘要，涉及需求中心 API 响应和既有请求日志；当前不新增持久事件或长任务链路。
  validation: 后续验证正常与隔离环境的 API 字段、页面标识和刷新一致性；请求日志及页面均不得包含宿主机路径、挂载细节或敏感数据。
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-007-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/review/REQ-0045-isolated-acceptance-data-source-label/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0045-isolated-acceptance-data-source-label/prototype/web/context.md
    role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
---

# 隔离验收环境在需求中心显示数据源标识追溯记录

## 来源与范围

来源为用户对服务数据源与归档工作区不一致事件的反馈。PRD、用户故事、业务流程、验收标准和结构原型已补齐并通过文档评审；尚未纳入 Sprint 或创建 OpenSpec Change。

## 重复检查

| 候选 | 状态 | 相似原因 | 处理结论 |
|---|---|---|---|
| REQ-0044-shared-project-verification-environment | done | 隔离验证环境 | 提供验证任务能力，本项显示治理数据源，验收闭环独立。 |
| REQ-0013-requirement-center-real-data-integration | done | 需求中心数据接入 | 已交付基础真实数据聚合，本项是环境来源提示。 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-11 10:36:36 | req.review | approved | 通过需求文档评审；实施和真实环境验收门禁见 review.md。 |
| 2026-10-11 10:33:12 | /req-complete | REQ-0045-isolated-acceptance-data-source-label 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-11 10:32:37 | req.complete | pending_review | 补齐需求文档和标题区结构原型；知识库无管理端/上传横切标签，承接原型门禁与 Sprint-007 事实源优先经验。 |
| 2026-10-11 10:27:40 | /req-generate | REQ-0045-isolated-acceptance-data-source-label 已生成 requirement.md，状态同步为 draft。 |
| 2026-10-11 10:20:11 | capture | captured | 记录隔离验收环境数据源标识需求。 |
| 2026-10-11 10:26:58 | req.generate | draft | 生成需求中心标题旁显示来源标识的 PRD。 |

- 阶段迁移：plan → review（/req-review）
