---
created_at: 2026-09-14 15:20:11
updated_at: 2026-09-14 15:47:29
---

# 测试计划

## 脚本级验证

- 运行 `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope`，覆盖聚焦成功路径。
- 运行 `python scripts/validate-openspec-language.py --change __missing__`，覆盖不存在 Change 的失败路径。
- 运行 `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope --residual-report`，覆盖残留分离报告路径。
- 运行 `python scripts/validate-openspec-language.py`，覆盖默认全量 active 行为。
- 运行 `bash scripts/validate-openspec.sh --change optimize-openspec-language-change-scope --residual-report`，覆盖 OpenSpec 校验总入口聚焦成功路径。
- 运行 `bash scripts/validate-openspec.sh --include-archive --change optimize-openspec-language-change-scope --residual-report`，覆盖 OpenSpec 校验总入口归档 Change 聚焦路径。
- 运行 `bash scripts/validate-openspec.sh --change __missing__`，覆盖 OpenSpec 校验总入口目标不存在失败路径。

## 治理门禁

- 运行 `python scripts/validate-agent-context-budget.py`。
- 运行 `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope`。
- 运行 `bash scripts/validate-openspec.sh --change optimize-openspec-language-change-scope --residual-report`。
- 运行 `python scripts/validate-directory-structure.py`。
- 运行 `openspec validate optimize-openspec-language-change-scope`。
- 运行 `python scripts/validate-sprint-scope.py sprint-006 --item optimize-openspec-language-change-scope`。

## 不适用测试

- 不运行后端、前端、数据库、OpenAPI、客户端生成、Docker Compose 或浏览器验收测试；本次仅变更治理脚本和治理文档。
