---
requirement_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
acceptance_status: passed
created_at: 2026-09-14 23:35:53
updated_at: 2026-09-29 14:44:19
owner: product
source: requirement.md
---

# 验收标准

## 功能 AC

- [x] AC-001 入口展示：当存在当前迭代且 `used_capacity > 0` 人天时，需求中心在当前迭代容量区域或当前迭代操作区展示“归档当前迭代”入口。
- [x] AC-002 不可用状态：当无当前迭代、`used_capacity = 0`、容量待核实、当前用户无可见 Sprint，或 Sprint 范围内任一 REQ、BUG、独立 Change 未归档闭环时，不提供可执行归档入口；如展示禁用态，必须说明安全摘要。
- [x] AC-003 多当前迭代：存在多个当前迭代时，每个归档入口或确认流程明确绑定目标 Sprint，不默认选择编号最大、更新时间最新或容量最高的 Sprint。
- [x] AC-004 确认流程：点击入口后进入确认流程，不直接执行归档；确认流程展示目标 Sprint ID、当前状态、容量摘要、门禁检查结果和归档影响。
- [x] AC-005 取消确认：用户取消确认后，不改变 Sprint、REQ、BUG、Change、验收报告或 Workflow Sync 状态。
- [x] AC-006 门禁复用：归档执行前复用 Sprint archive 既有门禁，覆盖范围内 REQ/BUG/独立 Change 归档闭环、验收报告 sign-off、权限和 Workflow Sync 校验。
- [x] AC-007 门禁失败：任一门禁失败时不能执行归档；页面展示失败项和修复方向，不提供“强制归档”绕过按钮。
- [x] AC-008 权限一致：无归档权限用户不能执行归档；前端入口状态与后端权限校验一致，错误摘要不泄露不可见资源或敏感信息。
- [x] AC-009 成功刷新：归档成功后，需求中心刷新当前迭代列表、容量区域、Scope 投影和相关卡片状态，已归档 Sprint 不再伪装为当前迭代。
- [x] AC-010 失败恢复：门禁检查、执行请求或 Workflow Sync 刷新失败时，页面保留当前迭代容量和卡片上下文，并展示轻量失败信息。

## UI 与交互 AC

- [x] AC-UI-001 入口位置贴近当前迭代容量信息，视觉权重低于容量核心数值和异常提示，高于普通辅助链接。
- [x] AC-UI-002 归档入口使用清晰动作文案或熟悉 icon；仅使用 icon 时必须提供 tooltip。
- [x] AC-UI-003 确认弹窗或 action modal 至少包含目标 Sprint、门禁状态、取消入口和主操作入口；高风险操作不得只依赖 toast 确认。
- [x] AC-UI-004 弹窗/浮层支持可理解退出路径；声明 click outside 时，验收需覆盖内部 `stopPropagation` 不误关闭、外部点击仍按约定关闭。
- [x] AC-UI-005 窄屏、长 Sprint ID、多当前迭代、无权限和失败态下，文本不与容量条、按钮、筛选器或卡片内容重叠。
- [x] AC-UI-006 禁用态、失败态和高风险状态不只依赖颜色表达，需提供文本、图标或 tooltip 辅助。

## 权限、安全与观测 AC

- [x] AC-SEC-001 服务端不得信任客户端传入的 Sprint ID、门禁状态、行为链路字段或权限状态作为最终授权依据。
- [x] AC-SEC-002 错误提示、行为事件、请求日志和 Task Trace 不记录完整文档正文、本机绝对路径、Authorization、Cookie、密钥、真实 `.env` 或未脱敏错误堆栈。
- [x] AC-OBS-001 入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败应具备行为事件或等价观测摘要。
- [x] AC-OBS-002 归档执行请求应具备请求日志摘要；若复用既有 archive API，Change 文档需说明复用口径和不新增字段的原因。
- [x] AC-OBS-003 Sprint archive 属于多步骤高风险写操作；实现阶段需复用或补齐 Task Trace，以定位校验、归档、同步和失败节点。

## 文档与测试 AC

- [x] AC-DOC-001 若新增或调整 API、OpenAPI、客户端生成类型、请求封装、行为事件、请求日志或 Task Trace，必须同步对应文档和测试。
- [x] AC-DOC-002 若完全复用既有 Sprint archive API 与观测链路，OpenSpec Change 需记录 N/A 原因、复用边界和验证摘要。
- [x] AC-TEST-001 自动化或等价验收需覆盖入口展示、隐藏或禁用、确认取消、REQ 未归档、BUG 未归档、独立 Change 未归档、验收 sign-off 缺失、权限拒绝、归档成功、Workflow Sync 失败、多当前迭代和刷新一致性。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点，见 `prototype/web/context.md`。
- [x] AC-PROTOTYPE-002 `/req-opsx` 生成的 Change `design.md` 必须承接 UI Skeleton，覆盖页面结构、容量区域、归档入口、确认弹窗、门禁结果、权限态和错误态。
- [x] AC-PROTOTYPE-003 `/opsx-apply` 完成 UI 任务前必须在 1440px 桌面视口验证首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出。
- [x] AC-PROTOTYPE-004 归档前必须确认 REQ `requirement.md`、`acceptance.md`、`trace.md` 与最终 Change 设计、实现证据、Mock/API 边界和视觉验收结果一致。

## 知识库引用

| 标签 | 引用文档 | 写入 AC |
|---|---|---:|
| prototype-ui | `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` | 4 |
| sprint-005-retro | `docs/knowledge-base/retrospectives/sprint-005-retrospective.md` | 2 |
| admin-list/admin-form/admin-modal/media-upload | 无匹配标签，本 REQ 是前台需求中心高风险动作入口，不是管理端 CRUD、表单、弹窗新建/编辑或媒体上传 | 0 |

## 横切 AC（knowledge-base）

本 REQ 未命中 `req-complete` 规定的 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 横切标签，因此不新增 `AC-XCUT-*` 管理端横切 AC。已将原型驱动 UI Gate 和 Sprint-005 需求中心动作族经验写入 `AC-PROTOTYPE-*`、`AC-UI-*`、`AC-OBS-*` 与 `AC-TEST-*`。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:44:19
accepted_by: workflow-sync
source_change: add-current-iteration-archive-entry
source_sprint: sprint-007
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-09-15 08:35:49 | CapacityItem 需按左侧 sprint id + 状态 badge、中间容量数值 + 进度条、右侧归档 icon button 三列呈现；归档 icon button 不要边框 | 桌面改为三列布局；状态 badge 移到左侧并通过 title 显示容量来源/说明；归档 icon button 去边框并保留归档/无法归档说明与 readiness safe_summary；390px 下安全堆叠 | `src/tmp/visual-evidence/req0037-capacity-tricol-1440.png`、`src/tmp/visual-evidence/req0037-capacity-tricol-390.png`；前端单测、TypeScript、OpenSpec strict 与 Playwright 视觉断言通过 |
| 2026-09-15 08:27:06 | 看板列头与首张卡片/空列框之间距离偏大，Image #1 红框约 57px，研发中与验收中起点观感不够紧凑 | `.rc-column-body` 与空列顶部 padding 从 20px 收紧为 10px；空列虚线框 top inset 从 20px 收紧为 10px；保持列宽、列头、卡片、阶段状态和归档入口逻辑不变 | 前端样式契约测试、TypeScript、OpenSpec strict 通过；Playwright 1440px 聚焦截图和 computed style 显示 `developmentGap: 16`、`bodyPaddingTop: 10px`、`emptyBeforeTop: 10px` |
| 2026-09-15 08:22:45 | 当前迭代容量条右侧需保留原状态，归档入口改为图标按钮，readiness 长摘要改为 hover/title 说明 | 状态 badge 固定在容量卡片右上角；归档按钮改为 34px icon-only；安全摘要移入 `title`；390px 下消除桌面 flex-basis 空白 | `src/tmp/visual-evidence/req0037-modify-1440.png`、`src/tmp/visual-evidence/req0037-modify-390.png`；前端单测、TypeScript、OpenSpec strict 与 Playwright 视觉断言通过 |

```yaml
acceptance_status: passed
accepted_at: 2026-09-17 10:24:46
accepted_by: workflow-sync
source_change: add-current-iteration-archive-entry
source_sprint: sprint-007
evidence:
  - uv run pytest tests/integration/api/test_requirement_center.py
  - ./node_modules/.bin/vitest run src/requirement-center.test.tsx -t "workflow demo|current iteration|archive readiness"
  - ./node_modules/.bin/tsc -b --pretty false
  - openspec validate add-current-iteration-archive-entry --strict
  - python scripts/validate-openspec-language.py --change add-current-iteration-archive-entry --residual-report
  - /private/tmp/req0037-desktop.png
  - /private/tmp/req0037-desktop-dialog.png
  - /private/tmp/req0037-mobile.png
  - /private/tmp/req0037-mobile-dialog.png
  - src/tmp/visual-evidence/req0037-modify-1440.png
  - src/tmp/visual-evidence/req0037-modify-390.png
  - src/tmp/visual-evidence/req0037-board-gap-1440-scrolled.png
  - src/tmp/visual-evidence/req0037-board-gap-1440-scrolled-computed.json
  - src/tmp/visual-evidence/req0037-capacity-tricol-1440.png
  - src/tmp/visual-evidence/req0037-capacity-tricol-390.png
failed_items: []
source_event: opsx.modify
notes: 实现完成并完成验收返修及归档验收；本 Change 不新增真实 Sprint archive 执行 API，归档执行、权限、请求日志、Task Trace 和 Workflow Sync 失败继续复用 /sprint-archive 既有门禁链路。
```
