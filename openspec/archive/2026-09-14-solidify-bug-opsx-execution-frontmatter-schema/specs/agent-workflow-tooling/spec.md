## ADDED Requirements

### Requirement: Change 执行事实

MoonBox MUST 使用 Change trace frontmatter 的 `execution.schema_version=1` 保存 OpenSpec Change 执行事实。`execution` MUST 包含 `schema_version`、`started_at`、`completed_at` 和 `last_event` 字段。`/req-opsx` 与 `/bug-opsx` 创建 Change 时 MUST 写入 schema v1 初始块，后续 `opsx.start` 与 `opsx.apply` 由 Workflow Sync 维护实际启动、完成和最后事件。

#### Scenario: bug-opsx 创建 Change trace 时固化 execution schema v1

- **WHEN** 系统通过 `/bug-opsx <BUG-full-id>` 创建或补齐 `openspec/changes/<change-id>/trace.md`
- **THEN** trace frontmatter MUST 包含 `execution.schema_version: 1`
- **AND** `execution.started_at` MUST 初始为 `null`
- **AND** `execution.completed_at` MUST 初始为 `null`
- **AND** `execution.last_event` MUST 初始为 `bug.opsx`
- **AND** 系统 MUST NOT 在 `/bug-opsx` 创建阶段伪造实施启动或完成时间

#### Scenario: REQ 与 BUG opsx 模板使用来源事件

- **WHEN** 系统生成 REQ 或 BUG 来源的 OpenSpec Change trace
- **THEN** `/req-opsx` MUST 使用 `last_event: req.opsx`
- **AND** `/bug-opsx` MUST 使用 `last_event: bug.opsx`
- **AND** 两者 MUST 共享 `execution.schema_version: 1`、`started_at: null` 和 `completed_at: null` 初始字段
