## 1. OpenSpec 与 Sprint

- [x] 1.1 创建 active OpenSpec Change `add-command-execution-review-hook-skill-coverage`。
- [x] 1.2 将 Change 纳入 `sprint-003` scope。
- [x] 1.3 补齐 proposal、design、delta spec、trace 和 acceptance。

## 2. Skill 覆盖

- [x] 2.1 为所有 `.agents/skills/*/SKILL.md` 命令补充 Command Execution Review Hook 短引用。
- [x] 2.2 保留 `.agents/skills/workflow-sync/SKILL.md` 作为中央契约来源。

## 3. 规则与脚本

- [x] 3.1 更新 `rules/agent-context-budget.md`，明确命令 Skill 短引用要求。
- [x] 3.2 扩展 `scripts/validate-agent-context-budget.py`，校验短引用覆盖率。
- [x] 3.3 运行上下文预算校验并修复问题。

## 4. 治理日志与验证

- [x] 4.1 写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-command-review-hook-skill-coverage.md`。
- [x] 4.2 更新 `docs/spec-logs/CHANGELOG.md`。
- [x] 4.3 运行 OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage。
