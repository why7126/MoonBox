---
change_id: apply-deepseek-harness-release-test-governance
status: proposed
created_at: 2026-08-27 08:06:34
updated_at: 2026-08-27 08:06:34
---

# 测试计划

## 必跑校验

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate apply-deepseek-harness-release-test-governance`
- `python scripts/validate-sprint-scope.py sprint-003`
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-deepseek-harness-release-test-governance --sprint auto`

## 不适用说明

本变更不修改 API、数据库、Web、管理端、对象存储、Docker Compose 或客户端生成物，业务测试不适用。
