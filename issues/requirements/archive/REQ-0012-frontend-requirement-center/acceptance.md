---
requirement_id: REQ-0012-frontend-requirement-center
title: MoonBox 前台需求中心
acceptance_status: passed
owner: product
source: requirement.md
priority: P1
created_at: 2026-08-10 12:57:18
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 功能 AC

- [ ] AC-001 页面展示 9 阶段需求研发流转看板：采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成；每个阶段列头必须展示阶段标题、原型命令副标题和两位数对象数量。
- [ ] AC-002 Requirement 与 Bug 使用同一生命周期框架，但卡片视觉可区分：Requirement 左侧蓝色边框，Bug 左侧红色边框。
- [ ] AC-003 卡片展示 ID、标题、优先级、负责人或来源、阶段产物、更新时间、阻塞状态、研发/测试进度和阶段主动作；卡片必须使用原型式单 pill meta、文档分隔区、无边框 mini action 和弱层级更新时间。
- [ ] AC-004 看板支持按全部/需求/Bug 筛选，并支持按 ID、标题、文档或负责人搜索；Bug 筛选下仍保留全部 9 个阶段列，且不展示冗余横向滚动提示文案。
- [ ] AC-005 工具栏提供负责人、优先级、Sprint 筛选和手动刷新图标按钮；筛选后看板对象范围与统计结果一致。
- [ ] AC-005A 点击刷新按钮后重新读取需求中心上下文并更新统计区和 9 阶段看板；刷新必须保留当前搜索、对象类型、负责人、优先级和 Sprint 筛选，刷新中显示 loading 语义且避免重复点击，刷新失败不得清空当前看板。
- [ ] AC-006 已进入迭代规划及后续阶段的卡片在右上角展示唯一 `sprint-xxx` 标签；未纳入迭代的对象不展示 Sprint 标签。
- [ ] AC-007 阶段主动作根据对象类型自动映射到对应 `req-*` 或 `bug-*` Skill；卡片按钮展示“生成需求 →”“加入迭代 →”“开始开发 →”等产品化文案，并保留命令映射追溯；缺少阶段必需文档时禁止流转并指出缺失项。
- [ ] AC-008 验收中对象仅当测试项和人工验收项全部完成时显示“完成 / 归档”入口。
- [ ] AC-009 页面不设置右侧内容区顶部全局导航栏，仅保留页面标题、统计区、工具栏和看板。
- [ ] AC-010 侧边栏支持展开 224px / 收起 72px；必须列出原型 8 个菜单：研发总览、Chat 工作台、需求中心、Spec、任务中心、Skill Center、Agent Center、知识中心；收起后保留图标、悬停提示和当前菜单高亮。
- [ ] AC-010A 侧边栏品牌区必须展示 MoonBox、`AI原生软件工厂` 副标题和版本徽标，前台 8 个菜单必须分组展示，需求中心 active 态必须使用金色左线；品牌区、导航密度、字体字号、图标尺寸、折叠按钮、收起态行为和用户菜单视觉层级必须与管理后台侧栏保持一致。
- [ ] AC-011 用户菜单入口文案为“切换空间”；Hover 后无需点击即可在一级菜单右侧展示空间列表。
- [ ] AC-012 从一级用户菜单移动到空间列表期间，一级用户菜单持续显示；空间列表具备短延时防误关闭。
- [ ] AC-013 空间列表平铺展示空间名称、中文角色、成员数、当前项勾选和创建或加入空间入口；不得展示标题、搜索框、组织分组或用户菜单摘要；空间项默认无独立卡片边框，hover 使用弱背景，selected 使用金色弱背景、左侧细线或勾选表达。
- [ ] AC-014 切换空间成功后，用户区空间名称和 `localStorage['moonbox.workspace']` 同步更新。
- [ ] AC-015 用户菜单提供“设置空间”入口，并打开作用于当前空间的居中分栏弹窗；弹窗宽度与视觉遵循原型 `min(1040px, calc(100vw - 80px))`、16px 圆角和投影。
- [ ] AC-016 空间设置弹窗左侧包含常规、成员与权限、Agent、Skill、集成、高级设置；右侧展示当前分组配置项。
- [ ] AC-017 常规配置支持空间名称、空间标识、空间描述和默认时区，提供取消、保存和成功反馈。
- [ ] AC-018 点击外部、关闭按钮或 Escape 可关闭空间切换浮层和空间设置弹窗；用户菜单也必须支持 click outside 关闭；关闭时不得保存未确认变更。
- [ ] AC-019 主题切换仅保留在用户菜单内，页面不得在 Sidebar 底部再出现独立主题行。
- [ ] AC-020 默认深色主题使用 MoonBox Platform Operations token；浅色主题切换后文字、面板、边框和交互态清晰可读。
- [ ] AC-021 9 列 Kanban Column Header 在页面纵向滚动时固定在页面标题区域下方，横向滚动时与对应列同步移动。
- [ ] AC-022 吸顶列头不得新增占位行、灰色空白、克隆表头或重复 9 行标题。
- [ ] AC-023 所有状态流转必须具备权限校验、前置条件校验、二次确认、幂等控制和审计记录。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 生成 Change 时，design.md MUST 写入 UI Skeleton，覆盖路由/页面壳、布局区域、组件插槽、状态容器、数据依赖、可测选择器和占位数据边界。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 实现阶段 MUST 在 1440px 桌面视口验收首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动、Hover 浮层和文本溢出，并记录截图或等价证据入口。
- [ ] AC-PROTOTYPE-004 `/opsx-archive` 前 MUST 完成 REQ 最终一致性检查，确认 requirement.md、acceptance.md、trace.md 与最终 Change 设计、实现证据和 1440px 验收结果一致。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md` — 预防 Sprint 002/003 复发类缺陷

- [ ] AC-XCUT-001 空间设置弹窗实现中不得让通用 `modal-card` 与专属宽度类并存，避免通用样式覆盖业务弹窗宽度。
- [ ] AC-XCUT-002 空间设置弹窗必须在浏览器 computed style 中验收最终宽度，确认宽度与原型设计一致。
- [ ] AC-XCUT-003 低视口下空间设置弹窗 body 必须可滚动，底部保存和取消操作必须可访问。
- [ ] AC-XCUT-004 弹窗遮罩不得吞掉内部滚动，也不得导致页面主体误滚动。
- [ ] AC-XCUT-005 必填字段、错误提示和底部操作区不得互相遮挡。

> 来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` — 带 prototype UI 需求门禁

- [ ] AC-XCUT-006 Change `tasks.md` 中 UI Skeleton 任务必须早于细节实现任务。
- [ ] AC-XCUT-007 视觉验收证据必须记录工具/命令、viewport、页面路径、截图或等价证据入口、结果摘要和例外说明。
- [ ] AC-XCUT-008 UI 返修后不得沿用旧截图或旧验收结论，必须重跑 1440px 验收并回填 REQ/Change 文档。
- [ ] AC-XCUT-009 主题开关必须提供唯一 `#themeSwitch` 选择器，空间切换浮层必须保留原型 fixed 位置和圆角阴影形态。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-frontend-requirement-center
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

