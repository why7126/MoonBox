---
title: Chat 归档历史引用过渡验收证据补充规格
created_at: 2026-10-12 09:25:51
updated_at: 2026-10-12 09:25:51
---

# Chat 归档历史引用过渡验收证据补充规格

## ADDED Requirements

### Requirement: 历史引用在合法归档过渡期保持同轮可核对

Chat source 工作区归档验收 MUST 核对主对象在 OpenSpec CLI 旧目录过渡期的历史引用再授权、归档权限、命令完成、标准目录与 Workflow Sync；不得以宿主恢复替代产品同轮通过。

#### Scenario: 唯一旧目录过渡并完成归档

- **WHEN** 已授权的归档轮次把完整唯一的主对象 Change 移至 CLI 旧归档目录
- **THEN** 同轮历史引用仍可核对，随后完成标准目录、规格合并、Workflow Sync 和命令成功终态。

#### Scenario: 旧目录事实冲突或中断

- **WHEN** 旧目录缺失、身份冲突或轮次在过渡期中断
- **THEN** 保留失败原因与文件事实，拒绝冒认产品成功，宿主恢复单独记录。
