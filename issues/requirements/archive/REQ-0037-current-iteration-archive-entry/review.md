---
review_id: REV-REQ-0037-001
date: 2026-09-14
participants:
  - product
result: approved
created_at: 2026-09-14 23:41:21
updated_at: 2026-09-14 23:41:21
---

# REQ-0037 需求评审

## 评审结论

通过。`REQ-0037-current-iteration-archive-entry` 已具备进入 Sprint 规划的条件。

本需求聚焦在当前迭代容量区域新增“归档当前迭代”入口，并明确不新增独立归档状态机、不绕过 Sprint archive 既有门禁、不自动归档未完成 Change、不自动补签验收报告或修复 Workflow Sync 漂移。范围、非目标、父需求关系和后续 Sprint archive 约束清晰。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 范围清晰，Out of Scope 明确 | 通过 | `requirement.md` 已区分首版包含与不包含，归档入口只进入确认流程，不直接执行归档。 |
| 验收标准可测试 | 通过 | `acceptance.md` 覆盖入口展示、不可用态、多当前迭代、确认流程、门禁失败、权限、成功刷新和失败恢复。 |
| 优先级与依赖合理 | 通过 | P1 合理；父需求为当前迭代容量展示，依赖需求中心当前迭代事实源与 Sprint archive 既有门禁。 |
| UI 类原型或实现策略已决 | 通过 | 已提供 `prototype/web/context.md` 与 `prototype/web/prototype.html`，并写入 AC-PROTOTYPE。 |
| 无与现有 REQ 重复未说明 | 通过 | 已说明为 `REQ-0031` 的 refinement，不改写父需求状态。 |
| 产品数据采集与链路观测 | 通过 | 已引用观测标准并声明 `usage_events`、`request_logs`、`task_traces` 适用；验收项覆盖脱敏与复用/补齐要求。 |

## 条件通过项

- [ ] `/req-opsx` 阶段必须在 Change `design.md` 中承接 `prototype_refs`、`prototype_gate`、UI Skeleton、点击外部关闭 capture 阶段验收、权限态和 Mock/API 边界。
- [ ] `/sprint-propose` 纳入 Sprint 前，需确认当前 Sprint 容量和范围可承接该高风险入口；不得直接跳到 `/req-opsx`。
- [ ] 实现阶段若复用既有 Sprint archive API 与 Task Trace，必须在 Change 文档中明确复用边界；若新增接口或字段，需同步 API、OpenAPI、客户端生成物和观测测试。

## 风险记录

- Sprint archive 是多步骤高风险写操作，前端入口只能作为确认流程入口；最终权限、门禁和状态写入必须以后端或既有治理命令事实源为准。
- 多当前迭代场景下必须绑定目标 Sprint，避免默认归档编号最大、更新时间最新或容量最高的 Sprint。
- 归档成功后当前迭代视图刷新失败会造成状态误导，需在实现阶段覆盖刷新失败和 Workflow Sync 失败回退。

## 下一步

`/sprint-propose --req REQ-0037-current-iteration-archive-entry`
