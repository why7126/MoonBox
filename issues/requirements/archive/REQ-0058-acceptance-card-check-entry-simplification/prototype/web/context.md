---
requirement_id: REQ-0058-acceptance-card-check-entry-simplification
document_status: draft
priority: P2
created_at: '2026-10-31 23:10:48'
updated_at: '2026-11-01 00:22:06'
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
  status: applicable
  affected_layers:
  - web
  reason: 仅删除卡片JSX，不新增请求或日志事件；API、DB、request_logs、usage_events、Task Trace、请求封装、部署、存储及权限契约均不变。
  validation: AC-001至AC-004的5项前端回归与隔离实际前后端检查通过；无客户端生成变化。
  standard_ref: docs/standards/product-data-collection-observability.md
title: 验收中卡片检查入口展示简化原型说明
terminal: web-catalog
version: v1
---

# 验收中卡片检查入口展示简化原型说明

用户最新确认：不新增弹窗，仅移除卡片“检查验收条件 / 验收待检查”整行，检查沿用现有流程。此前归档准备面板方案已撤回；不修改原有按钮、禁用条件、确认流程、检查API或服务端门禁。

## 拆解与参考契约
局部一致：截图红框确定删除区。页面壳、列头、卡片标题/标签/文档/进度/footer保持。目标selector为acceptance-check、acceptance-readiness（预期不存在），卡片rc-card。
## 状态与动作矩阵
原有返修、自动验收、完成/归档保持对应现有流程和权限；无新增modal。检查状态不能插回卡片。模拟卡片只验证删除范围，不调用API。
## 样式证据
1440px、390px采样卡片height、gap、padding、font-size、overflow；以现有token为准，删除区高度为零。旧新弹窗骨架已撤回；本次隔离真实前后端双视口证据已采集，见Change证据目录。
