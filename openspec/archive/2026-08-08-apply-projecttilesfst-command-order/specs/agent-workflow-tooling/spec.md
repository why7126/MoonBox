## MODIFIED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。跨项目学习应用命令执行顺序时，系统 MUST 产出可复用的命令顺序规则，并避免复制学习对象业务专属流程。

#### Scenario: 应用命令执行顺序学习结果

- **WHEN** 用户确认应用跨项目命令执行顺序学习结果
- **THEN** 系统 MUST 将推荐命令链路写入本项目治理文档或技能
- **AND** 系统 MUST 区分 REQ、BUG、Sprint、OpenSpec、release、image 和 usage-docs 命令族的先后关系
- **AND** 系统 MUST 明确会写同一机器事实源的步骤需要串行执行
- **AND** 系统 MUST NOT 复制学习对象业务专属命令作为 MoonBox 默认流程

## ADDED Requirements

### Requirement: 命令执行顺序治理

MoonBox MUST 维护 AI 工作流命令的推荐执行顺序，并在技能输出中给出符合链路身份的下一步命令。REQ 来源链路的后续实现和归档命令 MUST 使用原始 `REQ-*`，BUG 来源链路 MUST 使用原始 `BUG-*`，无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: 推荐标准执行顺序

- **WHEN** 系统需要引导用户从需求或缺陷进入交付
- **THEN** 系统 SHOULD 推荐 `capture/complete/review → sprint-propose → req-opsx/bug-opsx → opsx-apply → opsx-modify → opsx-archive → sprint-archive → release/image/usage-docs` 的顺序
- **AND** `opsx-modify` MUST 只用于 `opsx-apply` 后、`opsx-archive` 前的验收返修
- **AND** release、image 和 usage-docs 命令 SHOULD 位于 OpenSpec 与 Sprint 关键门禁之后

#### Scenario: 串行写入事实源

- **WHEN** 命令会写入 `sprint.yaml`、Workflow Sync 派生块、Issue promote 结果或 AI Usage snapshot
- **THEN** 系统 MUST 严格串行执行这些步骤
- **AND** 系统 MUST NOT 并行运行多个会写同一 Sprint scope、Issue 状态或 AI Usage snapshot 的命令
- **AND** 系统 MUST 先写机器事实源，再运行 Workflow Sync 和对应校验
