## MODIFIED Requirements

### Requirement: Change 执行事实

MoonBox MUST 使用 Change trace frontmatter 的 `execution.schema_version=1` 保存 OpenSpec Change 执行事实。`execution` MUST 包含 `schema_version`、`started_at`、`completed_at` 和 `last_event` 字段。`/req-opsx` 创建 Change 时 MUST 写入 schema v1 初始块，后续 `opsx.start` 与 `opsx.apply` 由 Workflow Sync 维护实际启动、完成和最后事件。

#### Scenario: req-opsx 创建 Change trace 时固化 execution schema v1

- **WHEN** 系统通过 `/req-opsx <REQ-full-id>` 创建或补齐 `openspec/changes/<change-id>/trace.md`
- **THEN** trace frontmatter MUST 包含 `execution.schema_version: 1`
- **AND** `execution.started_at` MUST 初始为 `null`
- **AND** `execution.completed_at` MUST 初始为 `null`
- **AND** `execution.last_event` MUST 初始为 `req.opsx`
- **AND** 系统 MUST NOT 在 `/req-opsx` 创建阶段伪造实施启动或完成时间

#### Scenario: Workflow Sync 维护执行事实

- **WHEN** 系统执行 `opsx.start` 或 `opsx.apply` Workflow Sync 事件
- **THEN** Workflow Sync MUST 复用 `execution.schema_version: 1`
- **AND** `opsx.start` MUST 写入真实 `started_at`
- **AND** `opsx.apply` MUST 写入真实 `completed_at`
- **AND** 旧 trace 缺少 `execution` 时 MAY 兼容补齐 schema v1，但不得批量重写历史终态
