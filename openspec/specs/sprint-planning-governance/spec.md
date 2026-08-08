# sprint-planning-governance Specification

## Purpose
TBD - created by archiving change apply-projecttilesfst-spec-study. Update Purpose after archive.
## Requirements
### Requirement: Sprint 自动编号与规范命名

MoonBox MUST 使用 `sprint-xxx` 三位数字递增格式命名 Sprint，并在当前没有进行中迭代且需要自动创建 Sprint 时按最新编号加一创建。

#### Scenario: 无进行中迭代时自动创建下一个 Sprint

- **WHEN** 当前不存在 `iterations/change/sprint-[0-9]{3}/` 进行中 Sprint
- **AND** 命令需要为 active Change 自动创建 Sprint
- **THEN** 系统 MUST 扫描 `iterations/archive/` 与 `iterations/change/` 下符合 `sprint-[0-9]{3}` 的目录和 `sprint.yaml:sprint_id`
- **AND** 系统 MUST 取最大编号加一作为新 Sprint ID
- **AND** 如果最新归档 Sprint 为 `sprint-001` 且无进行中 Sprint，新建 Sprint MUST 为 `sprint-002`

#### Scenario: 存在进行中迭代时不得默认新建并行 Sprint

- **WHEN** `iterations/change/` 下已存在 `sprint-[0-9]{3}/`
- **THEN** 系统 MUST 优先复用该进行中 Sprint 或要求用户明确选择
- **AND** 系统 MUST NOT 默认另建并行 Sprint

#### Scenario: 非规范 Sprint 名称必须修正

- **WHEN** 系统发现新建 Sprint 使用日期、主题词或混合命名，例如 `sprint-2026-08-07-spec-study`
- **THEN** 系统 MUST 将其重命名为自动编号结果
- **AND** 系统 MUST 同步更新四件套 `sprint_id`、标题、路径引用、Workflow Sync、AI Usage 和校验命令

