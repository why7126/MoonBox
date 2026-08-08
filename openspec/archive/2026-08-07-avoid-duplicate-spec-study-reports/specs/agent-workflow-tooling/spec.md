## MODIFIED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。同一次 `/spec-study` 学习应用流程 MUST 只生成一份正式 `study` 报告。

#### Scenario: 输出学习报告

- **WHEN** 系统完成 `/spec-study apply`
- **THEN** 系统 MUST 输出学习报告
- **AND** 学习报告 MUST 写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`
- **AND** 同一次学习应用流程 MUST 只生成一份正式 `study` 报告
- **AND** 如同一流程已有学习报告，系统 MUST 更新该报告而不是创建第二份 `study` 报告
- **AND** 学习阶段候选内容 MUST NOT 另行落盘为第二份正式 `study` 报告
- **AND** `/spec-study` 触发的治理资产应用结果 MUST 汇总到同一份 `study` 报告
- **AND** 系统 MUST NOT 为同一 `/spec-study` 流程额外生成内容重复的 `YYYYMMDDhhmmss-governance-xxx.md`
- **AND** 学习报告 MUST NOT 包含用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息或学习对象源码
