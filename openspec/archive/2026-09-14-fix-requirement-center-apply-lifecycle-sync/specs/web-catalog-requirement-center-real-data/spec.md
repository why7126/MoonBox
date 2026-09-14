---
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 21:00:30
updated_at: 2026-09-12 21:00:30
---

## MODIFIED Requirements

### Requirement: 9 阶段状态映射

系统 SHALL 将 REQ、BUG、Sprint 和 OpenSpec Change 状态映射到采集池、规划中、待评审、已评审、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。

#### Scenario: 已纳入 Sprint 但未创建 Change

- **WHEN** REQ 或 BUG 状态为 `in_sprint` 且没有关联 OpenSpec Change
- **THEN** 系统将该对象映射到“迭代规划”阶段

#### Scenario: Change 已创建但未 apply

- **WHEN** REQ 或 BUG 已关联 OpenSpec Change 且 Change 尚未完成 apply
- **THEN** 系统依据统一执行事实源将未启动对象映射到“待开发”、已启动对象映射到“研发中”，并独立返回真实任务进度摘要

#### Scenario: 已闭环对象

- **WHEN** REQ 或 BUG 状态为 `done` 或关联 Change 已归档
- **THEN** 系统将该对象映射到“已完成”阶段

#### Scenario: approved 展示为已评审

- **WHEN** REQ 或 BUG 的底层状态为 `approved`
- **THEN** 前端展示阶段必须为“已评审”
- **AND** API 可以保留 `approved` 作为机器状态，但必须提供可展示中文阶段或等价映射

#### Scenario: 已启动零完成任务

- **WHEN** Change已记录启动事实且完成数为0/N
- **THEN** 系统 MUST 返回研发中阶段与真实零进度，并提供查看进度动作

#### Scenario: 执行状态刷新一致

- **WHEN** 启动、进度或完成事实变化并成功刷新context
- **THEN** 系统 MUST 返回与治理事实源一致的阶段、动作、任务数及更新后的快照标识
- **AND** 轮询、焦点刷新及手动刷新 MUST 不依赖仅存在于前端的模拟状态，项目切换后不能串卡

#### Scenario: 完成门禁后进入验收

- **WHEN** 新契约Change通过完成门禁并记录完成事实
- **THEN** 系统 MUST 映射为验收中；仅全勾选但无完成事实时保持研发中
