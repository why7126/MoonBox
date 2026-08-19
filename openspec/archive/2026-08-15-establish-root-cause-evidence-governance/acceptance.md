---
change_id: establish-root-cause-evidence-governance
status: validated
created_at: 2026-08-14 17:00:00
updated_at: 2026-08-14 22:36:52
---

# Acceptance

## 验收项

| AC | 验收描述 | 状态 |
|---|---|---|
| AC-RCE-001 | 新增根因状态、证据链、人工补证和安全脱敏规则 | done |
| AC-RCE-002 | `/explore`、`/bug-explore`、`/bug-complete`、`/opsx-apply`、`/opsx-modify` 接入 root-cause evidence gate | done |
| AC-RCE-003 | 测试、日志、安全和 UI 验收规范要求回扣根因证据 | done |
| AC-RCE-004 | `scripts/validate-root-cause-evidence.py` 支持 `--bug`、`--change`、`--all-active` | done |
| AC-RCE-005 | 治理校验通过并记录结果 | done |

## 验证记录

| 命令 | 结果 | 摘要 |
|---|---|---|
| `python scripts/validate-root-cause-evidence.py --change establish-root-cause-evidence-governance --json` | pass | 纯治理 Change 无 BUG 来源，root-cause evidence gate 为 `na`。 |
| `python scripts/validate-root-cause-evidence.py --all-active --json` | warning | 新门禁发现现存 `BUG-0011-admin-user-list-enum-time-display-unclear` 的 `root-cause.md` 缺少根因状态；未擅自补证。 |
| `python scripts/validate-agent-context-budget.py` | pass | 技能契约与上下文预算通过。 |
| `python scripts/validate-openspec-language.py` | pass | OpenSpec 中文优先校验通过。 |
| `python scripts/validate-directory-structure.py` | pass | 补齐 `src/sdk`、`src/infrastructure` 空目录占位后通过。 |
| `python scripts/validate-sprint-scope.py sprint-003 --item establish-root-cause-evidence-governance` | pass | Sprint scope 包含本 Change。 |
| `openspec validate establish-root-cause-evidence-governance` | pass | Change 结构校验通过。 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change establish-root-cause-evidence-governance --sprint auto` | pass | Workflow Sync 更新 2 项，无错误。 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change establish-root-cause-evidence-governance --sprint sprint-003 --json` | pass | `usage_mode: actual`，`warning_count: 0`，刷新 `data/ai-usage/sprints/sprint-003.json`。 |
