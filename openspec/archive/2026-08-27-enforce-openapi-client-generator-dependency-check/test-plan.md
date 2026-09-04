---
change_id: enforce-openapi-client-generator-dependency-check
created_at: 2026-08-27 08:06:17
updated_at: 2026-08-27 08:06:17
---

# 测试计划

- 运行 `bash -n scripts/generate-openapi-client.sh` 验证脚本语法。
- 运行 `python scripts/validate-api-standard.py` 验证 API 治理校验包含客户端生成脚本检查。
- 运行 `python scripts/validate-agent-context-budget.py`、`python scripts/validate-openspec-language.py`、`python scripts/validate-directory-structure.py` 和 `openspec validate enforce-openapi-client-generator-dependency-check`。
