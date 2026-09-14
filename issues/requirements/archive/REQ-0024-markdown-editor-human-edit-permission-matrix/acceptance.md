---
requirement_id: REQ-0024-markdown-editor-human-edit-permission-matrix
acceptance_status: passed
created_at: 2026-09-03 22:02:09
updated_at: 2026-09-14 00:06:38
owner: product
source: requirement.md
---

# 验收标准

## 功能 AC

- [ ] AC-001 文档列表接口返回每个文档的能力对象，至少包含 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only`、`reason`。
- [ ] AC-002 `editable` 若保留兼容，必须等价于 `human_editable`，新逻辑和新增测试以能力对象为准。
- [ ] AC-003 采集池阶段只有 `capture.md` 的 `human_editable=true`，`trace.md` 始终 `human_editable=false`。
- [ ] AC-004 规划中阶段 Requirement 只允许 `requirement.md` 人工编辑，Bug 只允许 `bug.md` 人工编辑。
- [ ] AC-005 待评审阶段 Requirement 允许 `user-stories.md`、`business-flow.md`、`acceptance.md`、`requirement.md` 人工编辑；Bug 允许 `root-cause.md`、`workaround.md`、`acceptance.md`、`bug.md` 人工编辑。
- [ ] AC-006 已评审阶段在待评审可编辑文档基础上允许 `review.md` 人工编辑。
- [ ] AC-007 迭代规划、研发中和已完成阶段所有 Markdown 文档均不允许人工全文编辑。
- [ ] AC-008 待开发阶段只允许当前 OpenSpec Change 范围内的 `proposal.md`、`spec.md`、`design.md`、`tasks.md` 人工全文编辑。
- [ ] AC-009 已生效 `openspec/specs/**/spec.md` 始终不允许人工全文编辑。
- [ ] AC-010 验收中 `tasks.md` 返回 `task_toggle_only=true`，且 `human_editable=false`。
- [ ] AC-011 验收中 `tasks.md` 仅允许切换 `- [ ]` 与 `- [x]`，后端必须拒绝标题、任务描述、非任务行或验收记录的文本变化。
- [ ] AC-012 `trace.md` 可返回 `ai_mutable=true`，但人工保存接口提交 `trace.md` 全文时必须返回 403 或等价受限错误。
- [ ] AC-013 AI/Workflow/脚本通过既有治理命令更新 `trace.md`、`tasks.md` 或其他治理文档时，不受前端只读状态阻断。
- [ ] AC-014 前端 `human_editable=true` 时显示完整编辑、分栏、保存和脏状态保护。
- [ ] AC-015 前端 `task_toggle_only=true` 时只显示 checkbox-only 操作，不显示源码编辑器、Vditor 工具栏或全文保存入口。
- [ ] AC-016 前端只读文档展示阅读态和受限原因，关闭只读文档不得触发未保存确认。
- [ ] AC-017 完整 Markdown 保存接口复用后端能力计算，不能只信任前端传入的可编辑状态。
- [ ] AC-018 只读、越权保存、非法路径、全文修改验收中 `tasks.md`、编辑已生效规格等失败场景返回稳定脱敏错误，不暴露本机绝对路径、系统用户名、密钥、`.env`、内部堆栈或完整治理目录。
- [ ] AC-019 后端测试覆盖 REQ 与 BUG 在采集池、规划中、待评审、已评审、迭代规划、待开发、研发中、验收中、已完成阶段的能力矩阵。
- [ ] AC-020 前端测试覆盖完整编辑态、只读态、checkbox-only 态、脏状态确认和保存失败保留草稿。

## 产品数据采集与链路观测 AC

- [ ] AC-OBS-001 人工完整保存、task checkbox-only 保存、越权拒绝和只读打开至少在请求日志中记录脱敏摘要。
- [ ] AC-OBS-002 前端行为事件使用稳定事件名，属性只包含对象 ID、文档名、能力类型、结果和脱敏错误码，不保存完整文档内容。
- [ ] AC-OBS-003 高风险或多步骤的 task toggle 差异校验应接入 Task Trace，或在 Change 设计中写明不接入的具体原因。
- [ ] AC-OBS-004 后端 metadata 不保存完整请求体、完整响应体、完整 Markdown 内容、完整 Prompt、Authorization、Cookie、本机路径或对象存储私有地址。
- [ ] AC-OBS-005 验收需覆盖前端请求封装、后端可信 `request_id`、越权错误码和观测写入失败不阻塞主流程。

## 横切 AC（knowledge-base）

本需求未命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 标签，无 admin 类横切 AC。后续若实现阶段引入上传、管理端弹窗或后台表单，应重新读取对应 best-practices 并补充 AC-XCUT。

## Readiness Gate

- [ ] requirement、user-stories、business-flow、acceptance 和 trace 齐全。
- [ ] `trace.md` 包含 `knowledge_base_refs`、`cross_cutting_tags` 和 `product_data_collection_observability`。
- [ ] 本需求无 prototype 目录，当前不要求 AC-PROTOTYPE。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-14 00:06:38
accepted_by: workflow-sync
source_change: update-markdown-editor-human-edit-permission-matrix
source_sprint: sprint-004
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

