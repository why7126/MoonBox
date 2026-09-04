---
req_id: REQ-0024-markdown-editor-human-edit-permission-matrix
status: captured
created_at: 2026-09-03 21:17:11
updated_at: 2026-09-03 21:17:11
recorded_by: product
source: explore
priority_hint: P1
parent_requirement: REQ-0021-markdown-editor-vditor-enhancement
---
# 一句话

Markdown 编辑器需要按治理阶段扩展人工编辑权限矩阵，并将用户手动编辑能力与 AI/Workflow 系统修订能力分层控制。

# 原始描述

用户确认扩展规则方向合理：人工编辑权限应按阶段收紧，AI/Workflow 修改权限应另走治理链路，不被 UI 只读限制绑死。

建议抽象为两层能力：

- Human Edit Capability：控制页面里 Vditor/Markdown 编辑器是否开放给用户手动编辑。
- System Mutation Capability：控制 AI、workflow、脚本、命令是否能按治理流程生成、追加、修订文档。

这样 `trace.md` 始终只读不会误伤 AI 追加 trace，也不会让用户手动改审计记录。

阶段人工编辑策略初步理解：

| 阶段 | 人工编辑策略 |
|---|---|
| 采集池 | 只允许 `capture.md` |
| 规划中 | 允许 `requirement.md`、`bug.md` |
| 待评审 | 允许需求/缺陷完善类文档 |
| 已评审 | 允许已评审材料和 `review.md`，但需进一步区分评审权限 |
| 迭代规划 | 全只读 |
| 待开发 | 允许 OpenSpec 计划类文档：`proposal.md`、`spec.md`、`design.md`、`tasks.md` |
| 研发中 | 全只读 |
| 验收中 | 仅 `tasks.md` 可勾选/取消，不开放全文编辑 |
| 已完成 | 全只读 |

重点边界：

- `tasks.md` 在验收中不是全文可编辑，而是任务勾选能力；UI 应渲染 task list checkbox，只允许切换 `- [ ]` / `- [x]`。
- `review.md` 已评审阶段可编辑有风险；普通用户建议只读，有评审权限用户可编辑或追加修订，AI/Workflow 可按 `/req-review`、`/bug-review` 更新。
- 待开发阶段的 `spec.md` 要区分位置：OpenSpec Change 下的 `specs/**/spec.md` 可按阶段编辑，已生效 `openspec/specs/` 仍只读。

推荐落地方式：

- 后端统一返回每个文档的能力：`readable`、`human_editable`、`ai_mutable`、`task_toggle_only`、`reason`。
- 前端不再硬编码 `capture.md`，而是根据能力决定阅读态、编辑态、分栏/Vditor 或 checkbox-only 操作。
- 保存接口后端再次校验阶段、文档名、角色权限，前端只负责体验，不负责最终授权。

# 待澄清

- [ ] `review.md` 是否普通用户可编辑，还是仅有评审权限用户可编辑或追加修订。
- [ ] 验收中 `tasks.md` 是否只允许 checkbox 切换，不允许全文编辑。
- [ ] 后端能力字段是否需要同时覆盖 REQ、BUG、OpenSpec Change 和已生效 OpenSpec Specs。
- [ ] `ai_mutable` 是否仅表达能力展示，还是需要进入保存/命令接口的后端授权模型。

# 探索结论

该需求是 REQ-0021 Markdown 文档 Vditor 增强编辑器的权限矩阵 refinement，适合作为独立 REQ 推进：先沉淀阶段-文档-角色-能力矩阵，再在后续 PRD 与 OpenSpec 中落为后端能力计算、保存校验和前端渲染策略。
