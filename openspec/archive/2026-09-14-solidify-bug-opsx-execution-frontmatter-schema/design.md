## 设计目标

将 `/bug-opsx` 的 Change trace execution 模板与 `/req-opsx` 对齐，保证 REQ 与 BUG 两条 Issue → OpenSpec 链路都在创建 Change 时具备 schema v1 执行事实占位。

## 契约

新建 `openspec/changes/<change-id>/trace.md` 时，frontmatter 至少包含：

```yaml
execution:
  schema_version: 1
  started_at: null
  completed_at: null
  last_event: bug.opsx
```

- `schema_version` 使用数字 `1`。
- `started_at` 和 `completed_at` 在 `/bug-opsx` 阶段保持 `null`，避免把 Change 创建时间误当实施启动或完成时间。
- `last_event` 初始为 `bug.opsx`，表示 Change 来源于 BUG 转 OpenSpec。
- 若目标 Change 已存在 `execution` 块，只补齐缺失字段，不覆盖已有真实执行事实。

## 校验策略

`scripts/validate-agent-context-budget.py` 将 `/bug-opsx` 技能的 required 片段扩展为包含 `execution:`、`schema_version: 1` 和 `last_event: bug.opsx`。该校验可阻止后续命令模板改动时删除 execution schema v1。

Workflow Sync 已在 `solidify-req-opsx-execution-frontmatter-schema` 中支持把 `None` 或空值按缺失字段处理，因此 `/bug-opsx` 模板中的 `started_at: null` 会在 `opsx.start` 时替换为真实启动时间，`completed_at: null` 会保留到 `opsx.apply` 完成时再写入真实完成时间。

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改治理 Skill、规则、校验脚本和 OpenSpec 文档，不触达 API、DB、请求日志、行为事件、Task Trace、Web/管理端请求封装或对象存储。
validation: 通过上下文预算校验、OpenSpec 中文校验、目录结构校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
```
