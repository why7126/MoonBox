---
change_id: derive-sprint-md-planning-sections
status: proposed
created_at: 2026-08-27 01:16:16
updated_at: 2026-08-27 01:16:16
---

# Test Plan

## 脚本验证

- `python -m py_compile scripts/workflow_sync/patch.py scripts/validate-sprint-scope.py`
- `python scripts/sync-workflow-status.py --event opsx.apply --change derive-sprint-md-planning-sections --sprint auto`
- `python scripts/validate-sprint-scope.py sprint-003 --item derive-sprint-md-planning-sections`
- `python scripts/validate-sprint-scope.py sprint-003`

## 治理校验

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate derive-sprint-md-planning-sections`
- `git diff --name-only -- src`

## AI Usage

- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change derive-sprint-md-planning-sections --sprint sprint-003 --json`
