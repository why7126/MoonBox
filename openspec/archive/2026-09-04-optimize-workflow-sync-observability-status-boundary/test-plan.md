---
change_id: optimize-workflow-sync-observability-status-boundary
status: updated
created_at: 2026-09-04 08:03:36
updated_at: 2026-09-04 08:03:36
---

# 测试计划

## 自动化验证

- `uv run pytest tests/unit/test_workflow_sync_engine.py`：覆盖 Workflow Sync 聚焦单元测试。
- `python -m py_compile scripts/workflow_sync/collect.py`：验证脚本语法。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-workflow-sync-observability-status-boundary --sprint auto --dry-run`：确认 Change 位于 Sprint scope。
- `python scripts/validate-agent-context-budget.py`：验证 Agent 技能共享契约。
- `python scripts/validate-openspec-language.py`：验证 OpenSpec 中文优先。
- `python scripts/validate-directory-structure.py`：验证目录边界。
- `openspec validate optimize-workflow-sync-observability-status-boundary`：验证目标 Change。

## 不适用验证

- API/DB/Web/管理端/客户端生成/Docker Compose：本次不修改业务接口、数据结构、前端运行时代码、客户端生成物或部署配置。

