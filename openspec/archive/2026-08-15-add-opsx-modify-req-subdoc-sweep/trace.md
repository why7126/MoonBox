---
purpose: OpenSpec Change Trace
content: opsx-modify REQ 子文档一致性扫尾检查追踪
created_at: 2026-08-15 13:02:00
updated_at: 2026-08-15 13:08:30
owner: MoonBox 产品团队
change_id: add-opsx-modify-req-subdoc-sweep
status: proposed
---

# Trace

## 来源

- 命令：`/spec-opt`
- 目标：`/opsx-modify` 完成前增加 “REQ 子文档一致性扫尾检查”。

## 实施摘要

- 已在 `/opsx-modify` 文档更新阶段后、Validate 阶段前增加 REQ Subdocument Consistency Sweep。
- 已同步 `AGENTS.md` 与 `rules/agent-context-budget.md`，明确只读取当前 linked REQ 子文档片段并避免全量读取无关 REQ。
- 已将纯治理 Change 纳入 `sprint-003`。

## 验证摘要

- `python scripts/validate-agent-context-budget.py` 通过。
- `python scripts/validate-openspec-language.py` 通过。
- `openspec validate add-opsx-modify-req-subdoc-sweep --strict` 通过。
- `git diff --check` 聚焦 touched docs 通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item add-opsx-modify-req-subdoc-sweep` 通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-opsx-modify-req-subdoc-sweep --sprint auto` 通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-opsx-modify-req-subdoc-sweep --sprint sprint-003 --json` 通过。
- `python scripts/validate-directory-structure.py` 未通过：根目录存在未登记 `tmp/`，为本次变更前已有未跟踪目录，未在本次删除。
