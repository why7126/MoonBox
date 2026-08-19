## 1. OpenSpec 与 Sprint

- [x] 1.1 创建 active OpenSpec Change `establish-command-execution-review-hook`。
- [x] 1.2 将 Change 纳入 `sprint-003` scope。
- [x] 1.3 补齐 proposal、design、delta spec、trace 和 acceptance。

## 2. 规则与文档

- [x] 2.1 更新 `rules/agent-context-budget.md`，新增 Command Execution Review Hook 输出契约。
- [x] 2.2 更新 `.agents/skills/workflow-sync/SKILL.md`，同步 workflow 命令完成后的复盘口径。
- [x] 2.3 更新 `AGENTS.md`、`docs/08-command-execution-order.md`、`docs/README.md`。

## 3. 校验脚本

- [x] 3.1 更新 `scripts/validate-agent-context-budget.py`，校验中央 Hook 契约。
- [x] 3.2 运行上下文预算校验并修复问题。

## 4. 治理日志与验证

- [x] 4.1 写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-command-execution-review-hook.md`。
- [x] 4.2 更新 `docs/spec-logs/CHANGELOG.md`。
- [x] 4.3 运行 OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage。
