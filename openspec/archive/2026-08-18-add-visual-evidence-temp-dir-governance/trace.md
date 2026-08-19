---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:09:48
---

# Trace

## 来源

- 命令：`/spec-opt 明确视觉证据临时目录归属或 ignore 策略`
- 类型：纯治理 Change，无 REQ/BUG 来源。
- Sprint：`sprint-003`

## 决策

- `tmp/visual-evidence/` 定义为本地临时视觉证据采集目录。
- `tmp/**` 加入 `.gitignore`，根目录 `tmp/` 不作为正式顶层目录登记。
- 长期验收证据转存到对应 Change `evidence/` 目录或写入脱敏摘要。
- OpenSpec delta 使用 `ADDED Requirements`，因为正式 `harness-runtime` 尚无同名 Requirement。

## 验证记录

| 时间 | 命令 | 结果 |
|---|---|---|
| 2026-08-18 10:09:48 | `python scripts/add-sprint-scope-item.py --sprint sprint-003 --change add-visual-evidence-temp-dir-governance ...` | 通过，Change 已纳入 `sprint-003`。 |
| 2026-08-18 10:09:48 | `python scripts/sync-workflow-status.py --event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint auto` | 通过，Updated 2，Errors 0。 |
| 2026-08-18 10:09:48 | `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint sprint-003 --json` | 通过，`usage_mode: actual`，`warning_count: 0`。 |
| 2026-08-18 10:09:48 | `python scripts/validate-agent-context-budget.py` | 通过。 |
| 2026-08-18 10:09:48 | `python scripts/validate-openspec-language.py` | 通过。 |
| 2026-08-18 10:09:48 | `python scripts/validate-directory-structure.py` | 通过。 |
| 2026-08-18 10:09:48 | `python scripts/validate-env-ignore-policy.py` | 通过。 |
| 2026-08-18 10:09:48 | `openspec validate add-visual-evidence-temp-dir-governance` | 通过。 |
| 2026-08-18 10:09:48 | `python scripts/validate-sprint-scope.py sprint-003 --item add-visual-evidence-temp-dir-governance` | 通过。 |
