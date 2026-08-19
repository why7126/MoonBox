---
change_id: add-overlay-exit-lightweight-selection-rule
status: applied
created_at: 2026-08-15 15:24:58
updated_at: 2026-08-15 15:24:58
---

# Test Plan: 浮层退出路径与轻量选择确认规则

## 校验命令

```bash
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py
python scripts/validate-directory-structure.py
openspec validate add-overlay-exit-lightweight-selection-rule
python scripts/validate-sprint-scope.py sprint-003 --item add-overlay-exit-lightweight-selection-rule
python scripts/sync-workflow-status.py --event opsx.apply --change add-overlay-exit-lightweight-selection-rule --sprint auto
```

## 业务测试

本次仅修改治理 Markdown、OpenSpec 文档和 Sprint scope，不触碰 `src/` 业务实现；业务单元测试、前端测试、API/DB/部署回归不适用。
