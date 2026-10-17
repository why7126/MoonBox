---
title: Chat 关联 Issue 首次归档验收证据规格
created_at: 2026-10-12 11:20:00
updated_at: 2026-10-12 11:20:00
---

# Chat 关联 Issue 首次归档验收证据规格

## ADDED Requirements

### Requirement: 关联 Issue 首次归档须完成同轮阶段迁移

Chat source 工作区对关联 Issue 执行首次归档时，验收 MUST 核对同一产品轮次内的规格合并、唯一标准归档目录、Workflow Sync、Issue promote 和最终完成状态；宿主续跑应单独记录。

#### Scenario: 关联 Issue 同轮归档完成

- **WHEN** 已完成任务和交付证据门禁的关联 Issue 在对象 Chat 首次执行 `/opsx-archive`
- **THEN** 标准脚本退出 0，Change 移入唯一标准归档目录，Issue 迁入 archive，注册表与当前态索引同步，产品轮次为 completed。

#### Scenario: 关联 Issue 归档中断

- **WHEN** 产品轮次在 Change 目录迁移、Workflow Sync 或 Issue promote 阶段中断
- **THEN** 验收保留原始失败事实；事后恢复不替代首次产品归档通过。
