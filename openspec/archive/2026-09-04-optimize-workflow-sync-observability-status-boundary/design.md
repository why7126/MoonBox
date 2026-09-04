## 设计说明

### 状态字段边界

Workflow Sync 的 `parse_frontmatter()` 是面向简单 Frontmatter 的轻量解析器，调用方用它读取顶层 `status`、`title`、`priority` 等主文档事实。该解析器不应解释缩进字段，也不应把嵌套对象中的同名字段提升为顶层事实。

本次修复采用最小边界调整：

- 跳过以空格或 Tab 开头的 Frontmatter 行。
- 保留顶层 `key: value` 的既有行为。
- 结构化嵌套字段仍由 `parse_frontmatter_yaml()` 或 `parse_yaml_block()` 负责，避免主状态读取与观测声明读取混用。

### 兼容性

- 顶层 `status`、`title`、`priority`、`severity`、`updated_at` 等字段读取保持不变。
- 嵌套 `product_data_collection_observability.status`、`lifecycle.status` 或其他缩进同名字段不再影响轻量解析结果。
- 不改变 Workflow Sync 的状态机、Sprint 解析、Issue 子文档同步或 OpenSpec 归档逻辑。

### 验证策略

- 使用单元测试模拟 Frontmatter 中同时存在顶层主状态和嵌套观测声明状态，确认二者不会混淆。
- 使用 `load_issue_record()` 验证真实 Issue trace 读取时主状态保持 `in_sprint`。
- 运行 Workflow Sync dry-run 与项目治理校验，确认 Sprint scope 和 OpenSpec 工件有效。
