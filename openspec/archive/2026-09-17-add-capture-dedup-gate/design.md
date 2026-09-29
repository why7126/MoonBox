---
title: Capture 创建前去重门禁设计
created_at: 2026-09-16 22:42:16
updated_at: 2026-09-16 22:42:16
---

# Capture 创建前去重门禁设计

## 设计目标

- 在创建新 REQ/BUG 前尽早识别项目中已存在的相同或高度相似事项。
- 保持上下文预算可控：先读目录级索引和 registry，只对候选项读取必要片段。
- 保留用户决策权：疑似重复时不自动覆盖旧 Issue，也不静默新建。
- 不引入业务代码、数据库或 API 行为变更。

## 检查范围

capture 类命令的检查顺序统一为：

1. 读取对应类型的 `CHANGELOG.md` 和 `_registry.yaml`，形成活动、评审和归档 Issue 候选清单。
2. 基于输入标题、关键词、业务域、页面/模块、现象、期望、复现要点、验收要点和关联 REQ/BUG 做相似候选筛选。
3. 仅当候选不够清晰时，读取候选目录中的 `capture.md` 和 `trace.md` 标题、Frontmatter、摘要段落、当前状态、关联 Sprint/Change 和下一步。
4. 对混合 `/capture` 输入，先拆分并分类，再分别按 REQ 或 BUG 检查。

## 决策策略

发现疑似重复时，命令输出候选表，至少包含：

- Issue ID 与标题。
- 当前阶段/状态。
- 相似原因。
- 建议处理方式。
- 事实源路径。

默认推荐：

- 对已有 REQ 的补充：关联或更新原 REQ，必要时使用 `parent_requirement`，不新建 peer REQ。
- 对同一缺陷的补充：关联或更新原 BUG，必要时填写 `related_bug` / `related_requirement`，不新建 peer BUG。
- 只有用户确认目标不是重复事项，或候选只是弱相关背景时，才继续创建新 Issue。

## 不做范围

- 不实现自动全文向量检索或语义模型判重。
- 不批量修改历史 Issue。
- 不改业务 `src/`、API、DB、Web 或管理端实现。
- 不把 `CHANGELOG.md` 当作状态事实源；候选命中后仍以 `_registry.yaml` 和单条 `trace.md` / `capture.md` 片段补证。
