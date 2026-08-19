---
change_id: fix-workflow-sync-bug-sprint-propose-drift
created_at: 2026-08-15 11:45:27
updated_at: 2026-08-15 12:00:52
---

# 测试计划

## Focused Commands

```bash
python scripts/validate-root-cause-evidence.py --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --dry-run --output detail
python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --check
python scripts/validate-directory-structure.py
python scripts/validate-openspec-language.py
```

## 回归关注

- BUG `sprint.propose` 不再遗漏 `issues/bugs/CHANGELOG.md`。
- REQ `sprint.propose` 与 `req.generate` 当前态看板刷新仍保持可用。
- `bug.opsx` 能把 Change 回填到 `sprint.yaml changes[]` 与目标 scope estimate。
