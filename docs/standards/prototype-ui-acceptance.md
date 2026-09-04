---
purpose: 原型驱动 UI 验收标准
content: 带 prototype 或 UI 参考稿的 UI Change 的 UI Contract、Reference Replication Contract、Skeleton、截图、computed style、Mock/API 和一致性验收清单
created_at: 2026-08-10 20:14:00
updated_at: 2026-09-02 19:12:31
owner: MoonBox 产品团队
---

# 原型驱动 UI 验收标准

本标准适用于任何包含 `prototype/`、`prototype_refs`、`AC-PROTOTYPE-*`、UI Skeleton 或明确引用既有页面视觉的 UI Change。目标是把“像不像原型”前置为可执行合同、可截图证据和可复核样式检查。UI 效果不如预期、视觉偏差或交互异常同时 MUST 遵守 `rules/root-cause-evidence.md`。

## UI Reference Replication Contract

当用户提供附件 HTML、截图、标注图、既有页面或参考稿，并要求“一对一复刻”“全面贴近”“保持一致”或等价目标时，`/explore`、`/req-complete`、`/req-opsx`、`/opsx-apply`、`/opsx-modify` 和 `/opsx-archive` 必须承接同一份 UI Reference Replication Contract。

### 适用判定

| 判定项 | 要求 |
|---|---|
| 保真模式 | 一对一复刻、风格迁移或局部一致 |
| 事实源优先级 | 附件 HTML、截图、标注图、既有页面、当前实现、业务语义保留项和冲突处理 |
| 范围边界 | 本次要复刻的组件、明确不复刻的组件、不得被误改的既有能力 |
| 验收批次 | 每批组件、状态、视口和证据入口 |

### 参考稿反向工程清单

| 类别 | 必查项 |
|---|---|
| 页面壳 | 画布背景、主内容宽高、侧边栏、标题区、滚动容器和 sticky 边界 |
| 组件结构 | 指标卡、筛选区、按钮、看板列头、列体、空态、任务卡、标签、文档入口、进度、浮层 |
| 视觉属性 | 字体、字号、字重、行高、颜色、背景、边框、圆角、阴影、padding、gap、宽高 |
| 状态矩阵 | empty、filled、hover、focus、active、disabled、loading、open、collapsed、error |
| 响应式 | 1440px 基准、移动端、窄视口、横向滚动、文本溢出和触控密度 |

### Selector 映射表

| 字段 | 必填内容 |
|---|---|
| 组件 | 业务组件名或 UI 区块 |
| 参考 selector | 附件 HTML、参考页面或截图标注中的 selector / 文本锚点 |
| 目标 selector | 当前实现中的 CSS selector、data-testid 或可稳定定位的 DOM 路径 |
| 实现入口 | 目标组件文件或样式文件 |
| 状态 | default、hover、empty、filled、sticky、mobile 等 |
| 验收批次 | 所属批次和完成状态 |

### 动作按钮与 Modal 组件族矩阵

当参考稿复刻范围包含按钮、快捷动作、卡片 footer、FAB、工具栏动作、阶段动作或其他会触发弹窗、抽屉、Popover、确认框、Action Modal、AI 面板的交互入口时，`/req-opsx`、`/opsx-apply` 和 `/opsx-modify` 必须在实现前建立动作按钮矩阵。该矩阵用于一次性梳理动作族与浮层组件族，避免只按单个按钮逐轮返修。

| 字段 | 必填内容 |
|---|---|
| 动作按钮 | 用户可见按钮文案、图标、所在组件和业务动作 |
| modal 类型 | `dialog`、`drawer`、`popover`、`confirm`、`action-modal`、`ai-panel`、`inline-expanded` 或 N/A |
| 参考 selector | 附件 HTML、参考页面、截图标注或文本锚点中的按钮与浮层 selector |
| 目标 selector | 当前实现按钮、触发器、浮层根节点、关闭按钮和主操作按钮 selector |
| 状态 | default、hover、focus、active、disabled、loading、open、submitted、error、empty、permission-hidden 等 |
| 组件族 | 共用 Button、Modal/Drawer、ActionPanel、Form、Toast、Overlay 或专属组件入口 |
| 验收证据 | 截图、computed style JSON、Playwright/DOM 断言、键盘/外部点击证据或 trace 摘要 |
| 处置结论 | 一次性实现、复用既有组件、保留现状、证据不足、超出范围 |

矩阵完成后，属于同一动作族的按钮和 modal 必须统一实现组件族：同一视觉等级、尺寸、图标、关闭路径、loading/disabled/error、外部点击 capture 阶段、提交后 toast 或状态流转应一次性覆盖。若某个按钮确需例外，必须在矩阵中写明业务原因和验收方式；不得把例外留到后续逐按钮问答中补。

### Computed Style 采样清单

| 字段 | 必填内容 |
|---|---|
| 页面/视口 | 路由、宽高、主题、登录态或权限态 |
| selector | 目标 selector 和参考 selector |
| 属性 | `font-family`、`font-size`、`line-height`、`padding`、`gap`、`border`、`background`、`color`、`position`、`z-index`、`overflow` 等 |
| 期望 | 参考值、token、范围或允许偏差 |
| 实际 | 当前实现采样值 |
| 结论 | pass、warn、fail、N/A 和原因 |

### 分批验收门禁

参考稿复刻不得只用整体观感关闭。推荐按以下批次推进：页面壳与布局、品牌/标题、指标/筛选、看板列头与空列、任务卡与标签、动作按钮与 modal 组件族、移动端与滚动/sticky。每批完成前必须记录 selector 映射、动作按钮矩阵（如适用）、关键 computed style、截图或等价证据、非目标未改说明。

## UI Contract

`/req-opsx` MUST 在 Change `design.md` 写入 UI Contract。缺少 UI Contract 时，`/opsx-apply` 只能补齐合同和 Skeleton，不得把 UI 实现标记完成。

| 项 | 必填内容 |
|---|---|
| 事实源优先级 | `prototype.html`、PNG/截图、`context.md`、`acceptance.md`、`ui-design.md`、既有产品页面的排序和冲突处理 |
| 页面与入口 | 路由、导航入口、默认落点、登录态/权限态差异 |
| 信息架构 | 侧边栏、顶部区、主内容、浮层、弹窗、列表、卡片、空态和错误态 |
| 视觉 token | 字体、字号、行高、颜色、边框、间距、圆角、阴影、层级和滚动规则 |
| 交互状态 | hover、active、focus、disabled、loading、click outside、click outside capture 阶段、弹窗内 `stopPropagation`、展开/收起、二级浮层和键盘可达性 |
| 图标与文案 | 相同功能的统一图标/文案，不同功能的图标差异，用户可见文案产品化 |
| Mock/API 边界 | Mock 区域、真实 API 区域、后续接入计划、生产风险和验收非目标 |
| 权限规则 | 菜单、按钮、危险操作、空间/后台入口等按角色显示的规则 |
| 一致性参照 | 需要对齐的前台、后台或既有页面，以及逐项 checklist |

## Skeleton 首轮确认

带 prototype 的 UI Change MUST 先完成 Skeleton，再进入细节实现。Skeleton 至少覆盖：

- 页面壳、布局区域、导航结构、用户菜单、弹窗/浮层容器和主要状态容器。
- 关键元素的稳定选择器、可测状态和占位数据边界。
- 1440px 桌面首屏截图或等价视觉证据，证明布局、密度和层级方向正确。

Skeleton 证据未通过时，不得继续关闭细节实现任务。

## 视觉截图门禁

`/opsx-apply` 和 `/opsx-modify` 完成 UI 任务前 MUST 记录 1440px 桌面视口证据。若页面存在关键交互，还 MUST 记录对应交互状态。

| 场景 | 必查内容 |
|---|---|
| 默认首屏 | 页面标题、导航、主要区域、间距、对齐、滚动边界、文本溢出 |
| 侧边栏 | 展开、收起、折叠按钮、active 态、分组、品牌区、用户触发器 |
| 用户菜单 | 分组、入口权限、危险色、click outside、二级浮层隐藏规则 |
| 弹窗/浮层 | 宽高、层级、背景区分、边框、滚动、底部操作、click outside capture 阶段、弹窗内 `stopPropagation` 后外部点击仍可关闭 |
| 筛选与列表 | 输入框、segmented 控件、select、空态、错误态、卡片密度 |
| 响应式 | 原型或验收要求的低视口、移动端或横向滚动场景 |

任意 UI 返修会使相关旧截图 stale；必须重新取证并更新 Change `trace.md`。

若验收反馈仅描述“效果不对”“不像原型”或“交互不符合预期”，AI MUST 先输出人工补证步骤，要求补充页面路由、视口、期望/实际截图、关键交互状态、元素选择器或 computed style；补证前不得把偏差根因写为 confirmed。

### 视觉证据目录归属

UI 视觉证据分为本地临时证据和长期验收证据：

- 本地临时证据 MAY 写入被 `.gitignore` 覆盖的 `tmp/visual-evidence/`，用于 Playwright 截图、computed style JSON、人工对照截图和返修中间验证。
- 长期验收证据 MUST 写入对应 `openspec/changes/<change-id>/evidence/`，或在 Change `trace.md`、`acceptance.md`、Issue `acceptance.md` 中记录脱敏后的证据摘要。
- `/opsx-apply`、`/opsx-modify` 可以在执行中引用 `tmp/visual-evidence/`，但 `/opsx-archive` 前必须确认关键证据已转存或摘要化；不得只依赖本地临时路径闭环。
- 截图与样式证据不得包含真实客户数据、密钥、访问令牌、Cookie、Authorization header、真实 `.env` 内容、未脱敏日志或个人信息。

### 浮层外部点击捕获阶段验收

凡 UI Contract、验收标准或实现说明声明弹窗、Popover、Dropdown、Date/Time Picker 或其他可交互浮层支持点击外部区域关闭，capture 阶段 MUST 覆盖弹窗内 `stopPropagation` 场景：

- 内部按钮、输入、滚动容器、嵌套菜单或浮层内容区调用 `stopPropagation` 或等价阻止冒泡逻辑时，内部点击不得误关闭当前浮层。
- 用户点击浮层外部、遮罩或页面其他可点击区域时，浮层仍必须按 UI Contract 关闭、保留当前值、丢弃草稿或回到约定状态。
- 验收证据必须记录检查方式，例如 Playwright 点击、人工交互截图、DOM 事件说明、组件文档或代码片段摘要，并说明外部点击监听位于 capture 阶段，或具备不受内部 `stopPropagation` 影响的等价机制。
- capture 阶段证据应在 `/req-complete` 的 prototype 拆解、`/req-opsx` 的 UI Contract 或 `/opsx-apply` / `/opsx-modify` 的关键交互证据中至少出现一处；不得只写“支持点击外部关闭”而不覆盖阻止冒泡场景。

### 附件截图逐项视觉对照表

UI 型 `/opsx-modify` 若验收反馈包含附件截图、标注图、原型截图、实际截图或前后对比图，MUST 在返修前建立逐项视觉对照表；该表未完成前不得修改业务实现。

| 字段 | 必填内容 |
|---|---|
| 附件/截图编号 | 用户附件、原型截图、实际截图、标注图或历史视觉证据编号 |
| 页面/状态 | 路由、视口、主题、交互状态、弹窗/浮层/空态/错误态 |
| 对照对象 | 原型、验收截图、标注区域、当前实现或历史证据 |
| 期望表现 | 附件或原型表达的目标视觉/交互结果 |
| 实际表现 | 当前实现、复现截图或已有证据中的表现 |
| 偏差项 | 间距、字号、颜色、对齐、层级、溢出、文案、图标、状态等 |
| 检查方式 | 视觉对照、Playwright 截图、computed style、DOM 选择器或人工补证 |
| 处置结论 | 本次修复、无需修改并说明理由、超出范围、证据不足 |
| 证据入口 | 截图、trace、style JSON、测试输出或脱敏摘要 |

若缺少页面路由、视口、主题、期望截图、实际截图、关键交互状态、选择器或 computed style，且因此无法判断偏差，`/opsx-modify` MUST 先输出聚焦补证步骤。返修后必须在 Change `trace.md`、`tasks.md` 验收返修记录或等价验收证据中记录对照表复验结果。

## Computed Style

对原型差异风险高或验收反馈已指出的视觉点，MUST 使用浏览器 computed style、Playwright 断言或等价工具记录关键属性。

| 类别 | 示例属性 |
|---|---|
| 字体层级 | `font-family`、`font-size`、`font-weight`、`line-height` |
| 尺寸间距 | `width`、`height`、`padding`、`margin`、`gap`、`min/max-*` |
| 颜色边框 | `color`、`background-color`、`border-color`、`border-width` |
| 层级定位 | `position`、`z-index`、`overflow`、`transform` |
| 交互状态 | hover/active/open/collapsed 状态下的样式变化 |

computed style 证据可以记录在 Change `trace.md`、验收日志或测试输出中，但必须能定位到页面、选择器、视口和结论。

返修前后 computed style 或等价检查 SHOULD 回扣根因证据链：记录原偏差值、修复后值、期望值和仍存在的例外。

## Mock/API 边界

带 UI 的 Change 必须声明数据边界：

- 使用 Mock 数据时，明确 Mock 字段、Mock 来源和不代表真实 API 已完成。
- 使用真实 API 时，明确接口来源、权限、错误态和空态。
- 如果本 Change 不接入真实数据，必须把真实数据接入作为非目标或后续建议，避免验收误判。

## 前后台一致性 Checklist

当前台页面参照后台、后台页面参照前台，或两者共享功能时，MUST 至少检查：

- 品牌区：Logo 尺寸、平台名称、版本徽标、副标题、省略规则。
- 导航：菜单数量、命名、分组、图标尺寸、行高、间距、active 态。
- 折叠：展开/收起按钮尺寸、位置、方向、边框、背景和遮挡风险。
- 用户菜单：触发器密度、弹出方向、分组、危险色、入口权限和二级浮层。
- 字体：标题、菜单、正文、辅助文字和按钮的字号、字重、行高。
- 图标与文案：相同功能一致，不同功能不复用同一图标。

## 归档门禁

`/opsx-archive` 前 MUST 复核 linked REQ 与 Change 的 UI Contract、Skeleton、截图、computed style、Mock/API 边界和最终实现一致。缺证据、证据 stale、Mock/API 边界未声明或前后台一致性 checklist 未完成时，归档应阻断。
