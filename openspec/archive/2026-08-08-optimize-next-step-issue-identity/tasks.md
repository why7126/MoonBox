---
purpose: OpenSpec Change Tasks
content: 下一步可执行命令 Issue 身份参数优化任务
created_at: 2026-08-08 19:34:30
updated_at: 2026-08-08 19:34:30
owner: MoonBox 产品团队
---

# Tasks

- [x] 创建 active OpenSpec Change，并纳入 Sprint scope。
- [x] 更新命令顺序文档、AGENTS 入口和 REQ/BUG 规则，明确完整 Issue ID。
- [x] 更新 REQ、BUG、opsx、spec-opt 关键 Skill 的下一步参数模板。
- [x] 更新 `validate-agent-context-budget.py`，增加完整 Issue ID 校验。
- [x] 写入 `/spec-opt` 治理迭代日志。
- [x] 运行治理校验、OpenSpec 校验、Workflow Sync 和 AI Usage。

## 验证摘要

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-next-step-issue-identity`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item optimize-next-step-issue-identity`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-next-step-issue-identity --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-next-step-issue-identity --sprint sprint-001 --json`：通过，`usage_mode: actual`，warning 0。
