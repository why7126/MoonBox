---
change_id: optimize-workflow-sync-issue-output-next
created_at: 2026-08-27 08:02:44
updated_at: 2026-08-27 08:02:44
---

# 测试计划

## 聚焦验证

- 运行 `pytest tests/unit/test_workflow_sync_engine.py tests/unit/test_workflow_sync_patch.py`。
- 运行 `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-workflow-sync-issue-output-next --sprint auto --dry-run --output summary`。

## 治理校验

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate optimize-workflow-sync-issue-output-next`
