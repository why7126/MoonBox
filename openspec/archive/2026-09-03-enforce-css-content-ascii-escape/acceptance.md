---
purpose: OpenSpec Change 验收
content: CSS content 非 ASCII escape 写法治理验收记录
created_at: 2026-09-03 09:34:14
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# 验收记录

## 验收标准

- `rules/ui-design.md` 明确 CSS `content` 中非 ASCII 符号使用 escape 写法。
- `scripts/validate-design-system.py` 能识别 `.css` 中 `content: "·"`、`content: '✓'` 这类原始非 ASCII 写法并报错。
- 校验脚本允许 `content: "\00B7"`、`content: "\2713"`、ASCII 字符和空字符串。
- 校验逻辑不误判 `justify-content`、`align-content`。
- 目标 Change、上下文预算、OpenSpec 语言、目录结构和 Sprint scope 校验通过，或对既有无关失败说明原因。

## 验收结果

- 状态：passed
- `uv run pytest tests/unit/test_validate_design_system.py`：3 passed。
- `python scripts/validate-design-system.py`：通过。
- `python -m py_compile scripts/validate-design-system.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-css-content-ascii-escape`：通过。
- `python scripts/validate-sprint-scope.py sprint-004 --item enforce-css-content-ascii-escape`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-css-content-ascii-escape --sprint auto`：通过，无需派生文档更新。
- AI Usage hook：warning，当前会话无可持久化 command-run token 事件，Sprint 快照跳过。
