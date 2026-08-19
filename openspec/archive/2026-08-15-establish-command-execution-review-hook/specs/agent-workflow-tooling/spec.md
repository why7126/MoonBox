## ADDED Requirements

### Requirement: 命令执行复盘 Hook
MoonBox SHALL 在 workflow 命令完成后输出轻量命令执行复盘，反馈本次链路状态、问题证据和规范优化建议。该 Hook SHALL NOT 自动创建 follow-up REQ、BUG 或 Change，除非用户明确授权。

#### Scenario: 成功命令输出轻量复盘
- **WHEN** workflow 命令完成且所有关键门禁通过
- **THEN** 系统 SHALL 输出 `执行链路复盘`
- **AND** 复盘 SHALL 包含链路状态、问题证据和规范优化建议
- **AND** 若未发现问题，系统 SHALL 输出“无明显优化点”或等价简短结论

#### Scenario: Warning 或 blocker 必须引用证据
- **WHEN** 命令执行中出现 warning、blocker、脚本失败、文档漂移、门禁阻断或执行链路不顺
- **THEN** 系统 SHALL 在复盘中引用脚本输出、文件路径、校验报告、日志摘要或用户提供证据
- **AND** 系统 SHALL NOT 在没有证据时猜测流程根因

#### Scenario: Follow-up 只输出建议不自动创建
- **WHEN** 复盘发现可沉淀的规范优化、缺陷或需求线索
- **THEN** 系统 SHALL 输出建议命令，例如 `/spec-opt`、`/bug-capture`、`/req-capture` 或 `/capture`
- **AND** 系统 SHALL 明确未自动创建 follow-up Issue 或 Change
- **AND** 只有用户明确授权时，系统才 MAY 进入对应创建流程
