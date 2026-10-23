---
bug_id: BUG-0048-chat-legacy-panel-cleanup-removes-conversation
severity: high
created_at: '2026-10-19 18:48:04'
updated_at: 2026-10-19 22:43:47
owner: 产品团队
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0047-review-recovery-operation-record-missing
title: 旧治理面板清理误删聊天会话区域追溯
status: done
lifecycle_stage: archive
lifecycle:
  captured: '2026-10-19 18:48:04'
  generated: 2026-10-19 18:48:22
  completed: 2026-10-19 18:48:36
  reviewed: '2026-10-19 18:48:04'
  approved: '2026-10-19 18:48:04'
iteration: sprint-010
related_change: fix-chat-legacy-panel-cleanup-boundary
openspec_changes:
- change_id: fix-chat-legacy-panel-cleanup-boundary
  type: fix
  status: archived
---

# 旧治理面板清理误删聊天会话区域追溯

## 授权与范围

用户明确授权修复、同步本地容器、页面验证后重新执行 REQ-0046 评审并核验应用。只修正旧面板清理边界，不改变评审结论、权限或成果校验。

## 观测边界

product_data_collection_observability: not_applicable；affected_layers: web。只修改 DOM 清理选择器与测试，不改变 API、DB、请求封装、usage_events、request_logs、Task Trace 或保留周期。验证以 DOM 回归、页面截图和既有评审应用记录回读完成。
