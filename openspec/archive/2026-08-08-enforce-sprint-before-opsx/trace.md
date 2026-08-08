---
purpose: OpenSpec Change Trace
content: 评审后先 Sprint 再 opsx 顺序优化追溯
created_at: 2026-08-08 20:38:15
updated_at: 2026-08-08 20:38:15
owner: MoonBox 产品团队
---

# Trace

status: applied
source: `/spec-opt 需求或BUG评审完后，先进行sprint-propose，再进行bug-opsx或req-opsx`
sprint: sprint-001
requirements: []
bugs: []

## 优化规则

- REQ review approved 后：`/sprint-propose --req <REQ-full-id>` → `/req-opsx <REQ-full-id>`。
- BUG review approved 后：`/sprint-propose --bug <BUG-full-id>` → `/bug-opsx <BUG-full-id>`。
- `/req-opsx` / `/bug-opsx` 遇到 `approved` 但未 `in_sprint` 时必须停止。

## 应用验证

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-sprint-before-opsx`：通过。
- Workflow Sync：`opsx.apply` 通过，Sprint `sprint-001`。
- Sprint scope：通过。
- AI Usage：`usage_mode: actual`，warning 0。
