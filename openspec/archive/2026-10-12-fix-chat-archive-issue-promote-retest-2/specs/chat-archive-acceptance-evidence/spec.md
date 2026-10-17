---
title: Chat 关联 Issue 首次归档复验证据规格
created_at: 2026-10-12 13:16:40
updated_at: 2026-10-12 13:16:40
---

# Chat 关联 Issue 首次归档复验证据规格

## ADDED Requirements

### Requirement: 关联 Issue 首次归档再次中断后使用第三份独立复验样本

当首次归档轮次中断且产品终态为 stopped 或 unknown 时，验收 MUST 保留原轮次事实，并使用新的已关联 Issue 样本取得完整同轮成功证据，不能把文件迁移或宿主恢复替代产品成功。

#### Scenario: 新样本同轮完成

- **WHEN** 已完成任务与交付门禁的新关联 Issue 在对象 Chat 首次执行归档
- **THEN** 标准脚本退出 0，Change 规格与唯一归档目录同步，Issue 迁入 archive，注册表与 Sprint 状态同步，产品轮次为 completed。

#### Scenario: 新样本再次中断

- **WHEN** 新样本归档轮次在任一阶段中断
- **THEN** 保留错误、工具事件和文件事实，不将其计为 AC-001 通过。
