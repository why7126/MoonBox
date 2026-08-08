---
purpose: MoonBox UI 设计规则
content: MoonBox 深浅主题、字体、布局、组件和视觉验收规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-08 21:08:00
owner: MoonBox 产品团队
---

# UI 设计规则

MoonBox 的界面语言来自 `ProjectMoonBox/ui-design/ui-design.md`。新页面、重构页面和设计系统建设必须以该文档为事实源。

## 设计定位

MoonBox 不是通用 SaaS 蓝白后台，也不是常见暗色科技面板。界面应呈现东方器物质感、克制编辑排版感、金色单一强调色、衬线中文标题和意大利体英文点缀。

## Token

| 用途 | 深色主题 | 浅色主题 |
|---|---|---|
| 主背景 | `#0A0C1B` | `#F6F7FB` |
| 次级面板 | `#12142B` | `#FFFFFF` |
| 边框 | `rgba(234,242,255,.10)` | `rgba(20,33,61,.10)` |
| 强调金 | `#CBA35C` | `#B8863E` |
| 辅助金 | `#8B6F3D` | `#8C6528` |
| 主文字 | `#E7E8F3` | `#232A42` |
| 标题强调 | `#E9EEFB` | `#14213D` |
| 次级文字 | `#7C81A6` | `rgba(35,42,66,.55)` |

## 字体

- 中文标题使用 `Noto Serif SC`，字重 600 到 700。
- 英文品牌字和点睛词使用 `EB Garamond` italic，字重 500 到 600。
- 正文使用 `Noto Sans SC`，字重 300，行高约 1.9。
- 除主标题和结语引文外，页面字号保持克制，主要用留白、分割线和字重建立层级。

## 布局

- 顶部导航采用 Logo、文本链接和 CTA 的横向结构。
- Hero 使用左文案右签名插画的双栏结构。
- 差异化内容用竖向细线分隔，不使用大圆角卡片网格。
- 后台和工作台页面可以更密集，但仍应使用细线、近直角和克制色彩。

## 组件规则

- 按钮圆角为 `2px`，主按钮使用金底实色，次要动作优先使用文字链接。
- 签名开盒插画每屏最多出现一次，不作为可重复图标。
- Logo 小尺寸场景使用 Logo 位图资产，不使用签名插画代替。
- 避免蓝紫科技渐变、明亮发光、大圆角卡片、厚重阴影和数据仪表盘式装饰。

## 验收

UI 变更必须检查深浅主题对比、中文衬线标题使用、英文斜体使用、金色强调唯一性、近直角和细线基调，以及移动端文字不溢出。

## Prototype-driven UI Gate

带 `prototype/` 的页面、弹窗或主要 UI 流程 MUST 先完成原型驱动门禁，再进入实现完成态：

1. 原型拆解：`/req-complete` MUST 将 prototype 拆成页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和视觉验收焦点。
2. UI Skeleton：`/req-opsx` MUST 在 Change `design.md` 写入 UI Skeleton，并在 `tasks.md` 设置先行任务；Skeleton 至少包含路由/页面壳、布局区域、组件插槽、状态容器、可测选择器和占位数据边界。
3. 1440px 视觉验收：`/opsx-apply` 和 `/opsx-modify` MUST 在 1440px 桌面视口验证首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出，并记录截图或等价证据入口。
4. 文档实时回填：实现或返修改变 prototype 意图、UI 行为、验收标准或非目标时，MUST 同步更新 active Change 文档和 linked REQ `requirement.md` / `acceptance.md` / `trace.md`。
5. 最终一致性：`/opsx-archive` MUST 在归档前确认 linked REQ 与最终 Change 设计、实现证据、1440px 验收结果一致；不一致时阻断归档。

推荐知识库入口：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。
