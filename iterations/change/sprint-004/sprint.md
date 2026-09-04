---
note: workflow-sync — workflow-sync 自动同步 — 4/6 Change archived；2 applied；Sprint `planning`
sprint_id: sprint-004
status: planning
lifecycle_stage: change
created_at: 2026-08-31 08:39:23
updated_at: 2026-09-04 16:14:57
---

# sprint-004 迭代规划

## 1. Sprint 目标

承接 MoonBox 产品工作台现代 Ops 视觉系统升级，优先完成品牌分层、设计 token、核心组件规范和原型驱动 UI Gate，为后续实现建立统一视觉与验收基线。

### Sprint 目标编号列表

- REQ-0023-product-workbench-modern-ops-visual-system
- REQ-0024-markdown-editor-human-edit-permission-matrix
- add-ui-reference-replication-governance
- enforce-css-content-ascii-escape
- optimize-workflow-sync-observability-status-boundary
- apply-tilesfst-local-session-jsonl-governance

### REQ-0023-product-workbench-modern-ops-visual-system 要点

REQ `REQ-0023-product-workbench-modern-ops-visual-system`：MoonBox 产品工作台全面升级为现代 Ops 视觉系统。当前状态 in_sprint，估算 8 人天；apply 19/19；待 archive `update-product-workbench-modern-ops-visual-system`。

### REQ-0024-markdown-editor-human-edit-permission-matrix 要点

REQ `REQ-0024-markdown-editor-human-edit-permission-matrix`：Markdown 编辑器按治理阶段扩展人工编辑权限矩阵。当前状态 in_sprint，估算 3 人天；apply 25/25；待 archive `update-markdown-editor-human-edit-permission-matrix`。

### add-ui-reference-replication-governance 要点

Change `add-ui-reference-replication-governance`：add ui reference replication governance。当前状态 archived，估算 1 人天；archived `add-ui-reference-replication-governance`（2026-09-02 19:12:31）。

### enforce-css-content-ascii-escape 要点

Change `enforce-css-content-ascii-escape`：enforce css content ascii escape。当前状态 archived，估算 1 人天；archived `enforce-css-content-ascii-escape`（2026-09-03 09:45:40）。

### optimize-workflow-sync-observability-status-boundary 要点

Change `optimize-workflow-sync-observability-status-boundary`：optimize workflow sync observability status boundary。当前状态 archived，估算 1 人天；archived `optimize-workflow-sync-observability-status-boundary`（2026-09-04 08:14:54）。

### apply-tilesfst-local-session-jsonl-governance 要点

Change `apply-tilesfst-local-session-jsonl-governance`：apply tilesfst local session jsonl governance。当前状态 archived，估算 1 人天；archived `apply-tilesfst-local-session-jsonl-governance`（2026-09-04 16:05:54）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0023-product-workbench-modern-ops-visual-system | MoonBox 产品工作台全面升级为现代 Ops 视觉系统 | in_sprint | 8 人天 | apply 19/19；待 archive `update-product-workbench-modern-ops-visual-system` |
| REQ | REQ-0024-markdown-editor-human-edit-permission-matrix | Markdown 编辑器按治理阶段扩展人工编辑权限矩阵 | in_sprint | 3 人天 | apply 25/25；待 archive `update-markdown-editor-human-edit-permission-matrix` |
| Change | add-ui-reference-replication-governance | add ui reference replication governance | archived | 1 人天 | archived `add-ui-reference-replication-governance`（2026-09-02 19:12:31） |
| Change | enforce-css-content-ascii-escape | enforce css content ascii escape | archived | 1 人天 | archived `enforce-css-content-ascii-escape`（2026-09-03 09:45:40） |
| Change | optimize-workflow-sync-observability-status-boundary | optimize workflow sync observability status boundary | archived | 1 人天 | archived `optimize-workflow-sync-observability-status-boundary`（2026-09-04 08:14:54） |
| Change | apply-tilesfst-local-session-jsonl-governance | apply tilesfst local session jsonl governance | archived | 1 人天 | archived `apply-tilesfst-local-session-jsonl-governance`（2026-09-04 16:05:54） |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0023 | MoonBox 产品工作台全面升级为现代 Ops 视觉系统 | P1 | in_sprint | apply 19/19；待 archive `update-product-workbench-modern-ops-visual-system` |
| REQ-0024 | Markdown 编辑器按治理阶段扩展人工编辑权限矩阵 | P1 | in_sprint | apply 25/25；待 archive `update-markdown-editor-human-edit-permission-matrix` |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `update-product-workbench-modern-ops-visual-system` | REQ-0023-product-workbench-modern-ops-visual-system | applied | apply 19/19；待 archive `update-product-workbench-modern-ops-visual-system` |
| `add-ui-reference-replication-governance` | — | archived | archived `add-ui-reference-replication-governance`（2026-09-02 19:12:31） |
| `enforce-css-content-ascii-escape` | — | archived | archived `enforce-css-content-ascii-escape`（2026-09-03 09:45:40） |
| `optimize-workflow-sync-observability-status-boundary` | — | archived | archived `optimize-workflow-sync-observability-status-boundary`（2026-09-04 08:14:54） |
| `update-markdown-editor-human-edit-permission-matrix` | REQ-0024-markdown-editor-human-edit-permission-matrix | applied | apply 25/25；待 archive `update-markdown-editor-human-edit-permission-matrix` |
| `apply-tilesfst-local-session-jsonl-governance` | — | archived | archived `apply-tilesfst-local-session-jsonl-governance`（2026-09-04 16:05:54） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0023`、`REQ-0024` 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 2 个范围项关联 Change，另有 4 个纯 Change；4 archived，2 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 15 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 15 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 50.00% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 15 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 50.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | pass：未超过容量 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 2026-08-31 08:39:23 | 四件套创建并纳入正式范围 | planning |
| 范围实现完成 | 2026-09-14 08:39:23 | `changes[]` 全部 apply 完成 | 6/6 已 apply 或 archive |
| 归档收口 | 2026-09-14 08:39:23 | `changes[]` 全部 archive，验收报告完成 sign-off | 4/6 已 archive，2 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 待归档积压 | low | applied 2/6 | 完成验收后批量或逐项 `/opsx-archive` |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-004-retrospective.md` | 4/6 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

- `admin-list`：分页、fixed toast、设计系统确认弹窗、禁用 `window.confirm`、筛选结果与空态一致。
- `admin-modal`：弹窗宽度类不冲突、computed style 验收、低视口 body 可滚动、遮罩不吞内部滚动。
- `prototype-driven-ui`：Change 阶段必须写入 UI Skeleton，视觉验收覆盖 1440px、computed style、深浅主题和 REQ 最终一致性。

## 8. 依赖 ASCII 树

```text
REQ-0023-product-workbench-modern-ops-visual-system
└── /req-opsx
    └── OpenSpec Change
        └── /opsx-apply
```

## 9. 发布计划

以工作台视觉系统升级为主线，后续 Change 完成后进入版本发布对象评估；本 Sprint 规划阶段不直接发布。

## 10. 关联文档

- `issues/requirements/review/REQ-0023-product-workbench-modern-ops-visual-system/`
- `docs/knowledge-base/best-practices/admin-list-page-consistency.md`
- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
