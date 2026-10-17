---
title: 需求中心卡片全命令产品链路真实化 Agent Workflow 规格增量
created_at: 2026-09-30 18:06:35
updated_at: 2026-09-30 18:37:27
---

# 需求中心卡片全命令产品链路真实化 Agent Workflow 规格增量

## MODIFIED Requirements

### Requirement: 原型驱动 UI 开发门禁

系统 SHALL 对带 `prototype/` 的 UI 页面建立从需求完善、OpenSpec 转换、实现、返修到归档的连续门禁，确保原型拆解、UI Contract、UI Skeleton 首轮确认、1440px 与关键交互视觉验收、computed style 验收、Mock/API 边界声明、图标文案一致性检查和 REQ 文档最终一致性检查均被记录并通过。

#### Scenario: req-opsx 承接动作按钮矩阵

- **GIVEN** 一个带 prototype 的 REQ 已进入 `/req-opsx`
- **AND** prototype 或 context 中包含动作按钮、弹窗、抽屉、Action Modal、AI 面板或归档确认
- **WHEN** 系统生成 active Change
- **THEN** Change `design.md` SHALL 包含动作按钮到 modal 类型、selector、状态和验收证据的矩阵
- **AND** Change `tasks.md` SHALL 包含先完成 UI Contract、UI Skeleton、selector 映射、computed style 采样和 1440px 首轮确认的任务
- **AND** Change `trace.md` SHALL 记录 prototype 来源、冲突处理、Skeleton 状态、Mock/API 边界、视觉证据、computed style 和 REQ 最终一致性状态

#### Scenario: 需求完善拆解 prototype
- **GIVEN** 一个 UI REQ 存在 `prototype/web/` 或等价页面原型目录
- **WHEN** 执行 `/req-complete <REQ-full-id>`
- **THEN** 系统 SHALL 在需求文档中记录原型页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点
- **AND** 系统 SHALL 将可测试验收项写入 `acceptance.md` 并在 `trace.md` 记录 `prototype_refs`

#### Scenario: OpenSpec 承接 UI Contract 和 UI Skeleton
- **GIVEN** 一个带 prototype 的 REQ 已进入 `/req-opsx`
- **WHEN** 系统生成 active Change
- **THEN** Change `design.md` SHALL 包含 UI Contract，声明事实源优先级、页面入口、信息架构、视觉 token、交互状态、图标文案、Mock/API 边界、权限规则和一致性参照
- **AND** Change `design.md` SHALL 包含 UI Skeleton 章节
- **AND** Change `tasks.md` SHALL 包含先完成 UI Contract 与 UI Skeleton 再实现细节的独立任务
- **AND** Change SHALL 记录 prototype 与 acceptance 的冲突处理结论

#### Scenario: 实现阶段执行视觉和样式验收
- **GIVEN** 一个带 prototype 的 UI Change 正在 `/opsx-apply` 或 `/opsx-modify`
- **WHEN** 相关 UI 任务准备标记完成
- **THEN** 系统 SHALL 先在 1440px 桌面视口完成视觉验收
- **AND** 系统 SHALL 对关键交互记录截图或等价证据
- **AND** 系统 SHALL 对原型敏感或曾返修的视觉点记录 computed style 或等价检查
- **AND** 系统 SHALL 记录 Mock/API 边界、验收命令和结果摘要

#### Scenario: 前后台一致性检查
- **GIVEN** 一个带 prototype 的 UI Change 需要对齐前台、后台或既有页面
- **WHEN** 系统执行 `/req-opsx`、`/opsx-apply` 或 `/opsx-modify`
- **THEN** 系统 SHALL 对品牌区、菜单分组、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸、hover/click outside、危险色、图标和文案进行 checklist 验收

#### Scenario: 归档前检查 REQ 最终一致性
- **GIVEN** 一个带 prototype 的 UI Change 准备 `/opsx-archive`
- **WHEN** 系统执行归档前文档同步门禁
- **THEN** 系统 SHALL 复核 linked REQ 的 `requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、验收结果一致
- **AND** 若发现验收口径、非目标、UI 行为、Mock/API 边界、computed style、视觉证据或实现差异，系统 SHALL 阻断归档并要求先回填或返修

### Requirement: 命令执行顺序治理

MoonBox MUST 维护 AI 工作流命令的推荐执行顺序，并在技能输出中给出符合链路身份的下一步命令。REQ 来源链路的后续实现和归档命令 MUST 使用原始 `REQ-*`，BUG 来源链路 MUST 使用原始 `BUG-*`，无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

#### Scenario: req-opsx 固化 execution schema

- **WHEN** 系统通过 `/req-opsx <REQ-full-id>` 创建 OpenSpec Change
- **THEN** Change `trace.md` frontmatter MUST 写入 `execution.schema_version: 1`
- **AND** `execution.started_at` 和 `execution.completed_at` MUST 为 `null`
- **AND** `execution.last_event` MUST 为 `req.opsx`
- **AND** 系统不得在创建 Change 时伪造开发启动或完成时间

#### Scenario: req-opsx 回填同一 Sprint

- **GIVEN** REQ 已通过 `/sprint-propose` 纳入某个 `sprint-xxx`
- **WHEN** `/req-opsx` 创建或确认 Change
- **THEN** Workflow Sync MUST 将该 Change 回填到同一 Sprint 的 `changes[]` 和对应 `scope_estimates[].change`
- **AND** 后续 `/opsx-apply`、`/opsx-modify` 和 `/opsx-archive` 输出与执行入口仍 MUST 使用完整 REQ ID

#### Scenario: writer 应用必须以 Workflow Sync 闭环

- **WHEN** 后端治理 writer 应用 REQ 或 BUG 来源的 generate、complete 或 review 类候选成果
- **THEN** writer MUST 在标记 application 为 `applied` 前执行对应 Workflow Sync 事件
- **AND** Workflow Sync 成功后 MUST 重读治理事实源并记录同步后的事实源摘要
- **AND** Workflow Sync 失败、事实源版本变化或外部修改冲突时 MUST 保持待恢复或冲突状态
- **AND** candidate 不得被标记为 `applied`
- **AND** 需求中心卡片不得刷新为完成态

#### Scenario: 推荐标准执行顺序

- **WHEN** 系统需要引导用户从需求或缺陷进入交付
- **THEN** 系统 SHOULD 推荐 `capture/complete/review → sprint-propose → req-opsx/bug-opsx → opsx-apply → opsx-modify → opsx-archive → sprint-archive → release/image/usage-docs` 的顺序
- **AND** `opsx-modify` MUST 只用于 `opsx-apply` 后、`opsx-archive` 前的验收返修
- **AND** release、image 和 usage-docs 命令 SHOULD 位于 OpenSpec 与 Sprint 关键门禁之后

#### Scenario: 串行写入事实源

- **WHEN** 命令会写入 `sprint.yaml`、Workflow Sync 派生块、Issue promote 结果或 AI Usage snapshot
- **THEN** 系统 MUST 严格串行执行这些步骤
- **AND** 系统 MUST NOT 并行运行多个会写同一 Sprint scope、Issue 状态或 AI Usage snapshot 的命令
- **AND** 系统 MUST 先写机器事实源，再运行 Workflow Sync 和对应校验
