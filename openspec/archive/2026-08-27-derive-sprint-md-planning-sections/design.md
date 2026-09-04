---
change_id: derive-sprint-md-planning-sections
status: proposed
created_at: 2026-08-27 01:16:16
updated_at: 2026-08-27 01:16:16
---

# 设计：sprint.md 规划章节派生

## 事实源

- `sprint.yaml` 继续作为 Sprint 范围、容量、估算、起止时间和 scope estimates 的机器事实源。
- active / archived Change 的 tasks、状态和归档时间继续由 Workflow Sync 收集。
- `sprint.md` 作为人读规划面板，由 Workflow Sync 派生结构化章节。

## 派生章节

Workflow Sync 刷新 `sprint.md` 时维护以下顶层章节：

- `## 3. 工作量与容量`：展示容量、估算、人天占用率、fix 缓冲和容量门禁结论。
- `## 4. 里程碑`：基于 Sprint 起止时间、正式范围和 Change 状态生成启动、范围完成、归档收口等节点。
- `## 5. 风险与缓冲`：基于容量占用、fix 缓冲、未归档 / 未完成 Change 状态生成风险表。
- `## 6. 知识库承接`：声明 Sprint 复盘、best-practice、incident 等知识库承接入口和触发条件。

每个章节使用 `workflow-sync:sprint-*-section` marker 包裹派生内容。人工补充内容应放在 marker 之外，避免同步覆盖。

## 校验策略

`validate-sprint-scope.py` 在既有目标区和 Scope 校验基础上，继续检查四个规划章节和 marker 是否存在，确保 Sprint 人读文档不会退化为半派生状态。

## 兼容策略

- 若历史 `sprint.md` 缺少这些章节，Workflow Sync 自动插入。
- 若存在旧的手写 `## 风险与缓冲`，Workflow Sync 用派生章节替换。
- 章节编号以当前 MoonBox Sprint 面板顺序为准，不改 `sprint.yaml` 结构。
