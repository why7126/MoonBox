---
change_id: apply-tilesfst-governance-learnings
status: proposed
created_at: 2026-08-27 00:03:08
updated_at: 2026-08-27 00:03:08
---

# 测试计划

## 必跑校验

```bash
python -m py_compile scripts/validate-sprint-selection.py scripts/validate-release-upgrade.py scripts/validate-agent-context-budget.py scripts/ai_usage.py scripts/generate-sprint-fact-sheet.py
python scripts/validate-sprint-selection.py
python scripts/validate-release-upgrade.py --help
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py
python scripts/validate-directory-structure.py
openspec validate apply-tilesfst-governance-learnings
python scripts/validate-sprint-scope.py sprint-003 --item apply-tilesfst-governance-learnings
python scripts/sync-workflow-status.py --event opsx.apply --change apply-tilesfst-governance-learnings --sprint auto
```

## 影响面说明

- API：不适用，本次不修改接口契约。
- 数据库：不适用，本次不修改 schema 或 migration。
- Web / 管理端：不适用，本次不修改运行时 UI。
- Orval：不需要。
- Docker Compose：不修改 Compose 文件；升级计划治理仅新增规则和脚本。
