---
change_id: derive-sprint-md-planning-sections
status: proposed
created_at: 2026-08-27 01:16:16
updated_at: 2026-08-27 01:16:16
---

# 提案：派生 sprint.md 规划章节

## 背景

`sprint.md` 已通过 Workflow Sync 派生 Sprint 目标编号列表、逐项要点和 Scope 表，但容量、里程碑、风险与知识库承接仍主要依赖人工维护，容易与 `sprint.yaml`、Change 状态和归档节奏漂移。

## 目标

- 让 Workflow Sync 结构化派生 `sprint.md` 的工作量与容量、里程碑、风险与缓冲、知识库承接章节。
- 让 `validate-sprint-scope.py` 将这些章节纳入 Sprint 文档一致性校验。
- 同步 Sprint 相关技能、迭代规则和 workflow-sync 技能说明。
- 记录治理日志，明确本次不触碰业务 `src/`。

## 非目标

- 不改业务运行时代码、API、DB、Web、管理端或客户端实现。
- 不把 `sprint.md` 改成机器事实源；正式范围和容量仍以 `sprint.yaml` 为准。
- 不硬编码单个 Sprint 的业务风险、里程碑或知识库内容。
