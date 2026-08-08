---
purpose: OpenSpec Change Tasks
content: 命令执行顺序治理任务
created_at: 2026-08-07 23:20:00
updated_at: 2026-08-07 23:20:00
owner: MoonBox 产品团队
---

# Tasks

- [x] 新增命令执行顺序速查文档，并更新 docs 索引。
- [x] 更新关键 Skill 的 Command Order，覆盖 A/B/C/D 候选项。
- [x] 更新规则和 OpenSpec delta spec，固化下一步参数与串行执行边界。
- [x] 更新同一份 ProjectTilesFST study 报告，记录本次 A/B/C/D 应用结果。
- [x] 运行治理校验、OpenSpec 校验、Workflow Sync、AI Usage 和学习对象只读复核。

## 验证摘要

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate apply-projecttilesfst-command-order`：通过。
- `python scripts/validate-sprint-scope.py sprint-001 --item apply-projecttilesfst-command-order`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change apply-projecttilesfst-command-order --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change apply-projecttilesfst-command-order --sprint sprint-001 --json`：通过，`usage_mode: actual`，warning 0。
- `git status --short`（学习对象只读复核）：学习对象存在自身未提交改动；本次未修改学习对象文件。
