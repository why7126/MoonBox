---
change_id: add-frontend-requirement-center
status: proposed
source_requirement: REQ-0012-frontend-requirement-center
source_sprint: sprint-002
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-12 10:00:00
---

# 设计说明

## D1 UI 策略

采用“Prototype Port + MoonBox Design System Token”策略：

- 以 `prototype/prototype.html` 为 HTML 结构事实源，优先复刻页面区域、组件层级、状态触发和关键交互。
- 以 `prototype/prototype.png` 为 1440px 视觉基准，验收首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出。
- 以 `prototype/prototype-context.md` 为组件、状态、数据依赖和响应式断点事实源。
- 使用 MoonBox 深色默认主题 token：`#0A0C1B`、`#12142B`、`#0E1023`、`#CBA35C`、细线、近直角和克制层级。
- 不在右侧内容区新增全局顶部导航栏；页面只保留标题区、统计区、工具栏和看板。
- 实现阶段先落 UI Skeleton，再做数据接入和交互细节；任何原型口径变化必须回填 REQ 与 Change 文档。

## Conflict Resolution

| 来源 | 优先级 | 结论 |
|---|---:|---|
| `prototype/prototype.html` | 1 | 作为首要结构输入，定义 Sidebar、Page Header、Stats、Toolbar、Kanban、UserMenu、SpacePopover、SpaceSettingsModal 和 Toast。 |
| `prototype/prototype.png` | 2 | 作为 1440 × 900 视觉基准，约束首屏布局、暗色主题、金色强调、卡片层级和空间设置弹窗。 |
| `prototype/prototype-context.md` | 3 | 作为原型拆解事实源，承接页面清单、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。 |
| `acceptance.md` | 4 | 作为功能 AC、AC-PROTOTYPE 和 AC-XCUT 事实源。 |
| `rules/ui-design.md` | 5 | 作为 MoonBox 视觉风格与 Prototype-driven UI Gate 事实源。 |
| `openspec/specs/*` | 6 | 当前无既有需求中心 spec，新增 `web-catalog-requirement-center` 能力，不修改既有 homepage/login spec。 |

当前无阻断冲突。最终验收以 Change design、delta spec、REQ acceptance、1440px 视觉证据和 REQ 最终一致性回填共同为准。

## UI Skeleton

```text
RequirementCenterPage
  ├─ FrontendShell
  │  ├─ Sidebar
  │  │  ├─ BrandHeader
  │  │  ├─ Navigation
  │  │  └─ SidebarUserArea
  │  │     └─ UserMenu
  │  │        ├─ ProfileItem
  │  │        ├─ PasswordItem
  │  │        ├─ SpaceMenuItem
  │  │        ├─ SpaceSettingsItem
  │  │        ├─ ThemeSwitch
  │  │        └─ LogoutItem
  │  └─ MainContent
  │     ├─ PageHeader
  │     ├─ RequirementStats
  │     ├─ RequirementToolbar
  │     └─ KanbanBoard
  │        └─ KanbanColumn × 9
  │           ├─ KanbanColumnHeader
  │           └─ RequirementCard | BugCard
  ├─ SpaceSwitcherPopover
  ├─ SpaceSettingsModal
  │  ├─ SettingsNav
  │  └─ SettingsPanel
  └─ FixedToast
```

### 页面结构与区域边界

- Sidebar 负责品牌、导航、收起展开和用户菜单入口；不得承载看板业务状态。
- MainContent 负责标题、统计、工具栏和看板滚动容器；不得新增右侧内容区全局顶部导航栏。
- RequirementToolbar 负责搜索和筛选状态，筛选结果驱动统计与看板卡片范围。
- KanbanBoard 负责 9 阶段横向滚动、列头吸顶和卡片渲染；列头不得通过克隆 DOM 实现。
- UserMenu 负责个人资料、密码修改、切换空间、空间设置、主题和退出登录入口。
- SpaceSwitcherPopover 负责组织分组、搜索、单选和当前空间摘要更新。
- SpaceSettingsModal 负责当前空间配置草稿、设置分组切换、字段校验、保存/取消和低视口滚动。

### 状态容器

| 状态域 | 状态 | 说明 |
|---|---|---|
| `sidebarState` | `expanded` / `collapsed` | 控制 Sidebar 224px / 72px 形态，收起时关闭用户菜单。 |
| `themeState` | `dark` / `light` | 用户菜单内切换主题 token，不改变业务状态。 |
| `filterState` | search/type/owner/priority/sprint | 驱动统计区和 Kanban 卡片范围。 |
| `boardScrollState` | horizontal / sticky-offset | 控制 9 列横向滚动和列头吸顶对齐。 |
| `userMenuState` | open / closed | 控制一级用户菜单生命周期。 |
| `spacePopoverState` | open / scheduled-close / closed | 控制 180ms Hover 安全区和空间列表展示。 |
| `workspaceState` | selected workspace | 控制当前组织/空间、用户区摘要和本地最近选择。 |
| `settingsModalState` | open / closed / saving / saved / failed | 控制空间设置弹窗、保存反馈和错误恢复。 |

### 数据依赖

- Requirement/Bug：`id`、`type`、`title`、`priority`、`owner`、`source`、`stage`、`documents`、`updatedAt`、`blocked`、`sprintId`、`taskProgress`、`testProgress`、`manualAcceptanceCount`。
- Stage：阶段 ID、标题、说明、计数、允许动作、必需文档。
- Workspace：`organizationId`、`organizationName`、`workspaceId`、`name`、`slug`、`description`、`timezone`、`memberCount`、`role`、`selected`。
- User：显示名称、账号、头像/缩写、当前组织、当前空间、权限集合。
- Command Mapping：对象类型、当前阶段、目标命令、前置文档、权限和审计摘要。

### 可测选择器

- 页面标题：role heading，文本“需求研发流转看板”。
- 导航项：文本“需求中心”且当前态高亮。
- 看板列：data-stage 或可访问标题，覆盖 9 个阶段。
- 卡片：data-issue-id，区分 `REQ-*` / `BUG-*`。
- 类型筛选：按钮/分段控件“全部”“需求”“Bug”。
- 用户菜单：role menu，空间入口文本“切换空间”。
- 空间浮层：role dialog，label “切换组织和空间”。
- 空间设置：role dialog，标题“空间设置”。
- 主题开关：role switch。
- Toast：固定反馈区域。

### 1440px 验收焦点

- Sidebar、Page Header、Stats、Toolbar、Kanban 首列在 1440px 视口下清晰可见。
- 默认深色主题符合 MoonBox token，浅色主题切换后文字、面板、边框和交互态清晰可读。
- Requirement/Bug 卡片左侧语义边框、`sprint-xxx` 标签、9px 更新时间和阶段动作不重叠。
- 9 列表头纵向吸顶后与横向滚动列保持水平对齐，不出现克隆表头或灰色空白。
- 9 列表头纵向吸顶时必须具备不透明遮罩和高于卡片的 stacking 层，卡片上滑不得在列头顶部区域透出。
- Hover“切换空间”后一级用户菜单和空间列表同时可见，移动鼠标不误关闭。
- 空间设置弹窗宽度、滚动、底部操作、遮罩和字段提示符合原型。
- fixed toast 不造成 layout shift。

## Knowledge Gate

引用：

- `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
- `docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- `docs/knowledge-base/retrospectives/sprint-001-retrospective.md`

落地要求：

- `tasks.md` 必须包含 UI Skeleton 先行任务，且早于细节实现。
- `tasks.md` 必须包含空间设置弹窗 computed width、低视口滚动、遮罩滚动和底部操作可访问验收。
- `tasks.md` 必须包含 1440px 视觉验收、截图或等价证据入口、REQ 最终一致性回填。

## 验收返修决策

2026-08-10 14:08:00 根据原型差异验收反馈，设计口径明确为继续贴近 `prototype.html`：

- 空间设置弹窗采用原型宽度 `min(1040px, calc(100vw - 80px))`、高度 `min(720px, calc(100vh - 64px))`、16px 圆角和明显投影；不得退化为窄版 900px 近直角弹窗。
- 空间切换浮层采用 fixed 形态，位置对齐原型 `left: 208px; bottom: 72px`，保留圆角和阴影。
- 卡片主动作展示产品化文案，同时在实现中保留命令映射追溯。
- 用户菜单必须支持 click outside 关闭；主题开关必须提供唯一 `#themeSwitch` 选择器。

2026-08-10 14:21:00 第二轮 Sidebar 返修继续以 `prototype.html` 为准，同时借鉴管理后台侧栏的图标尺寸和操作密度：

- 前台 Sidebar 必须列出原型 8 个菜单：研发总览、Chat 工作台、需求中心、Spec、任务中心、Skill Center、Agent Center、知识中心。
- 需求中心保持当前高亮，active 态必须显示金色左线。
- 品牌区必须包含 MoonBox、`AI原生软件工厂` 副标题和 `v4.0.5` 版本徽标。
- 折叠按钮位于品牌区右侧，折叠宽度保持 `72px`，折叠后隐藏菜单 label 但保留图标和 title。

2026-08-10 14:36:00 第三轮视觉返修以前后台截图为依据，将前台 Shell 向管理后台侧栏收敛：

- 品牌区复用真实 MoonBox 产品图标，保持 `72px` 高度、后台式标题层级、右上版本徽标与轻量折叠按钮；前台副标题使用中文文案 `AI原生软件工厂`。
- 导航保持原型 8 个菜单，但采用后台式 `40px` 行高、`14px` 字号、`16px` lucide 图标、低调 active 背景和 `2px × 18px` 金色左线。
- 用户区采用后台式 `46px` 触发器、头像/用户名/空间副标题/chevron 结构；用户菜单采用轻量边框、`6px` 内边距、`14px` 菜单字重和 `14px` 图标。
- 主内容的标题、筛选控件与卡片字号下调到后台式管理界面密度，避免原型展示稿的大字号压迫感。

2026-08-10 16:20:00 第四轮看板返修以 `prototype.html` 的 9 阶段横向流程泳道为准：

- 列头恢复原型结构：左侧展示阶段标题和命令副标题，右侧展示两位数 count，例如 `00`、`01`。
- 9 阶段副标题使用原型命令语义，包括 `Capture / req-capture / bug-capture`、`req-generate / bug-generate`、`req-opsx / bug-opsx`、`opsx-apply / sprint-apply` 等。
- 工具栏不展示“按住 Shift 横向滚动 · 共 9 个阶段”等冗余提示；9 阶段流程由横向列结构、列头和两位数 count 自身表达。
- 看板列宽、列间距、卡片高度和空列高度向原型紧凑横向看板收敛；Bug 筛选时仍渲染全部 9 列，用两位数 count 表达阶段对象数量，避免用户误判阶段缺失。

2026-08-10 16:35:00 第五轮卡片与表头返修继续以 `prototype.html` 为准：

- 卡片恢复原型信息结构：`card-top` 仅强调小号 italic ID 与可选 Sprint tag，主体标题后展示单 pill meta，例如 `P1 · 产品团队`，不得拆成多个并列 token。
- `docs`、`progress` 和阻断信息使用上边框分隔区，承接原型 `.docs` 的信息层级。
- 阶段动作按钮使用无边框 mini action，更新时间保持 9px 弱层级。
- 阶段列增加顶部弱金线，`.rc-column-head` 的 sticky top 必须为 `0`，使表头贴近列顶部边框，避免列头与顶部边框之间出现大空隙。

2026-08-10 16:53:30 第六轮 Sidebar 结构性交互返修以前后台截图和后台实现为依据，将前台侧栏改为后台同构、前台内容差异化：

- 前台 Sidebar 使用后台式字体体系：页面根与导航/用户菜单为 `13px`，分组标题为 `10px`，品牌标题使用紧凑 serif 字体，避免与版本徽标冲突。
- 前台 8 个菜单按信息架构分为 `WORKSPACE` 与 `CAPABILITIES` 两组；collapsed 状态隐藏分组标题和菜单 label，但保留图标、title 和当前高亮。
- 折叠状态采用后台式 CSS 规则：品牌区居中、折叠按钮外凸到侧栏边缘、导航和用户触发器居中。
- 用户菜单保留前台业务项，但按钮密度、图标尺寸和 theme switch 视觉向后台用户菜单收敛；主题状态用滑块表达，而不是仅用文字表达。

2026-08-10 17:03:54 第七轮细节返修处理品牌区、折叠按钮层级和看板提示文案：

- 品牌区曾尝试使用稳定 grid 占位承载产品图标、品牌文案、版本徽标和折叠按钮，但该方案已在 2026-08-10 17:12:10 撤销，原因是偏离后台管理侧栏的视觉节奏。
- collapsed 状态下展开/收起按钮必须高于右侧内容区域可见且可点击，使用明确 `z-index`、背景和轻量阴影表达边界。
- 取消原型中的横向滚动提示文案，避免工具栏信息噪音；保留 9 阶段列、两位数 count 和横向滚动容器作为流程表达。

2026-08-10 17:12:10 第八轮返修以后台管理侧栏为准，恢复前台品牌区结构：

- `.rc-brand` 必须保持后台同构的 `flex` 品牌区，使用 `position: relative`、`align-items: center`、`gap: 12px`、`height: 72px` 和 `padding: 0 18px`。
- `.rc-version-badge` 恢复 absolute 定位，靠右贴近后台模式；前台可使用 `right: 36px` 给 `MoonBox` 留出间距，并确保不碰折叠按钮。
- `.rc-collapse` 恢复后台式 absolute 定位，展开态 `right: 10px`，collapsed 态 `right: -13px`，并保留较高 `z-index` 防止被右侧内容遮挡。
- 前台副标题 `AI原生软件工厂` 使用固定宽度省略，避免为了完整显示副标题而改变后台品牌区结构。

2026-08-10 17:26:59 第九轮返修继续以后台管理侧栏为准，收敛展开/收起按钮形态：

- 前台 Sidebar 展开/收起按钮使用文本 `‹` / `›`，不再使用 lucide chevron，确保与后台按钮字形和重心一致。
- 展开态保持后台式透明轻量按钮：`top: 24px`、`right: 10px`、`width: 24px`、无边框、无背景、无阴影。
- 收起态复刻后台外凸控制柄：`right: -13px`、`1px` 边框、侧栏背景、无阴影；保留较高 `z-index` 只用于避免被右侧内容遮挡。

2026-08-10 17:47:20 第十轮返修继续收敛 collapsed 控制柄到后台实现细节：

- `.rc-collapse` 必须逐项对齐 `.admin-collapse` 的按钮覆盖规则：`min-height: 24px !important`、`border: 0 !important`、`background: transparent !important`、`text-align: center !important`。
- collapsed 态必须使用 `border: 1px solid var(--rc-border) !important` 与 `background: var(--rc-panel-2) !important`，避免被通用按钮规则或主题规则冲掉。
- 前台侧栏因为使用 sticky/grid 组合，必须给 `.rc-sidebar` 明确 stacking 层，确保外凸到内容区边界的控制柄不被 `.rc-page-header` 覆盖；验收以 `buttonVisibleAtCenter=true` 为准。

2026-08-10 17:54:58 第十一轮返修以前台当前良好效果为准，反向修正后台 collapsed 控制柄高度：

- 后台 `.admin-collapse` 不得继承 `.admin-sidebar button` 的 `height: 40px` 和 `padding: 0 12px`，必须显式使用 `width: 24px`、`height: 24px !important`、`padding: 0 !important`。
- 前台 `.rc-collapse` 同步显式声明 `height: 24px !important` 与 `padding: 0 !important`，避免浏览器默认 button padding 造成 computed style 差异。
- 前后台 collapsed 控制柄验收以 computed style 一致为准：`24px × 24px`、`padding=0`、`right=-13px`、`top=24px`、1px 边框、侧栏背景、无阴影、中心点命中按钮。

2026-08-11 17:45:07 第十二轮看板滚动层级返修以当前原型驱动 UI 验收标准为准：

- 看板列头 `.rc-column-head` 必须保持 `position: sticky`、`top: 0` 和不透明 `var(--rc-panel-2)` 背景，且 `z-index` 高于卡片。
- 列头使用隔离 stacking context 和 `::before` 向上延伸 `18px` 作为遮罩，覆盖卡片上滑经过列头顶部边界时的透出区域。
- 遮罩不得拦截鼠标或键盘交互，`pointer-events` 必须为 `none`。

2026-08-11 22:00:52 第十三轮空间二级浮层视觉返修以前台用户菜单轻量层级为准：

- 空间二级浮层外层已经提供边框、背景和阴影，空间项不得再使用独立卡片边框。
- 空间项默认使用无边框透明列表行，hover 使用弱背景，selected 使用金色弱背景、右侧勾选和 2px 左侧金线表达当前态。
- “创建或加入空间”是明确动作按钮，继续保留独立边框，与空间列表行区分。

2026-08-12 10:00:00 第十四轮工具栏刷新能力返修以 9 阶段实时感知为准：

- 需求中心工具栏提供手动刷新图标按钮，使用 `RefreshCw`，作为辅助动作放在筛选控件末尾，不抢占“新建 Capture”主动作层级。
- 手动刷新必须保留当前搜索、类型、负责人、优先级和 Sprint 筛选；刷新成功只替换最新上下文数据，不重置筛选。
- 手动刷新使用独立 `isRefreshingContext` 状态，不触发首屏 loading，也不遮挡已有看板。
- 刷新失败不得清空当前看板；仅通过轻量 toast 提示“刷新失败，已保留当前看板”。
- 刷新按钮验收以 1440px 截图和 computed style 为准：`38px × 38px`、1px 边框、刷新中禁用、`aria-busy=true`、图标旋转。

2026-08-10 18:13:12 第十二轮返修收敛前台用户菜单交互语义：

- 用户菜单位于侧栏底部并向上弹出，触发箭头必须使用上下方向语义：关闭态 `⌃` 表示向上展开，打开态 `⌄` 表示可收起，不再使用向右 chevron。
- 前台用户菜单按账号、空间、偏好、会话四组轻量分隔；分组不显示额外标题，依靠顺序和分隔线降低视觉负担。
- 退出登录必须单独位于会话组，并使用与后台 `.admin-user-menu .logout` 一致的危险色 `#D47476`。

2026-08-10 18:47:47 第十三轮返修继续轻量化空间二级浮层：

- 账号组入口使用“进入后台”，不使用“进入管理后台”，保持前台/后台产品语言一致。
- “切换空间”是唯一触发二级浮层的菜单项，右侧必须展示 `>`；hover 到用户菜单其他项时立即隐藏空间浮层，仅“切换空间”到右侧空间浮层之间保留 180ms 安全区。
- 空间浮层不展示标题、搜索框和组织分组；当前原型数据空间数量少且没有真实分组字段，直接平铺空间列表。
- 空间列表项只展示空间名称、中文角色和成员数；不展示空间状态，不提供更多/退出空间操作，避免扩大到权限、确认流和成员关系变更边界。
- 底部动作合并为“创建或加入空间”；“设置空间”仅在当前空间角色为“拥有者”或“管理员”时展示。

2026-08-10 18:59:42 第十四轮返修处理用户菜单 summary、浮层可读性和前后台返回入口：

- 前台用户菜单打开后不再展示顶部 summary；当前用户和当前空间已由侧栏底部触发器承载，菜单内不得重复显示用户、空间组织或 `MoonBox Lab` 等已废弃分组信息。
- 空间二级浮层中的空间项必须显式声明暗色主题按钮样式，避免浏览器默认 button 样式导致浅底黑字；默认、hover、selected 和底部 action 都必须清晰可读。
- 后台用户菜单与前台“进入后台”保持对称，新增“返回前台”入口，点击进入 `/requirements`。

2026-08-10 19:19:46 第十五轮返修统一前后台用户菜单浮层层级与分组：

- 前后台用户菜单不得直接复用侧边栏背景色，应使用菜单专用 surface token，使浮层背景比侧边栏亮一档，并通过更清晰边框、克制阴影和金色透明 hover 态表达悬浮层级。
- 前台空间二级浮层与一级用户菜单使用同一浮层表面体系；空间项使用 raised surface，selected 态保留弱金色背景与边框。
- 后台用户菜单按账号、导航、偏好、会话分组，与前台账号、空间、偏好、会话形成一致信息层级；退出登录继续单独处于会话组，并保持前后台危险色一致。

2026-08-10 19:56:19 第十六轮返修统一用户菜单权限与图标语义：

- “进入后台”是用户级后台访问权限，不是空间拥有者/管理员能力；前台仅在当前用户具备 `canAccessAdmin` 时展示该入口。
- 前后台相同功能必须使用相同图标：个人资料 `UserRound`、修改密码 `KeyRound`、进入后台/返回前台 `LayoutDashboard`、界面主题 `SunMoon`、退出登录 `LogOut`。
- 不同功能不得复用同一图标；前台空间相关功能继续使用 `Users` 与 `Settings` 区分切换空间和设置空间。
