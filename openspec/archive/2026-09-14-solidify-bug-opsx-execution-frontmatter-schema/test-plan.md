# Test Plan

## 自动校验

- `python scripts/validate-agent-context-budget.py`
- `python -m py_compile scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py --change solidify-bug-opsx-execution-frontmatter-schema`
- `python scripts/validate-directory-structure.py`
- `openspec validate solidify-bug-opsx-execution-frontmatter-schema --strict`
- `python scripts/validate-sprint-scope.py sprint-006 --item solidify-bug-opsx-execution-frontmatter-schema`
- `python scripts/sync-workflow-status.py --event opsx.apply --change solidify-bug-opsx-execution-frontmatter-schema --sprint auto --dry-run`

## 手工复核

- 聚焦 diff 确认未修改 `src/` 业务代码。
- 复核 `/bug-opsx` 技能模板与规则文档中的 execution schema v1 表述一致。
