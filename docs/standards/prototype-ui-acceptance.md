---
purpose: 原型驱动 UI 验收标准
content: 带 prototype 的 UI Change 的 UI Contract、Skeleton、截图、computed style、Mock/API 和一致性验收清单
created_at: 2026-08-10 20:14:00
updated_at: 2026-08-10 20:14:00
owner: MoonBox 产品团队
---

# 原型驱动 UI 验收标准

本标准适用于任何包含 `prototype/`、`prototype_refs`、`AC-PROTOTYPE-*`、UI Skeleton 或明确引用既有页面视觉的 UI Change。目标是把“像不像原型”前置为可执行合同、可截图证据和可复核样式检查。

## UI Contract

`/req-opsx` MUST 在 Change `design.md` 写入 UI Contract。缺少 UI Contract 时，`/opsx-apply` 只能补齐合同和 Skeleton，不得把 UI 实现标记完成。

| 项 | 必填内容 |
|---|---|
| 事实源优先级 | `prototype.html`、PNG/截图、`context.md`、`acceptance.md`、`ui-design.md`、既有产品页面的排序和冲突处理 |
| 页面与入口 | 路由、导航入口、默认落点、登录态/权限态差异 |
| 信息架构 | 侧边栏、顶部区、主内容、浮层、弹窗、列表、卡片、空态和错误态 |
| 视觉 token | 字体、字号、行高、颜色、边框、间距、圆角、阴影、层级和滚动规则 |
| 交互状态 | hover、active、focus、disabled、loading、click outside、展开/收起、二级浮层和键盘可达性 |
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
| 弹窗/浮层 | 宽高、层级、背景区分、边框、滚动、底部操作 |
| 筛选与列表 | 输入框、segmented 控件、select、空态、错误态、卡片密度 |
| 响应式 | 原型或验收要求的低视口、移动端或横向滚动场景 |

任意 UI 返修会使相关旧截图 stale；必须重新取证并更新 Change `trace.md`。

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
