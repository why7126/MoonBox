---
review_id: REV-REQ-0032-001
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
date: 2026-09-14
participants:
  - product
result: approved
created_at: 2026-09-14 14:56:59
updated_at: 2026-09-14 14:56:59
---

# REQ-0032 需求评审

## 评审结论

通过。REQ-0032 聚焦需求中心 Sprint 筛选下拉新增状态展示，属于已有需求中心迭代信息能力的局部体验增强。范围、非目标、事实源边界、权限边界、观测声明和 UI 原型策略均已补齐，可进入 Sprint 规划。

本评审记录当时的准入结论；该需求后续已纳入 sprint-006，创建 OpenSpec Change，并完成实现与归档。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 范围清晰，Out of Scope 明确 | 通过 | 仅增强需求中心 Sprint 筛选下拉状态展示，不新增 Sprint 管理、分组、多选或状态修复。 |
| 验收标准可测试 | 通过 | acceptance.md 覆盖状态映射、异常降级、筛选兼容、UI、权限和观测检查。 |
| 优先级与依赖合理 | 通过 | P2 合理；依赖 REQ-0012/REQ-0022/REQ-0026 的需求中心事实源和稳定快照能力。 |
| UI 类原型或实现策略已决 | 通过 | prototype/web/context.md 和 prototype.html 已补齐；后续 Change 需写 UI Contract 与 Skeleton。 |
| 无与现有 REQ 重复未说明 | 通过 | 与 REQ-0030、REQ-0031 同属迭代信息增强，但本条只处理 Sprint 筛选状态展示。 |
| 产品数据采集与链路观测声明 | 通过 | 已声明 applicable，影响 usage_events、request_logs；不预期新增 DB、Task Trace 或对象存储。 |

## 条件通过项

- [ ] 后续 `/req-opsx` 需核实现有需求中心上下文或 Sprint 列表接口是否已有结构化状态字段；若没有，应在 OpenSpec 中明确 API/类型扩展和兼容策略。
- [ ] 后续 `/opsx-apply` 需补齐 1440px、窄屏、深浅主题、长 Sprint 名称和异常状态的真实视觉或等价证据。
- [ ] 后续实现不得回退加入迭代弹窗已有 Sprint 状态/容量展示，两个入口的状态口径需保持一致。

## 风险与处置

| 风险 | 等级 | 处置 |
|---|---|---|
| 现有 `sprintOptions` 可能只提供字符串，缺少状态字段 | medium | OpenSpec 阶段先核实 API/后端派生能力；必要时补 API、OpenAPI 和客户端类型。 |
| 原生 select 对复杂标签展示支持有限 | medium | Change 设计阶段明确使用原生 select 文案增强，或受控 combobox；需覆盖键盘可达性。 |
| Sprint 状态事实源和归档目录事实可能冲突 | low | 按 PRD 降级为“状态待核实”，不前端猜测正常状态。 |

## 下一步建议

1. 已完成 sprint-006 纳入、OpenSpec Change 创建、实现、验收与归档。

