---
purpose: OpenSpec Change Trace
content: 下一步可执行命令 Issue 身份参数优化追溯
created_at: 2026-08-08 19:34:30
updated_at: 2026-08-08 19:34:30
owner: MoonBox 产品团队
---

# Trace

status: applied
source: `/spec-opt 下一步可执行的操作优化`
sprint: sprint-001
requirements: []
bugs: []

## 优化规则

- REQ 链路：所有 `/req-*` 和后续 `/opsx-*` 使用完整 `REQ-xxxx-slug`。
- BUG 链路：所有 `/bug-*` 和后续 `/opsx-*` 使用完整 `BUG-xxxx-slug`。
- 非 REQ/BUG：纯治理 Change 的 `/opsx-*` 使用 `<change-id>`。

## 应用验证

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-next-step-issue-identity`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item optimize-next-step-issue-identity`：通过。
- Workflow Sync：`opsx.apply` 通过，Sprint `sprint-001`。
- AI Usage：`usage_mode: actual`，warning 0。
