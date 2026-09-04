---
change_id: apply-tilesfst-sprint-md-governance
status: proposed
created_at: 2026-08-27 01:02:45
updated_at: 2026-08-27 01:02:45
---

# 设计说明

## 1. 学习来源与适配原则

学习对象记为 `ProjectTilesFST（本地只读项目）`。本变更只采纳 sprint.md 治理模式：

- `sprint.yaml` 仍是正式范围机器事实源。
- `sprint.md` 作为产品化规划面板，展示目标编号列表、逐项要点、Scope、容量、里程碑、风险、知识库承接和横切预防清单。
- Workflow Sync 负责刷新可派生内容，避免手工编辑 marker block 或 Scope 表。
- Fact Sheet 为 `/sprint-exps` 和 `/sprint-archive` 的读优先摘要，原始 `tasks.md` / `trace.md` / acceptance 只在 blockers 或 warnings 指向时读取。

## 2. Workflow Sync 增强

`scripts/workflow_sync/patch.py` 新增目标区渲染：

- 在 `## 1. Sprint 目标` 内维护 `### Sprint 目标编号列表`。
- 对每个正式范围项生成 `### <id> 要点`。
- REQ/BUG 要点优先使用 Issue 标题、派生状态、关联 Change 状态和 Scope 说明。
- 纯治理 Change 要点使用 Change id、状态和 Scope 说明。

该生成逻辑只写当前项目 Sprint 文档，不读取或复制学习对象内容。

## 3. Scope 校验增强

`scripts/validate-sprint-scope.py` 保持原有校验：

- Scope 主表必须为六列：`类型 | 编号 | 标题 | 状态 | 估算 | 说明`。
- REQ/BUG/Change 必须出现在 Scope 主表。
- REQ/BUG/Change 必须出现在 workflow-sync 派生表。

新增校验：

- `## 1. Sprint 目标` 必须包含 `Sprint 目标编号列表`。
- 正式范围中的 REQ/BUG/纯 Change 必须出现在目标编号列表。
- 正式范围中的每个条目必须有 `### <id> 要点` 段落。

## 4. 技能与规则同步

同步范围：

- `/sprint-propose`：创建或追加 Sprint 范围后，要求目标编号列表、要点段落、Scope 主表、容量、知识库承接和横切预防清单一致。
- `/sprint-apply`：执行队列前优先读取 `sprint.yaml` 与 `sprint.md` 目标/Scope/依赖/横切摘要，避免全量展开历史。
- `/sprint-archive`：归档前优先读取 Sprint Fact Sheet，并按 readiness/blocker 定向读取原始文档。
- `/sprint-exps`：复盘前优先读取 Fact Sheet，AI Usage fresh gate 与 batch summary 指向问题后再读取原始材料。
- `rules/iterations-lifecycle.md`：明确 `sprint.md` 产品化规划面板结构与校验要求。

## 5. 不采纳说明

- 不迁移 ProjectTilesFST 的业务专属风险、验收清单和小程序内容。
- 不把 `sprint.md` 变成新的机器事实源；正式范围仍以 `sprint.yaml` 和 Workflow Sync 派生结果为准。
- 不在本次变更中改造所有历史归档 Sprint。
