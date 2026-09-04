---
requirement_id: REQ-0023-product-workbench-modern-ops-visual-system
title: MoonBox 产品工作台全面升级为现代 Ops 视觉系统 - 验收标准
acceptance_status: pending
created_at: 2026-08-30 23:24:18
updated_at: 2026-09-03 21:47:10
owner: product
---

# 验收标准

## 功能 AC

- [ ] AC-001 品牌升级范围已明确，至少在“仅产品工作台”“Web 前台加管理后台”“全站统一现代化”之间选择一种，并说明取舍原因。
- [ ] AC-002 PRD 明确公开品牌页、登录页、产品工作台、管理后台和产品手册的视觉分层策略，避免新旧品牌规则冲突。
- [ ] AC-003 现代 Ops 设计 token 已定义背景、面板、边框、文字、强调色、状态色、圆角、阴影、间距、字号、控件高度、图标尺寸和动效。
- [ ] AC-004 字体策略已明确中文 UI 字体、英文展示字体和等宽辅助字体的使用范围，并覆盖 REQ/BUG ID、命令、版本号和状态码。
- [ ] AC-005 核心组件规范覆盖 Sidebar、Header、统计卡、Toolbar、搜索、segmented、筛选 Popover、Kanban、Card、Drawer、Modal、Toast 和 AI 入口。
- [ ] AC-006 附件风格吸收边界已明确，保留统计趋势、筛选 badge、横向滚动提示、空列状态、卡片状态层级等高价值模式，并排除机械复制附件 HTML 的实现细节。
- [ ] AC-007 迁移计划已按试点、核心路径、全量迁移分阶段描述，并明确每阶段页面范围、验收证据和回退策略。
- [ ] AC-008 深色与浅色主题均完成可读性设计，关键文本、边框、状态色、focus、disabled 和 loading 状态不出现低对比或误导。
- [ ] AC-009 产品工作台页面不得出现文本重叠、控件遮挡、卡片高度剧烈跳动、横向滚动不可达或浮层无退出路径。
- [ ] AC-010 后续实现如涉及 UI 规则、设计系统文档、组件样式或验收标准变化，必须同步对应文档和测试。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Contract 与 UI Skeleton，明确事实源优先级、品牌分层、token、组件和 Mock/API 边界。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 阶段必须先完成工作台 Shell 与需求中心试点 Skeleton，再进入细节迁移和业务交互调整。
- [ ] AC-PROTOTYPE-004 1440px 桌面视觉验收必须覆盖首页或登录入口边界、产品工作台、需求中心看板、筛选 Popover、用户菜单、右侧抽屉和深浅主题。
- [ ] AC-PROTOTYPE-005 computed style 证据必须记录关键字体、字号、行高、间距、圆角、边框、背景、颜色、z-index、overflow 和 position。
- [ ] AC-PROTOTYPE-006 归档前必须确认 `requirement.md`、`acceptance.md`、`trace.md` 与最终 Change 设计、实现证据和视觉验收结论一致。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-list-page-consistency.md`、`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`、`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` — 预防 Sprint 002/003 复发类缺陷

- [ ] AC-XCUT-001 管理后台或工作台列表页迁移后，分页 DOM 必须对齐用户管理基准：总数位于左侧，翻页、页码、“每页显示”文案和条数下拉位于右侧。
- [ ] AC-XCUT-002 成功和失败反馈必须使用 fixed toast，不得引发布局位移，不得挤压列表、分页、弹窗、抽屉或看板内容。
- [ ] AC-XCUT-003 冻结、解冻、删除、重置、恢复默认、退出登录等状态变更必须使用设计系统确认弹窗或等价确认组件。
- [ ] AC-XCUT-004 管理后台和产品工作台状态变更不得调用 `window.confirm`。
- [ ] AC-XCUT-005 表格行内操作列在横向滚动或列较多时必须保持易访问，筛选条件变化后结果、分页和空态必须与当前条件一致。
- [ ] AC-XCUT-006 弹窗 TSX 或模板实现中不得让通用 `modal-card` 与专属宽度类并存，避免 CSS 级联覆盖业务弹窗宽度。
- [ ] AC-XCUT-007 弹窗必须通过浏览器 computed style 验收最终宽度，并确认与设计预期一致。
- [ ] AC-XCUT-008 低视口下弹窗 body 必须可滚动，底部主操作和取消操作必须可访问。
- [ ] AC-XCUT-009 弹窗遮罩不得吞掉内部滚动，也不得导致页面主体误滚动；必填字段、错误提示和底部操作区不得互相遮挡。
- [ ] AC-XCUT-010 Change `design.md` 必须存在 UI Skeleton，覆盖页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点。
- [ ] AC-XCUT-011 Change `tasks.md` 中 UI Skeleton 任务必须早于细节实现任务。
- [ ] AC-XCUT-012 视觉验收证据必须记录工具或命令、viewport、页面路径、截图或等价证据入口、结果摘要和例外说明。
- [ ] AC-XCUT-013 `admin-form` 横切 AC 暂未纳入：N/A — 当前仓库缺少对应 best-practice 文件，且本需求不是具体后台表单页；若后续实现涉及设置页或表单页，应先补齐知识库或在 Change 设计中声明等价验收。
- [ ] AC-XCUT-014 `media-upload` 横切 AC 暂不适用：N/A — 本需求不涉及图片、视频、头像或 Logo 上传与回显链路。

## Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | capture、requirement、user-stories、business-flow、acceptance、trace 与 Web 原型拆解已补齐 |
| Knowledge-base gate | Pass | 已读取并转化 `admin-list`、`admin-modal`、`prototype-driven-ui` 相关知识库；`admin-form` 文件缺失已作为 N/A 风险说明 |
| Prototype Gate | Pass | `prototype/web/context.md` 与 `prototype/web/prototype.html` 已创建，REQ 阶段拆解完成，后续 UI Skeleton 与 1440px 验收待 Change 实现阶段完成 |
| 产品数据采集与链路观测 | N/A | 当前需求为 UI 视觉系统与品牌升级，不改变 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装 |

## 验收结果回填

```yaml
acceptance_status: pending
accepted_at: null
accepted_by: null
source_change: update-product-workbench-modern-ops-visual-system
source_sprint: sprint-004
evidence: []
failed_items: []
source_event: opsx.modify
notes: 待验收；由 opsx.apply 标记，后续 archive 时回填结论。
```

## 返修验收补充

| 时间 | 反馈 | 处理 | 证据 |
|---|---|---|---|
| 2026-09-02 18:49:50 | 需求中心九阶段右下 Agent 助手入口需按附件 `.fab` 和 Action Modal 交互实现，不再直接打开右侧 AI Chat 抽屉 | 已仅调整右下金色 pill `Agent 助手` 入口和居中 Agent 操作面板；面板按 9 阶段展示当前可执行动作与上下文提示，并复用既有 `runIssueAction`、确认弹窗、toast、任务进度和 AI 消息能力 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-agent-modal-1440.png`、`computed-styles.json` |
| 2026-09-02 19:18:20 | 需求中心九阶段卡片动作按钮需参照附件 Action Modal 组件族复刻弹窗交互，覆盖分析、生成、完善、评审/确认、迭代、Opsx、开发/修复、进度和归档状态 | 已仅调整卡片动作按钮的弹窗承载：卡片主/辅助动作统一先打开附件式 Action Modal，再复用既有 `runIssueAction`、toast、任务进度和 AI 消息能力；补齐 loading、checklist、dropzone、tabs、progress、confirm 状态 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-modal-1440.png`、`requirements-action-generate-modal-1440.png`、`requirements-action-complete-modal-1440.png`、`requirements-action-sprint-modal-1440.png`、`requirements-action-opsx-modal-1440.png`、`requirements-action-progress-modal-1440.png`、`computed-styles.json` |
| 2026-09-02 19:42:32 | 需求分析 Action Modal 的解决方案要点需支持勾选，三条默认全选，可取消/重选并同步底部按钮数量 | 已仅修正需求分析 modal 要点交互：三条默认选中，点击切换 `aria-pressed` 状态，按钮文案实时显示 `采纳 n/3 项并保留分析 →`，0 项禁用；不改其它 Action Modal 或看板静态视觉 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-selection-1440.png`、`computed-styles.json` |
| 2026-09-02 22:38:41 | 已完成卡片不需要显示进度信息或 `查看归档` 动作 | 已仅调整 `done` 阶段卡片展示：隐藏研发/测试/人工验收进度和 footer 动作按钮，保留 `archive.md`、`trace.md` 文档入口及卡片基础信息；不改其它阶段卡片和看板视觉 | `src/web/src/requirement-center.test.tsx` |
| 2026-09-02 23:12:00 | 加入迭代弹窗需按附件 `sprintModal` 一比一收敛结构与样式 | 已仅调整加入迭代 Action Modal：补齐对象 label 与左侧金色边对象信息块、`加入现有迭代 / 新建迭代` 文案、现有迭代 radio、状态 pill、容量 used/total、capacity bar、容量不足 disabled/badge，以及新建迭代编号和确认按钮禁用/文案联动；不改其它 Action Modal、看板和静态视觉 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-sprint-modal-1440.png`、`computed-styles.json` |
| 2026-09-03 21:47:10 | 任务卡片进度行 `x/x` 数值颜色被回退，未保持附件 label/value 分层 | 已仅恢复 `.rc-progress` 的 JetBrains Mono、10.5px、10px gap，恢复 `.rc-progress-value` 为 secondary 色和 600 字重；保持无特殊符号纯间距和既有点击能力 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` |
