---
change_id: apply-tilesfst-sprint-md-governance
status: proposed
created_at: 2026-08-27 01:02:45
updated_at: 2026-08-27 01:02:45
---

# Test Plan

## 自动校验

- `python -m py_compile scripts/workflow_sync/patch.py scripts/validate-sprint-scope.py scripts/generate-sprint-fact-sheet.py`
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-sprint-md-governance --sprint auto`
- `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-sprint-md-governance`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate apply-tilesfst-sprint-md-governance`
- `git diff --name-only -- src`

## 不适用测试

- 后端 API 测试：本变更不修改 API 或运行时代码。
- 数据库迁移测试：本变更不新增 schema、migration 或持久化表。
- 前端/管理端测试：本变更不修改 Web 或管理端实现。
