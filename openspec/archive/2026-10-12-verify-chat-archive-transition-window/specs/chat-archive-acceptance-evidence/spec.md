---
title: Chat 归档迁移窗口验收证据补充规格
created_at: 2026-10-11 11:30:53
updated_at: 2026-10-11 11:30:53
---

# Chat 归档迁移窗口验收证据补充规格

## ADDED Requirements

### Requirement: 归档迁移窗口保留可核对的权限与目录证据

Chat source 工作区归档验收 MUST 核对 OpenSpec CLI 临时旧归档目录到项目标准归档目录的迁移窗口；只有同一产品轮次在窗口后继续完成标准目录校验与 Workflow Sync，才可把这段执行记为通过。

#### Scenario: 临时目录迁移后继续归档

- **WHEN** 已授权的归档轮次将唯一 Change 暂置 `openspec/changes/archive/`，随后标准脚本迁至 `openspec/archive/`
- **THEN** 验收记录核对轮次持续执行、旧目录消失、唯一标准归档目录存在、规格合并一次及 Workflow Sync 完成。

#### Scenario: 迁移窗口中断

- **WHEN** 轮次在临时目录出现后停止或权限撤销
- **THEN** 验收记录保留产品失败状态，宿主恢复单独记载，产品首次归档结论保持待复验。
