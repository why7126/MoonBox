## MODIFIED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。跨项目学习应用命令执行顺序时，系统 MUST 产出可复用的命令顺序规则，并避免复制学习对象业务专属流程。

#### Scenario: 应用数据采集治理学习结果

- **WHEN** 用户确认应用外部 Harness 的数据采集与链路观测治理经验
- **THEN** 系统 MUST 将学习结果改写为 MoonBox 的标准文档、规则摘要、技能门禁和校验脚本
- **AND** 系统 MUST 要求涉及 API、DB、日志审计、行为埋点、Task Trace、请求封装、对象存储或 Agent Workflow 链路观测的 REQ、Change、Sprint 或验收材料声明 `product_data_collection_observability`
- **AND** 声明 MUST 包含 `status`、`affected_layers`、`reason` 和 `validation`
- **AND** 系统 MUST NOT 复制学习对象的小程序/App、瓷砖业务、店主端、具体业务字段或运行时数据表实现
