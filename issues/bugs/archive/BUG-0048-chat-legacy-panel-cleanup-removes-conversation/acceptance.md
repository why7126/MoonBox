---
bug_id: BUG-0048-chat-legacy-panel-cleanup-removes-conversation
severity: high
created_at: '2026-10-19 18:48:04'
updated_at: 2026-10-20 08:19:17
owner: 产品团队
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0047-review-recovery-operation-record-missing
title: 旧治理面板清理误删聊天会话区域验收标准
acceptance_status: passed
---

# 旧治理面板清理误删聊天会话区域验收标准

## 验收项

- AC-001：包含每个旧面板关键词的普通消息、带标签会话外壳及无关 dialog 均保留。
- AC-002：明确旧面板仍被清理；正常邻接区域保留，重复调用幂等。
- AC-003：本地容器运行新 bundle；原目标会话在 1440px 显示正文、输入区和轨迹，刷新后仍可用。
- AC-004：页面正常后重新执行 REQ-0046 的 req-review；不重写旧失败终态，核对新轮次、评审文件、registry、trace 与唯一应用结果。

## 边界

这是 DOM 完整性修复，不涉及原型复刻、视觉重设计或新动作/modal。使用真实 API 进行产品验证，无 Mock 作为产品证据。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:17
accepted_by: workflow-sync
source_change: fix-chat-legacy-panel-cleanup-boundary
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-fix-chat-legacy-panel-cleanup-boundary/evidence/acceptance/20261019193626990093-561eee3a/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 逐项复验与签认

- [x] AC-001：通过，五类旧文案普通消息/祖先/无关对话框均保留。
- [x] AC-002：通过，明确旧面板清理且幂等。
- [x] AC-003：通过，1440×900真实会话刷新、正文、输入和轨迹目视/样式证据已核对。
- [x] AC-004：通过，最后真实评审completed且唯一应用applied/verified，正式9文件与approved/review/P2一致，原失败保留。
- [x] AC-005：通过，96项后端回归覆盖trace身份、内容边界和源码/治理投影分离。

证据：openspec/archive/2026-10-19-fix-chat-legacy-panel-cleanup-boundary/evidence/acceptance/。UI布局未改变；API/DB/生成客户端无需同步，部署说明已同步。
