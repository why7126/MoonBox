## MODIFIED Requirements

### Requirement: Sprint 自动编号与规范命名

MoonBox MUST 使用 `sprint-xxx` 三位数字递增格式命名 Sprint，并在当前没有进行中迭代且需要自动创建 Sprint 时按最新编号加一创建。Sprint 选择和新建编号 MUST 能通过脚本门禁复核，避免误建并行 Sprint 或跳号 Sprint。

#### Scenario: 校验默认 Sprint 选择

- **WHEN** `/sprint-propose` 未显式指定 Sprint
- **AND** 当前没有 active Sprint
- **THEN** Sprint 选择门禁 MUST 通过并提示默认创建下一个连续 Sprint
- **WHEN** 当前只有一个 active Sprint
- **THEN** Sprint 选择门禁 MUST 通过并提示默认使用当前 Sprint
- **WHEN** 当前存在两个或以上 active Sprint
- **THEN** Sprint 选择门禁 MUST 失败并要求用户显式指定 `--sprint`

#### Scenario: 校验显式新建 Sprint 编号

- **WHEN** 用户显式指定一个尚不存在的 Sprint
- **THEN** Sprint ID MUST 等于当前最大规范编号加一
- **AND** 如果已存在两个 active Sprint，系统 MUST 禁止创建第三个 active Sprint
