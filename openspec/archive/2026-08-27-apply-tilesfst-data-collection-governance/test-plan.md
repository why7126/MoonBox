---
change_id: apply-tilesfst-data-collection-governance
status: proposed
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
---

# Test Plan

## 自动校验

- `python -m py_compile scripts/validate-product-data-observability.py`
- `python scripts/validate-product-data-observability.py`
- `python scripts/validate-product-data-observability.py --change apply-tilesfst-data-collection-governance`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate apply-tilesfst-data-collection-governance`
- `python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-data-collection-governance`
- `git diff --name-only -- src`

## Workflow Sync

- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-data-collection-governance --sprint auto`
- AI Usage Post-command Hook 使用 Workflow Sync 解析到的 Sprint。

## 不适用测试

- 后端 API 测试：本变更不修改 API 或运行时代码。
- 数据库迁移测试：本变更不新增 schema、migration 或持久化表。
- 前端/管理端测试：本变更不修改 Web 或管理端实现。
