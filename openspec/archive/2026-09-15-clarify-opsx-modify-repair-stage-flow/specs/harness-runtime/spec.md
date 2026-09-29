## ADDED Requirements

### Requirement: opsx-modify 返修阶段流转

系统 SHALL 在 `/opsx-modify` 验收返修期间区分 Change canonical status、首次 apply execution facts、返修投影状态和验收状态。返修执行中用户可见阶段 SHALL 展示为研发中；返修完成并通过验证、文档同步和 Workflow Sync 后 SHALL 自动回到验收中。系统 SHALL 保留 Change `applied` 事实和首次 apply 的 `execution.completed_at`，不得用普通 `in_progress` 覆盖首次 apply 完成事实。

#### Scenario: 返修执行中展示研发中

- **GIVEN** Change 已完成 `/opsx-apply` 并处于 `applied`
- **WHEN** Agent 开始执行 `/opsx-modify` 并处理验收反馈
- **THEN** 用户可见阶段 SHALL 展示为研发中
- **AND** Change canonical status SHALL 继续保留 apply 完成事实
- **AND** 首次 apply 的 `execution.completed_at` SHALL NOT 被清空、覆盖或改写为新的普通进行中状态

#### Scenario: 返修完成后回到验收中

- **GIVEN** `/opsx-modify` 的返修任务、验证证据、文档同步和 Workflow Sync 已完成
- **WHEN** 返修结果仍属于原 Change 范围
- **THEN** 用户可见阶段 SHALL 回到验收中
- **AND** linked Issue 的验收入口 SHALL 保持待复验语义
- **AND** 下一步 SHALL 指向复验或 `/opsx-archive`

#### Scenario: 返修不回退 applied 事实

- **GIVEN** Change 已记录首次 apply 的 execution facts
- **WHEN** 返修过程需要表达正在处理
- **THEN** 系统 SHALL 使用返修投影语义表达研发中
- **AND** 系统 SHALL NOT 将 Change canonical status 简单覆盖为普通 `in_progress`
- **AND** 系统 SHALL NOT 伪造新的首次 apply 启动或完成时间
