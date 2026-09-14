---
change_id: enhance-ui-reference-replication-action-matrix
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-13 16:00:41
---

# Design: UI 参考稿复刻动作矩阵治理

## 设计目标

将 UI 参考稿复刻中的“按钮触发浮层”从零散验收项提升为前置矩阵，确保实现前已经知道每个动作按钮对应的 modal 类型、selector、状态和证据入口，并推动同一动作族一次性实现组件族。

## 事实源归属

| 事实 | 归属 |
|---|---|
| 动作按钮矩阵字段、适用条件和组件族约束 | `docs/standards/prototype-ui-acceptance.md` |
| UI 入口红线和执行摘要 | `rules/ui-design.md` |
| 上下文读取边界 | `rules/agent-context-budget.md` |
| 命令执行门禁 | `.agents/skills/{req-complete,req-opsx,opsx-apply,opsx-modify,opsx-archive}/SKILL.md` |
| 生效规格 delta | `openspec/changes/enhance-ui-reference-replication-action-matrix/specs/harness-runtime/spec.md` |

## 动作按钮矩阵合同

参考稿复刻范围包含动作按钮、卡片 footer、FAB、工具栏动作或阶段动作时，Change `design.md` 必须记录矩阵：

| 字段 | 说明 |
|---|---|
| 动作按钮 | 用户可见按钮、图标、所在组件和业务动作 |
| modal 类型 | dialog、drawer、popover、confirm、action-modal、ai-panel、inline-expanded 或 N/A |
| 参考 selector | 附件 HTML、参考页面、截图标注或文本锚点 |
| 目标 selector | 实现按钮、触发器、浮层根节点、关闭按钮和主操作 selector |
| 状态 | default、hover、focus、active、disabled、loading、open、submitted、error、empty、permission-hidden |
| 组件族 | 共用 Button、Modal/Drawer、ActionPanel、Form、Toast、Overlay 或专属组件 |
| 验收证据 | 截图、computed style、Playwright/DOM 断言、键盘/外部点击证据或 trace 摘要 |
| 处置结论 | 一次性实现、复用既有组件、保留现状、证据不足或超出范围 |

## 命令接入

- `/req-complete`：在参考稿复刻种子中记录动作按钮矩阵候选范围。
- `/req-opsx`：在 Change `design.md` 固化矩阵和组件族实现计划，`tasks.md` 将矩阵作为先行任务。
- `/opsx-apply`：实现 UI 前确认矩阵完整，同一动作族一次性实现按钮与 modal 组件族。
- `/opsx-modify`：若反馈只指出单个按钮或 modal，先扩展所属动作族矩阵，再做共享组件族返修。
- `/opsx-archive`：归档前确认矩阵、selector、computed style、截图证据和非目标保留一致。

## 验证策略

- 运行上下文预算校验，确认技能新增门禁未破坏命令契约。
- 运行 OpenSpec 中文优先校验和目标 Change validate。
- 运行目录结构校验，确认未新增非法顶层目录。
- 运行 Workflow Sync，确认纯治理 Change 已在 `sprint-004` 中可追溯。
