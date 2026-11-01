---
requirement_id: REQ-0058-acceptance-card-check-entry-simplification
status: done
priority: P2
created_at: '2026-10-31 23:10:48'
updated_at: 2026-11-01 00:26:32
owner: 产品团队
source: capture.md 与同会话探索
captured_via: capture
classification_rationale: 调整已交付检查入口的展示位置，保留检查能力，属于交互改进需求。
lifecycle_stage: archive
iteration: null
openspec_changes: []
related_requirement: REQ-0056-requirement-center-change-delivery-cards
related_bug: BUG-0071-change-summary-acceptance-check-entry-missing
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  reason: 仅删除卡片JSX，不新增请求或日志事件；API、DB、request_logs、usage_events、Task Trace、请求封装、部署、存储及权限契约均不变。
  validation: AC-001至AC-004的5项前端回归与隔离实际前后端检查通过；无客户端生成变化。
  standard_ref: docs/standards/product-data-collection-observability.md
title: 验收中卡片检查入口展示简化
terminal: web-catalog
version: v1
---

# 验收中卡片检查入口展示简化

用户最新确认：不新增弹窗，仅移除卡片“检查验收条件 / 验收待检查”整行，检查沿用现有流程。此前归档准备面板方案已撤回；不修改原有按钮、禁用条件、确认流程、检查API或服务端门禁。

## 背景、用户与范围
产品经理查看验收卡时希望减少常驻信息。仅移除acceptance-check整块及自然布局占位；保留红框外失败提示、文档、进度、负责人、人力、返修、自动验收和归档动作。
## 功能要求
- FR-001 所有验收卡不再渲染检查按钮、待检查状态及检查结果专用行。
- FR-002 不新增弹窗或入口，保留已有CLI验收、对象检查API及检查迭代归档条件流程；原有自动验收按钮目前禁用，不在本需求启用。
- FR-003 保留摘要首屏、刷新、失败重试与迟到响应隔离，归档仍受原权限和有效证据限制。
## UI与验证
局部删除，不修改样式token；1440px/390px验证卡片无空白占位、无新增弹窗。旧骨架截图为已撤回方案，不用于本次验收。实现前用户已明确缩减范围；不再要求新面板骨架。
## 边界与观测
API/DB/部署/对象存储/权限契约不变，无需OpenAPI/Orval生成。复用既有请求观测，引用docs/standards/product-data-collection-observability.md；不新增采集事件。
## 状态与关联
in_sprint，关联REQ-0056、BUG-0071，估算修复由BUG-0073承接。范围依用户最新说明更新，不重开历史交付。
