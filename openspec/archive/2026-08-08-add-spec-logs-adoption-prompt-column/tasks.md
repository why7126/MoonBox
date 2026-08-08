---
purpose: OpenSpec Change Tasks
content: spec-logs 跨项目落地提示词列任务
created_at: 2026-08-08 21:01:51
updated_at: 2026-08-08 21:05:10
owner: MoonBox 产品团队
---

# Tasks

- [x] 创建 active OpenSpec Change，并纳入 Sprint scope。
- [x] 更新 `docs/spec-logs/CHANGELOG.md`，新增跨项目落地提示词记录规则和表格列。
- [x] 为既有变更历史条目补充可复制 Prompt。
- [x] 写入 `/spec-opt` 治理迭代日志。
- [x] 运行治理校验、OpenSpec 校验、Workflow Sync 和 AI Usage。

## 验证摘要

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-spec-logs-adoption-prompt-column`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item add-spec-logs-adoption-prompt-column`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-spec-logs-adoption-prompt-column --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-spec-logs-adoption-prompt-column --sprint sprint-001 --json`：通过，`usage_mode: actual`，warning 0。
