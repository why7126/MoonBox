## MODIFIED Requirements

### Requirement: 引导式用户反馈契约

系统 MUST 在 Agent 命令需要用户选择、确认、补充信息或处理阻塞时，优先使用原生交互卡片组织问题；当客户端或工具层不支持原生交互卡片时，必须降级为文本结构化选项，并保持结构化选项、推荐项和可补充说明入口。

#### Scenario: 交互卡片顶部说明避免重复

- **WHEN** Agent 使用原生交互卡片向用户收集选择、确认或补充信息
- **THEN** 卡片顶部 MUST 只保留一处主说明来承载流程背景或决策意图
- **AND** 副标题、hint、description 或说明正文 MUST NOT 重复承载同一流程信息
- **AND** 其他字段 SHOULD 只提供互补约束、选项差异或补充说明入口

#### Scenario: 文本降级输出保持紧凑

- **WHEN** 原生交互卡片不可用，Agent 降级为文本结构化选项
- **THEN** Agent MUST 保留结构化选项、推荐项和可补充说明
- **AND** Agent SHOULD 避免在标题、说明和提示语中重复表达同一流程信息
