## MODIFIED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。跨项目学习应用命令执行顺序时，系统 MUST 产出可复用的命令顺序规则，并避免复制学习对象业务专属流程。

#### Scenario: 应用治理命令输出契约学习结果

- **WHEN** 用户确认应用外部 Harness 的命令输出契约治理经验
- **THEN** 系统 MUST 将输出契约改写为 MoonBox 技能、规则和校验脚本中的卫生约束
- **AND** 系统 MUST 校验命令技能不得保留易被原样输出的尖括号占位模板
- **AND** 系统 MUST 校验用户可见示例不得泄漏 `MUST`、`SHOULD` 或契约章节名等规范语气
- **AND** 系统 MUST NOT 复制学习对象业务专属命令或示例数据

## ADDED Requirements

### Requirement: Sprint AI Usage 矩阵语义

MoonBox MUST 在 Sprint AI Usage 复盘矩阵中区分真实数值 `0` 与未观测 workflow 阶段，避免将采集缺口误读为真实零成本。

#### Scenario: 未观测 workflow 阶段显示为短横线

- **WHEN** Sprint AI Usage 矩阵中某个对象和 workflow 阶段没有匹配 command run
- **THEN** 数据层 MUST 将该单元标记为 `unknown`
- **AND** Markdown 复盘输出 MUST 将该单元渲染为 `-`
- **AND** 已观测但 token 或调用次数为零的单元 MUST 保持数字 `0`
