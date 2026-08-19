---
change_id: add-visual-evidence-temp-dir-governance
status: proposed
created_at: 2026-08-18 10:06:40
updated_at: 2026-08-18 10:06:40
---

# 测试计划

## 治理校验

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `python scripts/validate-env-ignore-policy.py`
- `openspec validate add-visual-evidence-temp-dir-governance`

## Sprint 与同步校验

- `python scripts/validate-sprint-scope.py sprint-003 --item add-visual-evidence-temp-dir-governance`
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint auto`
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-visual-evidence-temp-dir-governance --sprint sprint-003 --json`

## 业务测试

本次只修改治理规则、ignore 策略和校验脚本，不触碰业务 `src/`、API、数据库或 Web 运行时代码，业务测试不适用。
