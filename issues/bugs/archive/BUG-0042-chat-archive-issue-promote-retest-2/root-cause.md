---
bug_id: BUG-0042-chat-archive-issue-promote-retest-2
title: Chat 关联 Issue 首次归档复验夹具证据缺口分析
status: confirmed
created_at: '2026-10-12 13:14:18'
updated_at: '2026-10-12 13:14:18'
---

# Chat 关联 Issue 首次归档复验夹具证据缺口分析

## 根因状态

status: confirmed

BUG-0040 的 Change 和 Issue 已在产品轮次中迁移，但该轮次对账终态为 stopped，缺少归档命令完成回执。此前纯治理样本无关联 Issue，BUG-0027 仅覆盖半归档恢复。因此 BUG-0026 AC-001 仍缺全新关联 Issue 的首次归档同轮闭环证据；本文件确认的是验收证据缺口，不声称新产品根因。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | BUG-0026 acceptance.md | BUG-0040 轮次 `7fcb3bd0-96bc-4518-ba85-0fba232bf7e1` 对账为 stopped | 已迁移文件不能替代产品同轮成功 |
| E2 | reproduction | BUG-0026 acceptance.md | 纯治理样本归档成功，但没有关联 Issue | 仍需关联 Issue 首次归档样本 |

## 修复与验证方向

建立用户已授权的独立复验夹具，完成评审、Sprint、OpenSpec、apply 与验收门禁；在真实产品对象 Chat 中核对标准脚本退出码、唯一归档、规格合并、Workflow Sync、Issue promote、产品轮次 completed。
