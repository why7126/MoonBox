## ADDED Requirements

### Requirement: Workflow Sync 主状态字段解析边界

系统 MUST 在 Workflow Sync 读取 Markdown Frontmatter 主状态时，只将顶层 `status` 作为 Issue、Change 或 Sprint 主状态事实源，不得把嵌套声明对象中的同名字段提升为主状态。

#### Scenario: 嵌套观测声明状态不覆盖主状态

- **GIVEN** Issue 或 Change 文档 Frontmatter 同时包含顶层主状态和嵌套 `product_data_collection_observability` 声明状态
- **WHEN** Workflow Sync 读取该文档并推导主状态
- **THEN** 主状态必须解析为 `in_sprint`
- **AND** 嵌套 `product_data_collection_observability.status` 只能作为产品数据采集与链路观测声明状态使用
- **AND** Workflow Sync 不得因为嵌套状态值将 Issue、Change 或 Sprint 派生状态改为 `not_applicable`

#### Scenario: 轻量 Frontmatter 解析只读取顶层键

- **WHEN** Workflow Sync 使用轻量 Frontmatter 解析器读取 `status`、`title`、`priority`、`severity` 或 `updated_at`
- **THEN** 解析器必须忽略缩进字段
- **AND** 结构化嵌套对象应由结构化 YAML 解析路径读取
