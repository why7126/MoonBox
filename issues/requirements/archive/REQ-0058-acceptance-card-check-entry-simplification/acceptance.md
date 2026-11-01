---
requirement_id: REQ-0058-acceptance-card-check-entry-simplification
acceptance_status: passed
priority: P2
created_at: '2026-10-31 23:10:48'
updated_at: 2026-11-01 08:06:38
owner: 产品团队
source: capture.md 与同会话探索
captured_via: capture
classification_rationale: 调整已交付检查入口的展示位置，保留检查能力，属于交互改进需求。
lifecycle_stage: plan
iteration: null
openspec_changes: []
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0071-change-summary-acceptance-check-entry-missing
product_data_collection_observability:
  acceptance_status: applicable
  affected_layers:
  - web
  reason: 仅删除卡片JSX，不新增请求或日志事件；API、DB、request_logs、usage_events、Task Trace、请求封装、部署、存储及权限契约均不变。
  validation: AC-001至AC-004的5项前端回归与隔离实际前后端检查通过；无客户端生成变化。
  standard_ref: docs/standards/product-data-collection-observability.md
title: 验收中卡片检查入口展示简化验收清单
terminal: web-catalog
version: v1
---

# 验收中卡片检查入口展示简化验收清单

## 功能 AC
- [x] AC-001 验收卡无acceptance-check、acceptance-readiness及目标按钮，所有检查状态均不产生占位。
- [x] AC-002 不新增归档准备弹窗、入口或自动检查请求；保留原有卡片动作及禁用语义。
- [x] AC-003 既有迭代检查可调用、失败可重试；刷新仍读取摘要，迟到响应保护不变。
- [x] AC-004 文档、进度、标签及红框外提示保留，权限与归档证据门禁未改变。
## 横切 AC（knowledge-base）
- [x] AC-XCUT-001 单元合成回归与真实产品证据分别记录；旧弹窗截图不得冒充当前验收。
## 原型驱动 UI AC
- [x] AC-PROTOTYPE-001 原型仅展示删除行后的卡片，设计与最新用户范围一致。
- [x] AC-PROTOTYPE-002 1440px与390px检查无空白占位、无新增弹窗，记录computed style及截图。
- [x] AC-PROTOTYPE-003 最终REQ文档与实际行为一致。
## 观测与边界
复用原有API与请求观测，不修改契约；DB、部署、存储N/A。无新请求行为；自动验收按钮原本禁用，不承诺本次启用。原本地页面刷新后验收列为空；已按用户授权在隔离实际前后端以合成事项覆盖双视口，详见Change视觉证据，不以空列证明通过。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-11-01 08:06:38
accepted_by: workflow-sync
source_change: update-acceptance-card-check-entry
source_sprint: sprint-018
evidence: [openspec/archive/2026-10-31-update-acceptance-card-check-entry/evidence/acceptance/20261101002352954216-978dece2/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

