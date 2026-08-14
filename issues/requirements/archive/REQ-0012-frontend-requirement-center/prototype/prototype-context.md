# 需求中心看板 原型上下文工程 v4.0.5

## v4.0.5 组件增量

- `SpaceMenuItem`：文案“切换空间”，以 `mouseenter` 触发二级列表。
- `SpaceSwitcherPopover`：与一级用户菜单并列显示；通过 `scheduleSpacePopoverClose` / `cancelSpacePopoverClose` 实现 180ms Hover 安全区。
- `UserMenu`：展示空间列表时持续保留 `open` 状态。

## v4.0.4 组件与字段

- `SpaceSwitcherPopover`：账号摘要、搜索、组织分组、空间单选和创建/加入入口。
- `SpaceSettingsModal`：`SettingsNav + SettingsPanel` 左右分栏，配置当前空间。
- Workspace 字段：`name`、`slug`、`description`、`timezone`、`memberCount`、`role`、`selected`。
- 函数：`openSpacePopover`、`filterSpaces`、`selectSpace`、`openSpaceSettings`、`switchSettings`、`saveSpaceSettings`。

## 设计基线
- 产品：MoonBox
- 模块：P03 Requirement Center
- 画布：1440 × 900
- 主题：Moon Light
- 设计语言：东方器物感、编辑式排版、品牌靛蓝 + 唯一暖金强调、细线、近直角、无厚阴影
- 侧边栏：248px 展开 / 76px 收起；用户与主题位于底部；品牌版本号 `v1.3.0` 位于 MoonBox 右上角
- 页面不得创建右侧内容区的全局顶部导航栏，仅保留页面标题与局部动作栏

## 页面
- 名称：需求中心看板
- 文件：01-requirement-board.html
- 图片：prototype.png

## Domain Objects
Requirement, Bug, Capture, Trace, Review, SprintProposal, OpenSpec, Task, TestRun, ManualAcceptance, Archive

## 状态机
Capture Pool -> Planning -> Review Ready -> Approved -> Sprint Planning -> Ready for Dev -> In Development -> Acceptance -> Done

## Skill Mapping
req-capture / bug-capture
req-generate / bug-generate
req-review / bug-review
sprint-propose
req-opsx / bug-opsx
opsx-apply / sprint-apply

## 实现约束
HTML必须与 prototype.png 同源；不得使用占位 lorem ipsum；所有数据示例体现真实研发对象、文档与状态。

## V3 Component State

### UserMenu
- trigger: Sidebar.UserRow
- placement: sidebar-bottom / upward popover
- items:
  - current workspace
  - switch workspace
  - create workspace
  - personal profile
  - change password
  - logout
- close conditions: click outside / Esc / sidebar collapse / navigation complete
- permission: workspace:create controls “创建空间”

### CardUpdatedAt
- font-size: 9px
- color: secondary text
- semantic role: tertiary metadata

### SprintTag
- visible from Sprint Planning onward
- format: Sprint {number}
- visual: thin warm-gold border, transparent warm-gold fill
- source: current sprint relation


# V4 Patch Change

仅新增 Card Visual Enhancement：

- Requirement Card:
  border-left: #3F659A

- Bug Card:
  border-left: #B94A4A

No other component changes.

# V4.0.1 Patch Change

## SprintTag

- placement: `Card.CardTop` 右上角，与对象 ID 两端对齐
- format: `sprint-{threeDigitNumber}`，例如 `sprint-025`
- visibility: Sprint Planning 及后续阶段
- uniqueness: 每张卡片最多一个，元数据区不重复渲染

## KanbanColumnHeaderSticky

- target: 9 个 `.column-head`
- sticky boundary: 页面标题区域下沿，视口顶部偏移 `76px`
- implementation: 在既有横向滚动容器内使用同一 CSS 位移变量同步 9 个表头，不创建克隆表头、不新增占位层
- vertical behavior: 表头触达标题区域下沿后保持可见；到达看板底部时停止位移
- horizontal behavior: 表头保留在各自 `.column` 内，随 `.board-wrap` 横向滚动并与卡片列同步
- layout safety: 位移不参与文档流重排，不产生额外灰色空白或重复的 9 行文字

# V4.0.2 Platform Operations Visual Alignment

## Design Tokens

- default theme: dark
- background: `#0A0C1B`
- panel: `#12142B`
- secondary panel / sidebar: `#0E1023`
- primary text: `#E7E8F3`
- heading: `#E9EEFB`
- muted text: `#7C81A6`
- accent: `#CBA35C`
- border: `rgba(234,242,255,.10)`
- radius: `2px`

## Shared Framework

- Sidebar: 224px expanded / 72px collapsed
- BrandHeader: 72px
- PageHeader: 72px, sticky, translucent background with blur
- UserAvatar: 32px circle, gold-tinted fill and border
- VersionBadge: thin gold border
- ThemeSwitch: token-level dark/light toggle

## Component Mapping

- `Stats` → Platform Operations `Metric`
- `Toolbar control` → Platform Operations `Field / Button`
- `KanbanColumn` → Platform Operations `Panel + Panel2 Header`
- `RequirementCard / BugCard` → Platform Operations `Card`, with preserved semantic left border
- `SprintTag` → thin gold-outline status label

## Stable Behavior

- 9-column workflow, data examples and actions remain unchanged.
- `.column-head` stays inside its original `.column`; vertical movement continues through the shared CSS offset variable.
- `SprintTag` remains the second item of `.card-top` for cards in Sprint Planning and later stages.

# V4.0.3 Patch Change

## UserMenu.ThemeSwitch

- placement: `Sidebar.UserMenu`
- uniqueness: 页面仅保留一个 `#themeSwitch`
- behavior: dark/light token toggle，不改变业务状态

## OrganizationWorkspaceManager

- entry: `UserMenu > 组织与空间管理`
- container: 420px right drawer with modal mask
- fields: organization id/name, workspace id/name, member count, current-user role, selected state
- actions: organization filter, workspace search, workspace single-select, organization settings, workspace settings
- persistence: `localStorage['moonbox.workspace']`
- close conditions: mask click / close button / Esc / selection complete
- permission expectation: settings actions require corresponding organization/workspace management permissions

## Stable Behavior

- Board DOM, 9-column workflow, cards, SprintTag and sticky-header algorithm remain unchanged from v4.0.2.

## /req-complete 原型拆解

### 页面清单

| 页面/区域 | 原型文件 | 说明 |
|---|---|---|
| 需求中心看板 | `prototype.html` | 首版主页面，承载统计区、筛选工具栏、9 阶段 Kanban、用户菜单、空间切换和空间设置。 |
| 空间切换浮层 | `prototype.html#spacePopover` | 用户 Hover“切换空间”后展示的右侧浮层，用于多组织、多空间搜索和单选切换。 |
| 空间设置弹窗 | `prototype.html#spaceSettingsMask` | 当前空间设置弹窗，左侧分组导航，右侧设置面板。 |
| 视觉截图 | `prototype.png` | 1440 × 900 视觉基准，后续实现验收以该截图和 HTML 同源结构为准。 |

### 关键区域

- Sidebar：MoonBox 品牌、版本号、主导航、收起/展开控制、底部用户菜单入口。
- Page Header：页面英文点题、中文标题、局部动作按钮。
- Stats：全部对象、需求、Bug、当前阻塞四项指标。
- Toolbar：搜索、对象类型分段筛选、负责人/优先级/Sprint 筛选和横向滚动提示。
- Kanban Board：9 列生命周期阶段、吸顶列头、横向滚动、卡片主动作。
- Requirement/Bug Card：对象 ID、Sprint 标签、标题、优先级、文档产物、进度、更新时间和阶段动作。
- UserMenu：个人资料、密码修改、切换空间、空间设置、主题、退出登录。
- SpaceSwitcherPopover：账号摘要、搜索、组织分组、空间单选、创建或加入入口。
- SpaceSettingsModal：设置导航、常规表单、成员与权限、Agent、Skill、集成、高级设置、保存/取消。
- Toast：空间切换和空间设置保存后的 fixed 成功反馈。

### 组件层级

```text
RequirementCenterPage
  ├─ Sidebar
  │  ├─ BrandHeader
  │  ├─ Navigation
  │  └─ UserMenu
  │     ├─ SpaceMenuItem
  │     ├─ ThemeSwitch
  │     └─ LogoutItem
  ├─ PageHeader
  ├─ RequirementStats
  ├─ RequirementToolbar
  ├─ KanbanBoard
  │  └─ KanbanColumn × 9
  │     ├─ KanbanColumnHeader
  │     └─ RequirementCard | BugCard
  ├─ SpaceSwitcherPopover
  ├─ SpaceSettingsModal
  │  ├─ SettingsNav
  │  └─ SettingsPanel
  └─ FixedToast
```

### 状态矩阵

| 状态域 | 状态 | 触发 | 结果 |
|---|---|---|---|
| Sidebar | expanded / collapsed | 点击收起按钮 | 宽度在 224px 与 72px 切换；用户菜单关闭。 |
| Theme | dark / light | 用户菜单内主题开关 | 页面 token 即时切换，不改变业务状态。 |
| UserMenu | open / closed | 点击用户区、点击外部、Esc、侧栏收起 | 菜单开闭，并控制空间浮层生命周期。 |
| SpaceSwitcherPopover | open / scheduled-close / closed | Hover“切换空间”、离开菜单、进入浮层 | 180ms 安全区内保持可用，防止误关闭。 |
| Workspace | selected / unselected | 点击空间项 | 单选更新，当前空间摘要与本地存储同步。 |
| SpaceSettingsModal | open / closed | 点击空间设置、遮罩、关闭按钮、保存成功 | 展示或关闭当前空间设置。 |
| SettingsPanel | general / members / agents / skills / integrations / danger | 点击左侧设置导航 | 右侧展示对应配置区域。 |
| KanbanHeader | normal / sticky | 页面纵向滚动 | 列头吸附在标题区域下方并随横向滚动对齐。 |

### 交互触发

- `toggleSidebar()`：切换侧边栏宽度并关闭用户菜单。
- `toggleUserMenu(event)`：打开或关闭一级用户菜单。
- `openSpacePopover()`：Hover“切换空间”后打开空间列表，并保持一级用户菜单 `open`。
- `scheduleSpacePopoverClose()` / `cancelSpacePopoverClose()`：实现 180ms Hover 安全区。
- `filterSpaces()`：按输入关键字过滤空间项。
- `selectSpace(item)`：单选空间、更新摘要、写入 `localStorage['moonbox.workspace']`、展示 toast。
- `openSpaceSettings(event)` / `closeSpaceSettings()`：打开或关闭空间设置弹窗。
- `switchSettings(tab)`：切换空间设置右侧面板。
- `saveSpaceSettings()`：保存空间设置并展示 fixed toast。

### 数据依赖

- Requirement/Bug：`id`、`type`、`title`、`priority`、`owner`、`source`、`stage`、`documents`、`updatedAt`、`blocked`、`sprintId`、`taskProgress`、`testProgress`、`manualAcceptanceCount`。
- Stage：阶段 ID、标题、说明、计数、允许动作、必需文档。
- Workspace：`organizationId`、`organizationName`、`workspaceId`、`name`、`slug`、`description`、`timezone`、`memberCount`、`role`、`selected`。
- User：显示名称、账号、头像/缩写、当前组织、当前空间、权限集合。
- Theme：当前主题、可用 token、用户本地偏好。
- Audit/Command：阶段流转动作、触发者、目标对象、幂等键、审计摘要。

### 响应式断点

- 1440 × 900：主验收画布；Sidebar 展开 224px，主内容显示统计、工具栏和横向滚动看板。
- 1280px 以上：保持桌面工作台密度，Kanban 使用横向滚动，不压缩卡片到不可读。
- 1024px 至 1279px：允许 Sidebar 收起到 72px；工具栏可换行，但搜索、类型筛选和主要动作不得重叠。
- 768px 至 1023px：看板仍以横向滚动为主；用户菜单和空间浮层不得超出视口。
- 小于 768px：首版可提示使用桌面视口或降级为列表视图；不得出现文字溢出、按钮遮挡或不可关闭弹窗。

### 1440px 验收焦点

- 首屏结构：Sidebar、Page Header、Stats、Toolbar、Kanban 首列在 1440px 视口下清晰可见。
- 主题：默认深色主题和浅色主题均符合 MoonBox token，金色强调唯一且不过量。
- 字号：卡片更新时间为 9px 弱层级，不与标题、标签或动作竞争。
- 对齐：9 列表头横向滚动后仍与卡片列对齐。
- 浮层：Hover“切换空间”后一级菜单和空间列表同时可见，移动鼠标不误关闭。
- 弹窗：空间设置弹窗宽度、滚动、底部操作和遮罩行为符合原型。
- Toast：fixed toast 不影响页面布局，不造成看板或工具栏 layout shift。
- 文本：导航、标题、卡片、标签、按钮和弹窗字段不得截断到不可理解，也不得互相遮挡。
