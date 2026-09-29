# Acceptance

## 验收标准

- `/req-opsx` 技能明确生成 `execution.schema_version: 1` 的 Change trace frontmatter 模板。
- 模板明确 `started_at`、`completed_at` 初始为 `null`，`last_event` 初始为 `req.opsx`。
- 上下文预算校验脚本能检查 `/req-opsx` 技能中的 schema v1 关键片段。
- Workflow Sync 能把 schema v1 初始模板中的 `started_at: null` 替换为真实 `opsx.start` 时间，并在 `opsx.apply` 写入 `completed_at`。
- 本 Change 纳入 `sprint-006` 并通过 OpenSpec、语言、目录结构、Sprint scope 与 Workflow Sync 校验。

## 非目标

- 不修改业务 `src/` 代码。
- 不批量重写历史 Change trace。
- 不改变 `opsx.start`、`opsx.apply` 的执行事实写入语义。
