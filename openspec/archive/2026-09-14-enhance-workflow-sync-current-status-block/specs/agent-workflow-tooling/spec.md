## ADDED Requirements

### Requirement: Workflow Sync 同步当前状态代码块

Workflow Sync MUST 在同步 Issue `trace.md` 时维护正文 `## 当前状态` 章节内的 fenced `yaml` 当前态快照，使其 `openspec_changes` 与 `next` 字段和派生事实源一致。

#### Scenario: 同步当前状态代码块的 Change 状态和下一步

- **GIVEN** Issue `trace.md` 的 `## 当前状态` 章节包含 fenced `yaml` 代码块
- **AND** 该代码块包含 `openspec_changes` 或 `next`
- **WHEN** Workflow Sync 根据目标 Issue、Change 状态和 Sprint scope 刷新该 trace
- **THEN** 系统 MUST 同步该代码块中的 `openspec_changes[].status`
- **AND** 系统 MUST 同步该代码块中的 `next`
- **AND** `next` MUST 继续遵守 REQ/BUG 链路身份参数规则

#### Scenario: 当前状态代码块同步范围受限

- **GIVEN** Issue `trace.md` 同时包含 Readiness、验收结果、历史示例或其他 fenced `yaml` 代码块
- **WHEN** Workflow Sync 刷新正文当前态快照
- **THEN** 系统 MUST 只处理 `## 当前状态` 章节内首个 fenced `yaml` 代码块
- **AND** 系统 MUST NOT 改写其他章节的 fenced `yaml` 示例或验收语义块

#### Scenario: 兼容旧式 scalar openspec_changes

- **GIVEN** `## 当前状态` fenced `yaml` 中的 `openspec_changes` 使用旧式 scalar 条目
- **WHEN** Workflow Sync 同步对应 Change 状态
- **THEN** 系统 MUST 将目标条目升级为包含 `change_id` 与 `status` 的结构化条目
- **AND** 系统 MUST 保留后续 Workflow Sync 可继续更新的结构
