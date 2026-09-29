# issue-classification-metadata Specification

## Purpose
规范 REQ priority 与 BUG severity 的 Frontmatter 归属、事实源优先级、同步镜像、汇总展示和异常处理，保证需求与缺陷分级语义独立且可追溯。
## Requirements
### Requirement: Issue 分级元数据独立归属

系统 SHALL 在 REQ 使用 priority，在 BUG 使用 severity；trace Frontmatter 保存当前事实，已存在 capture 和主文档保持一致，注册表及汇总仅投影。

#### Scenario: 汇总类型区分

- **WHEN** 生成 Sprint 范围表、需求中心卡片或需求中心上下文 API 响应
- **THEN** REQ 汇总与卡片数据必须使用 `priority`
- **AND** BUG 汇总与卡片数据必须使用 `severity`
- **AND** BUG 不得因缺少 `priority` 被默认投影为 `P2`
- **AND** REQ 表头和卡片语义使用“优先级”，BUG 表头和卡片语义使用“严重度”

#### Scenario: 缺失或非法分级

- **WHEN** 聚焦 Issue 无合法分级来源或最高优先来源显式值非法
- **THEN** 同步、构卡或 API 聚合链路必须报告可诊断错误
- **AND** 系统不得猜测或写入默认等级
- **AND** BUG 不得回退为 REQ 的 P 值展示

