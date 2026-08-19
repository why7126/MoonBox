---
purpose: OpenSpec Change 测试计划
content: 浮层外部点击 capture 阶段 stopPropagation 覆盖规则验证计划
created_at: 2026-08-15 16:41:16
updated_at: 2026-08-15 16:41:16
owner: MoonBox 产品团队
---

# 测试计划

## 文档校验

- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py`
- `python scripts/validate-directory-structure.py`
- `openspec validate add-overlay-click-capture-stop-propagation-rule`
- `python scripts/validate-sprint-scope.py sprint-003 --item add-overlay-click-capture-stop-propagation-rule`

## 业务测试

本次仅修改治理规则、OpenSpec 文档、Sprint scope 和治理日志，不修改业务 `src/`，业务单元测试与 E2E 不适用。
