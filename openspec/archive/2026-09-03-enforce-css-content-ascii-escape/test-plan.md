---
purpose: OpenSpec Change 测试计划
content: CSS content 非 ASCII escape 写法治理验证计划
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# 测试计划

## 自动化验证

- `uv run pytest tests/unit/test_validate_design_system.py`
- `python scripts/validate-design-system.py`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate enforce-css-content-ascii-escape`
- `python scripts/validate-sprint-scope.py sprint-004 --item enforce-css-content-ascii-escape`

## 手工复核

- 聚焦 diff 确认没有修改 `src/` 业务运行时代码。
- 复核治理日志和 spec-logs 索引不包含隐私、密钥、未脱敏日志或本机绝对路径。
