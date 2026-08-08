---
purpose: OpenSpec Change Tasks
content: 评审后先 Sprint 再 opsx 顺序优化任务
created_at: 2026-08-08 20:38:15
updated_at: 2026-08-08 20:38:15
owner: MoonBox 产品团队
---

# Tasks

- [x] 创建 active OpenSpec Change，并纳入 Sprint scope。
- [x] 更新 review、opsx、sprint-propose 关键 Skill 的命令顺序。
- [x] 更新 AGENTS、命令顺序文档、REQ/BUG 管理规则和上下文预算规则。
- [x] 更新上下文预算校验脚本，阻止旧顺序回退。
- [x] 写入 `/spec-opt` 治理迭代日志。
- [x] 运行治理校验、OpenSpec 校验、Workflow Sync、Sprint scope 校验和 AI Usage。

## 验证摘要

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate enforce-sprint-before-opsx`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enforce-sprint-before-opsx --sprint auto`：通过，错误 0。
- `python scripts/validate-sprint-scope.py sprint-001 --item enforce-sprint-before-opsx`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enforce-sprint-before-opsx --sprint sprint-001 --json`：通过，`usage_mode: actual`，warning 0。
