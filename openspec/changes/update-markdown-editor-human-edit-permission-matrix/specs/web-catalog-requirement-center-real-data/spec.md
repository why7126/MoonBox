## ADDED Requirements

### Requirement: 文档能力对象接口

系统 SHALL 在需求中心文档列表和文档读取相关响应中返回每个文档的结构化能力对象，并在过渡期将旧 `editable` 字段作为 `human_editable` 的兼容别名。

#### Scenario: 文档列表返回能力对象

- **WHEN** 前端请求需求中心对象的文档列表
- **THEN** 每个文档响应项 SHALL 包含 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only` 和 `reason`
- **AND** `reason` SHALL 使用可展示的脱敏业务原因

#### Scenario: editable 兼容 human_editable

- **WHEN** 响应仍包含旧字段 `editable`
- **THEN** `editable` SHALL 与 `human_editable` 等值
- **AND** 新增后端和前端逻辑 SHALL 以能力对象为准

#### Scenario: trace 系统可变更但人工只读

- **WHEN** 文档名为 `trace.md`
- **THEN** `human_editable` SHALL 为 false
- **AND** `task_toggle_only` SHALL 为 false
- **AND** `ai_mutable` MAY 为 true 以表达 Workflow Sync、AI 命令和治理脚本可按门禁写入

### Requirement: 文档保存授权校验

系统 SHALL 在人工保存 Markdown 文档或提交 task toggle 时复用后端文档能力计算结果进行最终授权，不得信任前端传入的可编辑状态。

#### Scenario: 完整 Markdown 保存需要 human_editable

- **WHEN** 用户提交完整 Markdown 保存请求
- **THEN** 后端 SHALL 重新计算文档能力
- **AND** 仅当 `human_editable=true` 时保存
- **AND** 否则返回 403 或等价受限错误

#### Scenario: task toggle 保存需要 task_toggle_only

- **WHEN** 用户提交 task toggle 保存请求
- **THEN** 后端 SHALL 重新计算文档能力
- **AND** 仅当 `task_toggle_only=true` 时进入差异校验
- **AND** 否则返回 403 或等价受限错误

#### Scenario: 验收中 tasks 只允许 checkbox 差异

- **WHEN** 后端处理 `tasks.md` checkbox-only 保存
- **THEN** 后端 SHALL 比较原文与提交内容
- **AND** 仅允许 Markdown task list marker 在 `- [ ]` 与 `- [x]` 之间切换
- **AND** 对标题、任务描述、非任务行、验收记录或其他文本变化 SHALL 拒绝保存

#### Scenario: 已生效规格人工只读

- **WHEN** 用户尝试保存 `openspec/specs/**/spec.md`
- **THEN** 后端 SHALL 拒绝人工全文保存
- **AND** 错误原因 SHALL 说明已生效规格只能通过 OpenSpec Change 和 archive 合并流程修改

### Requirement: 文档操作安全与观测

系统 SHALL 对人工文档操作、task toggle、越权拒绝和系统治理写入记录脱敏摘要，并避免在 API 响应或观测 metadata 中泄漏敏感内容。

#### Scenario: 人工文档操作进入请求日志

- **WHEN** 用户打开只读文档、保存完整 Markdown、提交 task toggle 或触发越权拒绝
- **THEN** 系统 SHALL 在请求日志中记录对象 ID、文档名、操作类型、结果、错误码和脱敏原因
- **AND** 请求日志 SHALL NOT 保存完整 Markdown 内容、完整请求体、完整响应体、Authorization、Cookie、密钥、本机路径或内部堆栈

#### Scenario: 行为事件使用稳定事件名

- **WHEN** 前端记录文档打开、全文保存、checkbox-only 保存或保存失败事件
- **THEN** 行为事件 SHALL 使用稳定事件名
- **AND** 事件属性 SHALL 仅包含对象 ID、文档名、能力类型、结果和脱敏错误码

#### Scenario: Task Trace 覆盖或说明豁免

- **WHEN** task toggle 差异校验被实现为多步骤或高风险写操作
- **THEN** 系统 SHALL 接入 Task Trace 或记录不接入的具体原因
- **AND** Task Trace metadata SHALL NOT 保存完整 Markdown 内容或完整 Prompt

#### Scenario: 系统治理写入不受 UI 只读阻断

- **WHEN** Workflow Sync、AI 命令或治理脚本按既有门禁更新 `trace.md`、`tasks.md` 或其他治理文档
- **THEN** 系统 SHALL 允许该系统写入路径继续执行
- **AND** UI 只读状态 SHALL NOT 被用作禁止系统治理写入的依据
