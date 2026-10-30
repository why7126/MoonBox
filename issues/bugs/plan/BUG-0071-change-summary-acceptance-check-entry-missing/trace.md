---
bug_id: BUG-0071-change-summary-acceptance-check-entry-missing
title: 独立 Change 归档按钮禁用且缺少验收检查入口追溯记录
status: pending_review
severity: high
created_at: '2026-10-30 09:38:45'
updated_at: 2026-10-30 09:49:12
owner: 产品团队
source: 用户 capture 授权与同会话 explore
captured_via: capture
classification_rationale: 已有归档操作因摘要延迟检查形成无法操作的断点，属于缺陷。
lifecycle_stage: plan
environment: local
iteration: null
openspec_changes: []
related_requirement: null
related_bug: BUG-0054-change-card-blocked-reason-missing
related_bugs:
- BUG-0054-change-card-blocked-reason-missing
- BUG-0056-requirement-center-context-load-latency
root_cause_status: confirmed
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - web_request_wrapper
  - usage_events
  - request_logs
  reason: 涉及卡片级验收检查请求和状态回填；后续执行归档仍走现有授权及 Task Trace，不以检查替代执行授权。
  validation: 本次复用浏览器刷新观察与代码路径，未执行归档；后续验证检查权限、行为与请求关联、失败重试、缓存失效及脱敏。DB、部署、对象存储暂无修改目标，客户端生成视
    API 契约差异决定。
lifecycle:
  captured: '2026-10-30 09:38:45'
  generated: 2026-10-30 09:41:40
  completed: 2026-10-30 09:49:12
  reviewed: null
  approved: null
readiness: Ready
---

# 独立 Change 归档按钮禁用且缺少验收检查入口追溯记录

## 当前摘要

根因、临时处理办法及验收清单已补齐，根因证据已形成；未评审、未纳入 Sprint、未创建 Change。判重见 capture.md，根因见 root-cause.md，回归见 acceptance.md。来源样本的 sprint-016 不自动成为本 BUG 归属。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-30 09:49:12 | /bug-complete | BUG-0071-change-summary-acceptance-check-entry-missing 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-30 09:41:40 | /bug-generate | BUG-0071-change-summary-acceptance-check-entry-missing 已生成 bug.md，状态同步为 draft。 |
| 2026-10-30 09:38:45 | bug.capture | captured | 用户确认新建关联 BUG，保留旧归档事实。 |
