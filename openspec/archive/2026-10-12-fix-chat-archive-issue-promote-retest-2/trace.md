---
title: Chat 关联 Issue 首次归档复验夹具追溯记录
change_id: fix-chat-archive-issue-promote-retest-2
type: fix
status: applied
bug: BUG-0042-chat-archive-issue-promote-retest-2
sprint: sprint-009
created_at: 2026-10-12 13:16:40
updated_at: 2026-10-12 13:18:13
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 仅补充治理验收规格，不改变产品采集、请求或 Task Trace 实现。
  validation: 核对既有脱敏轮次事件与目录事实，无新增采集字段。
execution:
  schema_version: 1
  started_at: 2026-10-12 13:17:20
  completed_at: 2026-10-12 13:18:13
  last_event: opsx.apply
---

# Chat 关联 Issue 首次归档复验夹具追溯记录

## 来源

BUG-0042-chat-archive-issue-promote-retest-2 是用户授权的虚拟复验样本，归属 sprint-009，仅用于 BUG-0026 AC-001。BUG-0040 产品轮次 stopped，不可计为通过。

## 归档前验证

OpenSpec strict、中文标题、身份、目录、交付证据与关联 Issue 过渡权限回归均通过，详见 `verification.md`。`acceptance-fixes.md` 记录夹具三项归档前验收及 `opsx.modify` 同步事实；首次 apply 时间保持不变。BUG-0026 的产品首次归档结果独立留证。
