## MODIFIED Requirements

### Requirement: Harness 治理资产学习应用

系统 MUST 在通过 `/spec-study apply` 应用外部 Harness 学习成果时，以 MoonBox 当前 OpenSpec、REQ/BUG、Sprint、Workflow Sync 和 `.agents/skills/` 体系为事实源，转写可迁移治理能力，不得照搬外部目录结构或与本项目事实源冲突的自动化。

#### Scenario: 学习成果转写为本项目治理规则

- **WHEN** 外部 Harness 的治理能力被确认采纳
- **THEN** Agent MUST 将其改写为适配 MoonBox 的规则、文档、脚本说明、Skill 或 active Change 内容
- **AND** Agent MUST NOT 恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等非本项目入口目录
- **AND** Agent MUST NOT 修改业务 `src/` 或 `openspec/specs/` 正式规格

#### Scenario: 学习报告承载应用结果

- **WHEN** `/spec-study apply` 完成治理资产应用
- **THEN** Agent MUST 在 `docs/spec-logs/` 写入或更新一份 `YYYYMMDDhhmmss-study-xxx.md` 学习报告
- **AND** 同一次学习应用流程 MUST NOT 额外生成内容重复的 `governance` 日志
- **AND** `docs/spec-logs/CHANGELOG.md` MUST 将该学习报告作为目录级索引条目登记

### Requirement: 文档事实唯一归属

系统 MUST 为长期治理文档维护事实唯一归属，避免同一规则、状态、验收或脚本语义在多个文档中各自展开并发生漂移。

#### Scenario: 长期文档更新前确认事实源

- **WHEN** Agent 新增或修改长期文档中的规则、流程、状态、验收或脚本语义
- **THEN** Agent MUST 先确认该事实的唯一归属文档
- **AND** 其他文档 SHOULD 使用摘要和链接引用该事实源
- **AND** 不得在多个长期文档中复制同一规则的完整说明

### Requirement: 最小相关验证

系统 MUST 按变更影响面选择能够证明风险被覆盖的最小相关验证组合，并在无法覆盖时说明残余风险。

#### Scenario: 治理变更选择验证

- **WHEN** Change 只修改治理规则、Skill、文档或校验脚本
- **THEN** Agent MUST 优先运行对应治理校验、目标 OpenSpec validate、Sprint scope 和 Workflow Sync
- **AND** 业务 API、数据库、Web、管理端或客户端测试 MAY 标记为不适用
- **AND** 不适用原因 MUST 写入学习报告、治理日志、trace 或最终回复
