---
purpose: 原型驱动 UI 开发门禁治理优化设计
content: prototype 页面拆解、Skeleton、1440px 验收和 REQ 最终一致性检查的命令协作设计
created_at: 2026-08-08 21:08:00
updated_at: 2026-08-08 22:01:14
owner: MoonBox 产品团队
source_requirement: REQ-0008-prototype-driven-page-acceptance-gate
---

# 设计

## D1. Prototype-driven UI Gate

当 REQ 存在 `prototype/web/` 或其他页面原型目录时，视为带 prototype 的 UI 页面。命令必须按阶段传递同一事实链：

```text
req-complete 原型拆解
→ req-opsx Change 设计与任务化
→ opsx-apply UI Skeleton 与 1440px 视觉验收
→ opsx-modify 返修再验收
→ opsx-archive REQ 最终一致性检查
→ workflow-sync 回填验收状态与证据入口
```

## D1.1 REQ-0008 承接范围

本 Change 正式承接 `REQ-0008-prototype-driven-page-acceptance-gate`。门禁首期只覆盖 Web 前台和管理后台页面，不覆盖未来小程序、移动端、桌面端或其他非 Web 端。

触发条件为页面需求存在 `prototype.html` 或 `prototype.png`。无原型资产的页面不因本门禁被阻断，但必须记录不适用原因。

## D2. 原型拆解

`/req-complete` 必须为带 prototype 页面补齐 `prototype/web/context.md` 的结构化信息，包括页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。拆解结果应进入 `acceptance.md` 的可测试 AC 和 `trace.md` 的 `prototype_refs`。

## D3. UI Skeleton

`/req-opsx` 必须将原型拆解转化为 Change `design.md` 的 UI Skeleton 章节和 `tasks.md` 的独立任务。Skeleton 不是装饰性线框，而是开发前必须先稳定的页面结构、路由、布局区域、组件插槽、状态容器和可测选择器。

## D3.1 UI Skeleton

UI Skeleton 必须先于业务逻辑联调完成，覆盖页面结构、主要布局区块、关键组件占位、mock 数据或静态样例、基础状态展示、可测选择器和高风险 DOM/CSS 区域。后续业务逻辑联调不得破坏已验收的 Skeleton；若破坏，必须重新执行受影响范围的 1440px 截图验收和 DOM/CSS 检查。

## D3.2 Conflict Resolution

当 `prototype.html`、`prototype.png`、`prototype/context.md`、`acceptance.md`、`rules/ui-design.md` 或现有 OpenSpec spec 存在冲突时，按以下顺序处理：

```text
prototype.html > prototype.png > prototype/context.md > acceptance.md > rules/ui-design.md > openspec/specs
```

若具体页面需求另有明确优先级，以该页面需求的 `prototype/context.md`、acceptance 或 Change design 为准，并在 trace 中记录冲突处理结论。

## D4. 1440px 视觉验收

`/opsx-apply` 对带 prototype 页面必须在 1440px 桌面视口完成浏览器验收，记录截图或等价证据入口，检查首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出。若 1440px 证据缺失，不得将对应 UI 任务标记完成。

## D5. REQ 最终一致性回填

`/opsx-archive` 归档前必须复核 REQ `requirement.md`、`acceptance.md`、`trace.md` 与 Change 设计、实现证据、验收结果一致。存在验收口径、非目标、UI 行为、视觉证据或实现差异时，必须先通过 `/opsx-modify` 或文档回填解决，再归档。
