---
title: Chat 关联 Issue 首次归档验收夹具追溯记录
change_id: fix-chat-archive-issue-promote-fixture
type: fix
status: applied
bug: BUG-0040-chat-archive-issue-promote-fixture
sprint: sprint-009
created_at: 2026-10-12 11:20:00
updated_at: 2026-10-12 11:12:08
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本夹具仅补充治理验收规格，不改变产品采集、请求或 Task Trace 实现。
  validation: 核对既有脱敏轮次事件与目录事实，无新增采集字段。
execution:
  schema_version: 1
  started_at: 2026-10-12 11:11:19
  completed_at: 2026-10-12 11:12:08
  last_event: opsx.apply
---

# Chat 关联 Issue 首次归档验收夹具追溯记录

## 来源

BUG-0040 是用户授权的虚拟验收样本，归属 sprint-009，仅用于 BUG-0026 的产品归档验收。

## 归档前验证

OpenSpec strict、当前 Change 中文校验通过；关联 Issue 临时旧目录与复制窗口的写权限回归 2/2 通过。产品首次归档结果待独立记录。

## 返修记录核对

关联 Issue 已记录 opsx.modify 和夹具验收 passed；归档前依现存证据补齐 acceptance-fixes.md，与 verification.md、tasks.md 和 Issue 验收投影一致。本轮交付证据校验退出 0。首次 apply 执行时间保留。
