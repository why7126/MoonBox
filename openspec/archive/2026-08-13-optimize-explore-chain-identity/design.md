## 设计目标

让探索命令的“下一步”输出与 REQ/BUG → Sprint → OpenSpec → opsx 的链路身份保持一致，避免从探索阶段开始把 Issue 来源 Change 降级为裸 Change ID。

## 链路身份解析

探索命令在输出 `/opsx-apply`、`/opsx-modify`、`/opsx-archive` 等下一步命令前，MUST 尝试识别当前 Change 的来源：

1. 优先读取当前上下文中明确出现的完整 `REQ-xxxx-slug` 或 `BUG-xxxx-slug`。
2. 若用户只给出 `openspec/changes/<change-id>` 或 `<change-id>`，读取该 Change 的 `trace.md`、`proposal.md`、`design.md`、`tasks.md` 必要片段，查找关联 REQ/BUG。
3. 必要时读取当前 Sprint `sprint.yaml` 的 `scope_estimates` 中同一 `change` 的 `requirement` 或 `bug` 字段。
4. 若可识别 REQ 来源，下一步 `/opsx-*` 使用完整 `REQ-xxxx-slug`。
5. 若可识别 BUG 来源，下一步 `/opsx-*` 使用完整 `BUG-xxxx-slug`。
6. 只有确认无 REQ/BUG 来源的纯治理 Change，才使用 `<change-id>`。

## 输出示例

```text
下一步：/opsx-apply REQ-0012-frontend-requirement-center
```

```text
下一步：/opsx-modify BUG-0009-frontend-admin-sidebar-version-mismatch
```

```text
下一步：/opsx-apply optimize-explore-chain-identity
```

第三个示例仅适用于无 REQ/BUG 来源的纯治理 Change。

## 边界

- 本规范只影响 Agent 命令输出契约，不改变 OpenSpec CLI 参数解析本身。
- 如果无法识别来源，探索命令不得臆造 Issue ID；应在「待用户决策/处理」中说明需要补充来源，或给出基于 `<change-id>` 的纯治理路径前提。
- Workflow Sync 内部仍可使用 `<change-id>` 作为机器参数，但用户可执行的 REQ/BUG 来源 `/opsx-*` 下一步必须保留完整 Issue ID。

## 校验策略

`scripts/validate-agent-context-budget.py` 增加 `/explore` 与 `/opsx-explore` 的链路身份契约检查，确保两个探索 Skill 均包含完整 `REQ-xxxx-slug`、完整 `BUG-xxxx-slug`、纯治理 Change 使用 `<change-id>`、以及 `/opsx-*` 下一步参数不得降级的约束。
