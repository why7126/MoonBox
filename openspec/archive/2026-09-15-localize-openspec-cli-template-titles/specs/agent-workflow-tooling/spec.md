## MODIFIED Requirements

### Requirement: OpenSpec 中文优先语言校验

MoonBox MUST 校验 OpenSpec Change 文档的标题、任务项和业务叙述中文优先。校验可以按全部 active Change 执行，也可以按一个或多个指定 Change 聚焦执行；聚焦模式只用目标 Change 决定退出码，非目标残留通过分离报告呈现。

#### Scenario: req-opsx 与 bug-opsx 中文化 CLI 模板标题

- **WHEN** `/req-opsx <REQ-full-id>` 或 `/bug-opsx <BUG-full-id>` 使用 OpenSpec CLI `instructions` 或 template 生成 Change 文档
- **THEN** 系统 MUST 将 `proposal.md`、`design.md` 和 `tasks.md` 的英文脚手架标题替换为项目中文标题
- **AND** `Why` MUST 写为 `背景`
- **AND** `What Changes` MUST 写为 `变更内容`
- **AND** `Capabilities` MUST 写为 `能力影响`
- **AND** `Impact` MUST 写为 `影响范围`
- **AND** `Implementation`、`Testing` 和 `Documentation` MUST 写为中文任务标题
- **AND** 系统 MUST NOT 将 CLI template 中的 HTML 注释、尖括号占位符或英文说明原样写入最终 Change 文档
- **AND** OpenSpec 关键字、命令、路径、API 字段、代码标识和 capability ID MAY 保留英文
