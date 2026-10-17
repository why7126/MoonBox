---
bug_id: BUG-0040-chat-archive-issue-promote-fixture
title: Chat 首次归档关联 Issue 迁移验收夹具验收标准
acceptance_status: passed
created_at: '2026-10-12 11:05:30'
updated_at: 2026-10-17 17:01:21
---

# Chat 首次归档关联 Issue 迁移验收夹具验收标准

- [x] AC-001 本夹具已完成任务、OpenSpec strict、语言、Sprint 和关联 Issue 过渡权限回归。
- [x] AC-002 归档前已确认 Change 与 BUG 唯一身份、来源追溯、任务与交付证据门禁。
- [x] AC-003 本夹具明确标记测试用途；首次产品归档结果由 BUG-0026 AC-001 单独记录。

## 数据采集与链路观测

本夹具只补充治理规格，不新增采集字段；复用 BUG-0026 既有请求与 Task Trace 脱敏约束。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 17:01:21
accepted_by: workflow-sync
source_change: fix-chat-archive-issue-promote-fixture
source_sprint: sprint-009
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
