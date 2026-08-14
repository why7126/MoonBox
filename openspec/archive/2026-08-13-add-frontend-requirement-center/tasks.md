---
change_id: add-frontend-requirement-center
status: applied
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-13 22:45:00
---

# Tasks

## 1. UI Skeleton 与原型承接

- [x] 1.1 确认 REQ-0012 `prototype/prototype.html`、`prototype/prototype.png` 和 `prototype/prototype-context.md` 为设计事实源。
- [x] 1.2 建立 `RequirementCenterPage` UI Skeleton，包含 FrontendShell、Sidebar、PageHeader、RequirementStats、RequirementToolbar、KanbanBoard、SpaceSwitcherPopover、SpaceSettingsModal 和 FixedToast。
- [x] 1.3 建立 9 阶段 Kanban Column Skeleton，覆盖采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成。
- [x] 1.4 建立 RequirementCard / BugCard Skeleton，覆盖 ID、标题、优先级、阶段产物、更新时间、阻塞状态、进度、Sprint 标签和阶段主动作。
- [x] 1.5 建立状态容器：sidebarState、themeState、filterState、boardScrollState、userMenuState、spacePopoverState、workspaceState、settingsModalState。
- [x] 1.6 标注可测选择器，覆盖页面标题、9 个阶段列、卡片、筛选控件、用户菜单、空间浮层、空间设置弹窗、主题开关和 toast。

## 2. 前台需求中心页面实现

- [x] 2.1 新增或接入前台需求中心路由，需求中心导航项高亮。
- [x] 2.2 实现 MoonBox 前台 Sidebar 展开 224px / 收起 72px，收起后保留图标、悬停提示和当前菜单高亮。
- [x] 2.3 实现页面标题区、统计区、搜索、全部/需求/Bug 分段筛选、负责人/优先级/Sprint 筛选。
- [x] 2.4 实现 9 阶段横向滚动看板，列头在纵向滚动时吸顶并保持横向对齐。
- [x] 2.5 实现 Requirement/Bug 卡片视觉差异、唯一 `sprint-xxx` 标签、9px 更新时间和阶段主动作。
- [x] 2.6 实现阶段文档缺失阻断提示和验收中归档入口门禁。

## 3. 用户菜单、空间切换与空间设置

- [x] 3.1 实现用户菜单入口，包含个人资料、密码修改、切换空间、空间设置、主题和退出登录。
- [x] 3.2 将主题切换仅保留在用户菜单内，移除 Sidebar 底部独立主题入口。
- [x] 3.3 实现 Hover“切换空间”打开右侧 SpaceSwitcherPopover，无需点击。
- [x] 3.4 实现一级用户菜单与空间列表之间 180ms Hover 安全区，移动到空间列表期间一级菜单持续显示。
- [x] 3.5 实现空间搜索、组织分组、空间单选、当前项勾选、创建/加入入口和本地最近选择保存。
- [x] 3.6 实现 SpaceSettingsModal 分栏结构，左侧常规、成员与权限、Agent、Skill、集成、高级设置，右侧展示当前配置面板。
- [x] 3.7 实现常规设置字段：空间名称、空间标识、空间描述、默认时区，以及取消、保存、成功 toast。

## 4. 横切验收与 UI 质量

- [x] 4.1 执行空间设置弹窗 admin-modal 横切验收：不得让通用 `modal-card` 与专属宽度类并存。
- [x] 4.2 在浏览器 computed style 中验收空间设置弹窗最终宽度与原型一致。
- [x] 4.3 验收低视口下弹窗 body 可滚动，底部保存/取消操作可访问。
- [x] 4.4 验收弹窗遮罩不吞掉内部滚动，也不导致页面主体误滚动。
- [x] 4.5 验收 fixed toast 不造成看板、工具栏或弹窗 layout shift。
- [x] 4.6 执行 1440px 桌面视觉验收，记录截图或等价证据入口。
- [x] 4.7 视觉验收必须覆盖首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动、Hover 浮层和文本溢出。

## 5. 测试

- [x] 5.1 前端测试覆盖需求中心页面渲染、9 阶段列、Requirement/Bug 卡片、筛选和搜索。
- [x] 5.2 前端测试覆盖阶段主动作映射和验收中归档入口门禁。
- [x] 5.3 前端测试覆盖 Sidebar 展开/收起、主题切换和需求中心导航高亮。
- [x] 5.4 前端测试覆盖 Hover“切换空间”、180ms 安全区、空间搜索、空间单选和当前空间摘要更新。
- [x] 5.5 前端测试覆盖空间设置弹窗分组切换、保存、取消、关闭和 toast。
- [x] 5.6 如引入 API 或数据契约，补充对应 API 文档、客户端封装和测试；否则在 trace 中记录本 Change 不引入后端/API/DB 变更。

## 6. 文档、追溯与归档准备

- [x] 6.1 回填 Change trace 的 UI Skeleton、1440px 视觉验收状态和证据入口。
- [x] 6.2 如实现改变 REQ-0012 prototype 意图，回填 REQ `requirement.md`、`acceptance.md` 和 `trace.md`。
- [x] 6.3 更新 sprint-002 acceptance-report 中 REQ-0012 验收证据。
- [x] 6.4 归档前确认 REQ-0012 最终一致性：REQ 文档、Change design、实现证据和 1440px 验收结果一致。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-10 14:08:00 | 当前实现与原型存在差异：空间设置弹窗宽度与视觉、空间浮层形态、卡片动作命令直出、用户菜单缺 click outside 关闭、缺唯一 `#themeSwitch`。 | 已将空间设置弹窗恢复为 `1040px` 原型宽度、16px 圆角和阴影；空间浮层恢复 fixed `left:208px; bottom:72px`；卡片动作改为产品化文案并用 `title` 保留命令映射；补充 click outside 关闭；主题开关补唯一 `id="themeSwitch"`。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 与 `1440x640` 返修视觉验收通过。 |
| 2026-08-10 14:21:00 | 前台 Sidebar 未列出原型全部菜单，整体效果与原型差异大，且与管理后台侧栏质感不一致。 | 已补齐原型 8 个菜单：研发总览、Chat 工作台、需求中心、Spec、任务中心、Skill Center、Agent Center、知识中心；恢复品牌副标题、版本徽标、active 金色左线和品牌区折叠按钮；统一 16px lucide 图标、导航密度与折叠 72px 行为。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` Sidebar 展开/收起验收通过。 |
| 2026-08-10 14:36:00 | 用户基于前后台截图反馈：前台与管理后台在 Sidebar、整体字体大小、用户菜单视觉层级上仍差异明显。 | 已将前台 Sidebar 收敛到后台式品牌结构、真实 MoonBox 图标、72px 品牌高、224px/72px 宽度、40px 菜单行高、14px 菜单字体、16px 图标、金色 active 左线、品牌区折叠按钮、46px 用户触发器、chevron 和 6px 用户菜单浮层；保留前台 8 个菜单与需求中心高亮。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` Shell 展开、用户菜单和折叠态验收通过。 |
| 2026-08-10 16:20:00 | 9 个阶段看板实现与原型效果差异较大：列头结构、命令副标题、两位数 count、列宽/间距/卡片密度和 Bug 筛选空列表现不一致。 | 已恢复原型式列头：左侧标题与命令副标题、右侧两位数 count；将列宽收敛到 `258px`、卡片最小高度收敛到 `132px`、空列高度降低；Bug 筛选下仍保留 9 列与两位数阶段计数。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 全部筛选与 Bug 筛选看板验收通过。 |
| 2026-08-10 16:35:00 | 9 阶段卡片与产品原型差异明显：卡片信息拆分过重，缺单 pill meta 与 docs 分隔区，mini action 有边框；阶段表头没有贴近列顶部边框。 | 已恢复原型卡片信息结构：italic 小号 ID、单 pill meta、docs/progress/blocked 分隔区、无边框 mini action 和 9px 更新时间；阶段列增加顶部弱金线，表头 sticky top 改为 `0` 并将 gap 降到列顶线本身。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 卡片与表头原型对齐验收通过。 |
| 2026-08-10 16:53:30 | 前台 Sidebar 与后台侧栏在顶部品牌区、分组、字体、折叠交互和用户菜单视觉上仍存在结构性差异；副标题文案需改为“AI原生软件工厂”。 | 已将前台 Sidebar 字体 token 收敛到后台 13px 体系；品牌区保留完整 `MoonBox`、`AI原生软件工厂` 与 `v4.0.5`；导航增加 `WORKSPACE` / `CAPABILITIES` 分组；collapsed 状态采用后台式隐藏规则与外凸折叠按钮；用户菜单按钮密度与 theme switch 视觉对齐后台。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` Sidebar 展开、用户菜单和折叠态结构验收通过。 |
| 2026-08-10 17:03:54 | 前台品牌区版本号与 MoonBox/AI原生软件工厂靠得太近并出现重合；收起态展开/收起按钮被右侧内容遮挡；“按住 Shift 横向滚动 · 共 9 个阶段”提示冗余。 | 已将品牌区改为稳定 grid 占位，版本徽标不再绝对覆盖品牌文案；collapsed 折叠按钮提升 `z-index` 并增加背景/阴影；移除横向滚动提示文案和样式。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 品牌不重合、折叠按钮可点击和提示移除验收通过。 |
| 2026-08-10 17:12:10 | 上一轮 grid 品牌区虽然解决局部重合，但偏离后台管理侧栏视觉节奏，整体效果变差。 | 已撤销 grid 品牌区，恢复后台式 flex 品牌区、absolute 版本徽标与折叠按钮定位；副标题 `AI原生软件工厂` 固定宽度省略；保留 collapsed 按钮 `z-index` 防遮挡；继续移除横向滚动提示。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 后台同构品牌区和收起态验收通过。 |
| 2026-08-10 17:26:59 | 展开/收起按钮与后台管理仍有差异：前台使用 lucide chevron，收起态有阴影，形态不像后台外凸控制柄。 | 已将前台 Sidebar 展开/收起按钮改为后台一致的文本 `‹` / `›`；展开态保持透明轻量按钮；收起态保留外凸 1px 边框和背景，移除阴影，保留 `z-index` 防遮挡。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 展开/收起按钮后台同构验收通过。 |
| 2026-08-10 17:47:20 | 展开态按钮样式已一致，但收起态仍与后台管理不同，且需确认不会被右侧内容区域覆盖。 | 已逐项复刻 `admin-collapse` 的尺寸、`text-align`、`border/background !important` 覆盖规则；为 sticky 前台侧栏补明确 stacking 层，使 collapsed 外凸控制柄完整露出并命中按钮中心点。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 展开/收起后台同构复验通过，collapsed `buttonVisibleAtCenter=true`。 |
| 2026-08-10 17:54:58 | 前台效果已满足预期，但后台 collapsed 控制柄高度被 `.admin-sidebar button` 的 `40px` 通用按钮规则撑高，导致前后台收起态按钮高度不一致。 | 已让后台 `.admin-collapse` 显式脱离通用按钮高度和 padding，并同步让前台 `.rc-collapse` 显式使用 `24px × 24px`、`padding: 0`，确保前后台 collapsed 控制柄尺寸一致。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 前后台 collapsed 控制柄高度、padding 和点击中心点一致。 |
| 2026-08-10 18:13:12 | 前台用户菜单与后台/交互语义仍有差异：底部弹出菜单不应使用向右箭头；菜单项需要轻量分组；退出登录应单独成组并使用后台一致危险色。 | 已将用户触发箭头改为关闭态 `⌃`、打开态 `⌄`；下拉菜单按账号、空间、偏好、会话分组，其中退出登录单独会话组；退出登录使用后台危险色 `#D47476`。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 用户菜单分组、箭头、危险色和 `#themeSwitch` 唯一性验收通过。 |
| 2026-08-10 18:47:47 | 前台用户菜单和空间二级浮层仍偏重：进入后台文案需统一；空间浮层不应保留标题、搜索和组织分组；空间角色需中文；创建/加入空间应合并；设置空间仅对管理角色显示。 | 已将“进入管理后台”口径收敛为“进入后台”；“切换空间”右侧增加 `>` 二级提示；hover 用户菜单其他项立即隐藏空间浮层；空间浮层移除标题、搜索和组织分组，仅展示空间名称、中文角色和成员数；“创建空间/加入空间”合并为“创建或加入空间”；“空间设置”改为“设置空间”，仅拥有者/管理员显示。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 空间浮层轻量化、中文角色、hover 关闭和文案验收通过。 |
| 2026-08-10 18:59:42 | 前台用户菜单顶部仍残留空间/组织 summary 信息，空间二级浮层按钮在暗色主题下不清晰，后台用户菜单缺少返回前台入口。 | 已移除前台用户菜单顶部 summary，不再显示用户、空间组织或 `MoonBox Lab`；空间列表按钮显式使用暗色背景、浅色文字和弱边框；后台用户菜单新增“返回前台”，点击进入 `/requirements`。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` summary 移除、暗色可读性和后台返回前台入口验收通过。 |
| 2026-08-10 19:19:46 | 前后台用户菜单下拉框背景与侧边栏过近，层级不清；后台用户菜单也需要与前台一致进行分组。 | 已新增前后台菜单专用浮层 surface token，使用户菜单和空间二级浮层使用区别于侧边栏的背景、边框、阴影和 hover 态；后台用户菜单按账号、导航、偏好、会话分组，退出登录继续单独成组并保持危险色一致。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 前台用户菜单/空间浮层和后台用户菜单分组与浮层层级验收通过。 |
| 2026-08-10 19:56:19 | 前台“进入后台”必须只对有后台权限用户展示；前后台相同功能图标需一致，不同功能图标需不同。 | 已新增前台当前用户 `canAccessAdmin` 权限开关，`进入后台` 仅在用户具备后台访问权限时渲染；统一菜单图标映射：个人资料 `UserRound`、修改密码 `KeyRound`、进入后台/返回前台 `LayoutDashboard`、界面主题 `SunMoon`、退出登录 `LogOut`，并避免前台菜单内不同功能复用图标。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 前后台用户菜单权限入口与图标唯一性验收通过。 |
| 2026-08-11 17:45:07 | 需求中心看板卡片上滑时会在列头顶部区域透出，影响滚动视觉层级。 | 已为 `.rc-column-head` 建立隔离 stacking context，并用 `::before` 向上延伸 18px 不透明列头遮罩；`.rc-board-wrap` 保持相对定位，列头 `z-index` 提升到 `8`，确保卡片滚动经过表头边界时被遮住且不拦截点击。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 滚动截图与 computed style 验收通过：`position=sticky`、`z-index=8`、`isolation=isolate`、`::before inset=-18px 0 0`、`pointer-events=none`。 |
| 2026-08-11 22:00:52 | 前台用户菜单空间二级浮层中，每个空间项使用独立卡片边框，层级偏重。 | 已将空间项改为轻量列表行：默认无边框透明背景，hover 使用弱背景，selected 使用金色弱背景、右侧勾选和 2px 左侧金线；“创建或加入空间”仍保留独立边框按钮。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 用户菜单空间浮层截图与 computed style 验收通过：空间项 `borderWidth=0px`，hover 弱背景，selected 左线 `width=2px`，动作按钮 `borderWidth=1px`。 |
| 2026-08-12 10:00:00 | 需求中心需要新增手动刷新入口，让用户主动了解 9 个阶段的实时情况；刷新需保留当前筛选，刷新失败不能清空当前看板。 | 已在筛选工具栏末尾新增 `RefreshCw` 图标按钮，使用独立 `isRefreshingContext` 状态；手动刷新成功后替换最新上下文并保留搜索/筛选状态，刷新失败仅显示 toast“刷新失败，已保留当前看板”，不进入错误空屏。 | `pnpm --dir src/web test -- requirement-center.test.tsx`、`pnpm --dir src/web build`、Playwright Chromium `1440x900` 工具栏刷新按钮截图与 computed style 验收通过：按钮 `38px × 38px`、`borderWidth=1px`、刷新中 `disabled=true`、`aria-busy=true`、图标动画 `rc-spin 0.8s`。 |
