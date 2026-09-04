---
requirement_id: REQ-0024-markdown-editor-human-edit-permission-matrix
created_at: 2026-09-03 22:02:09
updated_at: 2026-09-03 22:02:09
owner: product
source: requirement.md
---

# 用户故事

## US-001 阶段化人工编辑

作为产品负责人，我希望需求中心按治理阶段开放不同 Markdown 文档的人工编辑能力，以便我能在合适阶段补充材料，同时避免误改审计记录、迭代计划或已完成文档。

验收要点：

- 采集池只允许人工编辑 `capture.md`。
- 规划中只允许人工编辑 `requirement.md` 或 `bug.md`。
- 待评审允许人工编辑需求/缺陷完善类文档。
- 已评审允许人工编辑已评审材料和 `review.md`。
- 迭代规划、研发中、已完成阶段均不开放人工全文编辑。

## US-002 系统修改不受 UI 只读误伤

作为项目负责人，我希望 UI 只读只限制人工编辑，不阻断 AI、Workflow 和脚本按治理流程更新文档，以便状态同步、trace 记录和命令产物仍能正常生成。

验收要点：

- `trace.md` 在页面始终只读。
- Workflow Sync、AI 命令和治理脚本仍可按既有门禁更新 `trace.md`。
- `ai_mutable` 不等同于人工保存权限。
- 人工保存接口不得因为系统可修改而接受越权全文保存。

## US-003 验收中任务勾选

作为研发协作者，我希望验收中 `tasks.md` 只提供任务勾选和取消勾选能力，以便同步任务状态，同时不误改任务描述、标题或验收记录。

验收要点：

- 验收中 `tasks.md` 不显示完整 Vditor、源码编辑器或全文保存入口。
- 用户只能切换 Markdown task list 的 `- [ ]` 与 `- [x]`。
- 后端校验 diff 只包含 checkbox 状态变化。
- 任何非勾选状态文本变化必须被拒绝并给出脱敏原因。

## US-004 待开发 Change 文档编辑

作为开发负责人，我希望待开发阶段可以人工编辑 OpenSpec Change 的计划类文档，以便在正式 apply 前补充 proposal、design、spec 和 tasks。

验收要点：

- 待开发阶段可编辑 `proposal.md`、Change 下的 `spec.md`、`design.md`、`tasks.md`。
- 已生效 `openspec/specs/**/spec.md` 保持人工只读。
- 前端需清楚展示文档属于当前 Change，不让用户混淆草案规格和已生效规格。

## US-005 能力驱动前端体验

作为空间成员，我希望页面能明确展示文档是否可编辑、只读或仅可勾选，以便我理解当前限制并避免无效操作。

验收要点：

- 前端使用后端返回的能力对象决定展示，而不是硬编码 `capture.md`。
- `human_editable=true` 时显示完整编辑体验。
- `task_toggle_only=true` 时显示 checkbox-only 体验。
- 只读文档展示可理解原因。
