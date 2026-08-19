## 设计

### 中央契约

`.agents/skills/workflow-sync/SKILL.md` 继续作为 `Command Execution Review Hook` 的完整规则来源，避免每个命令 Skill 复制长规则。

### 命令短引用

每个命令 Skill 使用同一段短引用：

```text
命令结束前 MUST 遵守 `.agents/skills/workflow-sync/SKILL.md` 的 Command Execution Review Hook，输出「执行链路复盘」：链路状态、问题证据、规范优化建议，并说明默认未自动创建 Issue/Change。
```

该短引用覆盖四个必要要素：

- 中央契约路径。
- 执行链路复盘。
- 链路状态、问题证据、规范优化建议。
- 默认未自动创建 Issue/Change。

### 校验

`scripts/validate-agent-context-budget.py` 在命令 Skill 校验中新增短引用覆盖检查；同时将 `openspec-*` 和 `usage-docs-*` 纳入命令技能识别口径。

## 取舍

- 不复制完整 Hook：降低后续维护漂移。
- 不只依赖中央规则：每个命令入口都有就近提醒。
- 不自动创建 follow-up：保持用户授权边界。
