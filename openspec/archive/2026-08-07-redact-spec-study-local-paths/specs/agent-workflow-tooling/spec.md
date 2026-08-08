## MODIFIED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告，且持久化学习对象时 MUST 使用脱敏项目标识，不得记录本机绝对路径、系统用户名或用户主目录。

#### Scenario: 输出学习报告

- **WHEN** 系统完成 `/spec-study apply`
- **THEN** 系统 MUST 输出学习报告
- **AND** 学习报告 MUST 写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`
- **AND** 同一次学习应用流程 MUST 只生成一份正式 `study` 报告
- **AND** 如同一流程已有学习报告，系统 MUST 更新该报告而不是创建第二份 `study` 报告
- **AND** 学习阶段候选内容 MUST NOT 另行落盘为第二份正式 `study` 报告
- **AND** `/spec-study` 触发的治理资产应用结果 MUST 汇总到同一份 `study` 报告
- **AND** 系统 MUST NOT 为同一 `/spec-study` 流程额外生成内容重复的 `YYYYMMDDhhmmss-governance-xxx.md`
- **AND** 学习报告 MUST NOT 包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、学习对象源码、本机绝对路径、系统用户名或用户主目录

#### Scenario: 记录学习对象

- **WHEN** 系统在学习报告、治理日志、active Change trace 或最终回复中记录本地学习对象
- **THEN** 系统 MUST 使用项目名或脱敏占位符描述学习对象
- **AND** 系统 SHOULD 使用 `ProjectName（本地只读项目）` 或 `<local-project>/ProjectName` 格式
- **AND** 系统 MUST NOT 写入 `/Users/<name>/...`、`/home/<name>/...`、用户主目录、系统用户名或可反推出个人环境的目录结构
