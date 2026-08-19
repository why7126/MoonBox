## ADDED Requirements

### Requirement: 命令执行复盘 Hook Skill 覆盖

所有 `.agents/skills/` 命令 Skill MUST 保留 Command Execution Review Hook 短引用，指向 `.agents/skills/workflow-sync/SKILL.md` 中央契约，并显式包含「执行链路复盘」「链路状态」「问题证据」「规范优化建议」和「未自动创建 Issue/Change」。

#### Scenario: 命令 Skill 包含短引用

- **GIVEN** 一个 `.agents/skills/<command>/SKILL.md`
- **WHEN** 该文件描述命令最终输出契约
- **THEN** 它 MUST 包含 Command Execution Review Hook 短引用
- **AND** 短引用 MUST 指向 `.agents/skills/workflow-sync/SKILL.md`

#### Scenario: 校验脚本发现漏引用

- **GIVEN** 一个命令 Skill 缺少 Command Execution Review Hook 短引用
- **WHEN** 运行 `python scripts/validate-agent-context-budget.py`
- **THEN** 校验 MUST 失败
- **AND** 输出缺失短引用的文件路径与缺失字段
