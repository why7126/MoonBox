---
bug_id: BUG-0041-chat-archive-issue-promote-retest
title: Chat 关联 Issue 首次归档复验夹具验收标准
acceptance_status: passed
created_at: '2026-10-12 13:14:18'
updated_at: 2026-10-17 17:01:21
---

# Chat 关联 Issue 首次归档复验夹具验收标准

- [x] AC-001 完成任务、OpenSpec strict、中文标题、Sprint 和关联 Issue 权限回归。
- [x] AC-002 归档前确认 Change 与 BUG 身份、来源追溯、任务与交付证据。
- [x] AC-003 明确本对象只用于复验；BUG-0026 单独记录真实产品首次归档结果。

## 数据采集与链路观测

仅补充治理规格；无新增采集字段，沿用 BUG-0026 的脱敏事件约束。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: fix-chat-archive-issue-promote-retest
source_sprint: sprint-009
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
