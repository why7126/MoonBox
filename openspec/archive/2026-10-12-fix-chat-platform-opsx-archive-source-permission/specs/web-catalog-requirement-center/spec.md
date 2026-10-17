---
title: Chat 平台 source 工作区归档权限与状态诊断修复
created_at: '2026-10-04 11:17:53'
updated_at: '2026-10-04 11:17:53'
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## MODIFIED Requirements

### Requirement: 阶段动作门禁

系统 MUST 根据治理对象类型和当前阶段提供正确主动作，并在阶段产物缺失、真实写入能力未接入或验收未完成时阻止错误流转。

#### Scenario: Requirement 和 Bug 主动作按阶段映射

- **WHEN** 用户查看某个阶段的 Requirement 或 Bug 卡片
- **THEN** 系统必须根据对象类型与阶段映射 `req-*`、`bug-*`、`sprint-*` 或 `opsx-*` 主动作
- **AND** 卡片主动作必须展示产品化文案，例如“生成需求 →”“加入迭代 →”“开始开发 →”“完成 / 归档 →”
- **AND** 实现必须保留可追溯命令映射，避免仅以裸 `/req-*` 或 `/opsx-*` 命令作为用户可见按钮文案
- **AND** 采集池对象必须指向生成文档动作
- **AND** 待评审对象必须指向评审动作
- **AND** 已通过对象必须指向 Sprint 规划动作
- **AND** 迭代规划对象必须指向 OpenSpec Change 创建动作
- **AND** 每个动作必须声明产品真实能力状态，区分真实候选写入、真实应用写入、demo 模拟和仅展示

#### Scenario: 满足门禁后完成归档

- **WHEN** 对象处于验收中
- **AND** 必要任务和验收项均满足完成条件
- **THEN** 系统必须允许发送 `/opsx-archive <完整 REQ 或 BUG ID>`
- **AND** Chat 平台执行该命令时 MUST 使用后端重读的治理事实源和 archive 专用写权限
- **AND** 归档成功后对象必须进入已完成阶段
- **AND** 若执行前发现事实源版本变化、归档权限不足或工具链不可用，系统必须进入 failed、conflict 或 stale 状态，不得展示为成功或移动卡片阶段
