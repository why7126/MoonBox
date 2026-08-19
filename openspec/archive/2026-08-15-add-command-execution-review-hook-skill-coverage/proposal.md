## 背景

`Command Execution Review Hook` 已有中央契约，但只有 `.agents/skills/workflow-sync/SKILL.md` 直接包含该契约。其他命令 Skill 依赖外部规则记忆，新增或维护命令时容易漏掉最终「执行链路复盘」输出。

## 变更内容

- 为所有 `.agents/skills/*/SKILL.md` 命令补充轻量短引用，指向 `.agents/skills/workflow-sync/SKILL.md` 中央契约。
- 扩展 `scripts/validate-agent-context-budget.py`，校验命令 Skill 是否包含 Hook 短引用。
- 将 `openspec-*` 与 `usage-docs-*` 纳入命令技能识别口径，避免覆盖率统计遗漏。
- 更新 `rules/agent-context-budget.md`，明确每个命令 Skill 必须保留短引用。
- 不修改业务 `src/`、API、DB、Web UI 或部署拓扑。

## 影响范围

- `.agents/skills/*/SKILL.md`：新增短引用，`workflow-sync` 保留中央契约。
- `scripts/validate-agent-context-budget.py`：新增覆盖率校验。
- `rules/agent-context-budget.md`：同步命令 Skill 短引用要求。
- `openspec/changes/add-command-execution-review-hook-skill-coverage/`：记录本次治理 Change。
- `docs/spec-logs/`：写入治理迭代日志和索引。

## 回滚计划

如短引用位置影响命令说明阅读：

1. 保留中央契约和校验逻辑。
2. 调整短引用插入位置或标题层级。
3. 重新运行上下文预算校验、OpenSpec 语言校验和目标 Change 校验。
