---
change_id: apply-tilesfst-local-session-jsonl-governance
status: proposed
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
---

# 测试计划

## 验证范围

- AI Usage 本地 session 自动发现。
- 缺 session、缺 token、unsafe record 的 fallback 行为。
- 治理规则、技能输出契约和目录边界。
- OpenSpec Change 文档语言与 Sprint scope。

## 命令

```bash
python -m pytest tests/unit/test_ai_usage.py
python -m py_compile scripts/ai_usage.py tests/unit/test_ai_usage.py
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py
python scripts/validate-directory-structure.py
openspec validate apply-tilesfst-local-session-jsonl-governance
python scripts/validate-sprint-scope.py sprint-004 --item apply-tilesfst-local-session-jsonl-governance
```

## 通过标准

- 聚焦 AI Usage 单测全部通过。
- OpenSpec 与目录校验通过，或只因既有无关工作区状态失败并清晰说明。
- `git diff --name-only -- src` 为空。
