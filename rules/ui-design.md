---
purpose: MoonBox UI 设计规则
content: MoonBox 深浅主题、字体、布局、组件和视觉验收规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-09-03 09:34:14
owner: MoonBox 产品团队
---

# UI 设计规则

MoonBox 的界面语言来自 `ProjectMoonBox/ui-design/ui-design.md`。新页面、重构页面和设计系统建设必须以该文档为事实源。

## 设计定位

MoonBox 采用“双品牌层级”：对外叙事页面保留东方器物质感、克制编辑排版感和金色强调；产品工作台、管理后台和运营型页面统一采用现代 Ops 视觉系统。Ops 系统强调高信息密度、近直角、细边框、清晰层级、可扫描表格与看板、沉稳深浅主题和 MoonBox 品牌资产，不采用通用 SaaS 蓝白后台、蓝紫科技渐变或装饰化数据大屏。

## Token

| 用途 | 深色主题 | 浅色主题 |
|---|---|---|
| 主背景 | `#0A0D14` | `#F4F6FA` |
| 次级面板 | `#131826` | `#FFFFFF` |
| 抬升面板 | `#1A1F2C` | `#EEF2F7` |
| 输入面 | `#0F1320` | `#F8FAFD` |
| 边框 | `#242A3A` | `#DDE3EE` |
| 细边框 | `#1B2130` | `#E8EDF5` |
| 强调金 | `#D8AC55` | `#B9832E` |
| 辅助金 | `#8B6F3D` | `#8C6528` |
| 主文字 | `#ECEAE4` | `#202636` |
| 标题强调 | `#F6F1E7` | `#101828` |
| 次级文字 | `#98A0B3` | `#677085` |

## 字体

- 对外叙事页面：中文标题使用 `Noto Serif SC`，英文点睛词可使用 `EB Garamond` italic。
- Ops 工作台/后台：标题与正文统一使用 `Inter` + `Noto Sans SC`，辅助标识、ID、状态胶囊和小标签使用 `JetBrains Mono` 或系统等宽字体。
- Ops 页面正文行高约 1.45，避免营销式大字号；通过对齐、细线、密度、色阶和状态徽标建立层级。

## 布局

- 对外叙事页面顶部导航采用 Logo、文本链接和 CTA 的横向结构，Hero 可使用签名插画。
- Ops 工作台采用侧边栏 + 主工作区 + 工具栏 + 表格/看板/抽屉/弹窗结构；首屏直接呈现可操作内容，不做营销落地页。
- 工作台与后台需要保持一致的品牌区、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸和 toast 行为。

## 组件规则

- Ops 按钮、输入、筛选、表格、看板卡片和弹窗默认使用 8px 以内圆角，主按钮使用金底实色，次要动作使用边框或文字按钮。
- 签名开盒插画每屏最多出现一次，不作为可重复图标。
- Logo 小尺寸场景使用 Logo 位图资产，不使用签名插画代替。
- Ops 页面避免蓝紫科技渐变、明亮发光、大圆角卡片、厚重阴影、装饰性大屏组件和低信息密度卡片墙。
- CSS 伪元素或样式规则使用 `content` 生成非 ASCII 符号时，必须使用 CSS escape 写法，例如 `\00B7`、`\2713`，不得直接写入 `·`、`✓`、`→` 等原始符号；ASCII 字符、空字符串、`attr()`、`counter()` 和纯文本占位可保持原写法。实现和返修时必须通过 `scripts/validate-design-system.py` 校验，避免不同截图、字体、压缩或编码链路中出现符号漂移。

## 浮层交互

- 弹窗、Popover、Dropdown、Date/Time Picker、Tooltip 以外的可交互浮层 MUST 明确至少一种用户可理解的退出路径，例如点击外部区域、选择后立即关闭、关闭按钮、`Esc` 或返回上级；涉及输入编辑、删除、支付、提交、权限、不可逆动作或跨页面状态变更时 SHOULD 提供显式取消/关闭路径。
- 轻量选择场景 SHOULD 避免额外确认按钮：当用户只是在有限选项中选择展示值、过滤值、日期快捷项、空间/菜单项或其他可随时重选的临时值时，点击选项应立即应用并关闭，或点击外部区域关闭并保留当前值；不得为了“可退出”而默认增加“取消 / 确定”等确认按钮。
- 若浮层内存在多步编辑、自由输入、批量选择、异步提交、校验失败恢复或选择会产生高成本副作用，MAY 使用确认按钮，但 MUST 在 UI Contract、验收标准或交互说明中写明为何不能采用轻量选择的即时应用/外部关闭模式。
- 凡 UI Contract、验收标准或实现说明声明浮层支持点击外部区域关闭，capture 阶段 MUST 覆盖弹窗内 `stopPropagation` 场景：浮层内部按钮、输入、滚动容器或嵌套菜单阻止冒泡时，内部点击不得误关闭浮层；用户点击浮层外部、遮罩或页面其他可点击区域时，浮层仍 MUST 按预期关闭或回到约定状态。验收证据 MUST 说明外部点击监听位于 capture 阶段，或具备不受内部 `stopPropagation` 影响的等价机制。

## 验收

UI 变更必须检查深浅主题对比、中文衬线标题使用、英文斜体使用、金色强调唯一性、近直角和细线基调，以及移动端文字不溢出。UI 效果不如预期、视觉偏差或交互异常 MUST 遵守 `rules/root-cause-evidence.md`：先记录截图、视口、关键交互状态、computed style 或等价证据；证据不足时输出人工补证操作步骤，不得直接猜测样式根因。

## Prototype-driven UI Gate

带 `prototype/` 的页面、弹窗或主要 UI 流程 MUST 先完成原型驱动门禁，再进入实现完成态。详细模板见 `docs/standards/prototype-ui-acceptance.md`。

1. 原型拆解：`/req-complete` MUST 将 prototype 拆成页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和视觉验收焦点。
2. UI Contract：`/req-opsx` MUST 在 Change `design.md` 写入 UI Contract，明确事实源优先级、页面/路由、布局结构、关键尺寸、字体层级、颜色、图标、文案、交互状态、Mock/API 边界、权限显示规则和前后台一致性参照；缺 Contract 时不得进入最终实现验收。
3. UI Skeleton：`/req-opsx` MUST 在 Change `design.md` 写入 UI Skeleton，并在 `tasks.md` 设置先行任务；Skeleton 至少包含路由/页面壳、布局区域、组件插槽、状态容器、可测选择器和占位数据边界。Skeleton 首轮必须先做 1440px 截图或等价视觉证据确认，再继续细节实现。
4. 前后台一致性：若原型或验收要求参照管理后台、前台或既有页面，MUST 建立 checklist，对齐品牌区、菜单分组、导航密度、active 态、折叠按钮、用户菜单、浮层层级、字体 token、图标尺寸、hover/click outside、click outside capture 阶段和危险色。
5. 视觉与交互截图门禁：`/opsx-apply` 和 `/opsx-modify` MUST 在 1440px 桌面视口验证首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出；同时覆盖关键交互截图，例如侧边栏展开/收起、用户菜单、二级浮层、筛选、弹窗、空态、错误态和权限差异。声明支持点击外部关闭的弹窗、Popover、Dropdown、Date/Time Picker 或其他可交互浮层，MUST 在 capture 阶段覆盖弹窗内 `stopPropagation` 场景，并记录“内部点击不误关闭、外部点击仍关闭”的交互证据。UI 型 `/opsx-modify` 若验收反馈包含附件截图、标注图、原型截图或实际截图，MUST 在返修前建立“附件截图逐项视觉对照表”，逐项记录截图编号、页面/状态、期望表现、实际表现、偏差项、检查方式、处置结论和证据入口；对照表缺少必要路由、视口、交互状态、期望/实际截图或 computed style 证据时，必须先补证，不得直接进入返修。UI 返修后旧截图立即视为 stale，必须重新取证并回填对照表复验结果。
6. Computed style 验收：对原型敏感或曾返修的视觉点，MUST 记录浏览器 computed style 或等价检查，包括 `font-size`、`font-family`、`line-height`、`width`、`height`、`gap`、`padding`、`border`、`background`、`color`、`z-index`、`overflow` 和 `position` 等关键属性。
7. Mock/API 边界声明：若 UI 使用 Mock 数据，MUST 在 Change `design.md`、`trace.md` 或验收证据中明确声明哪些区域为 Mock、哪些调用真实 API、Mock 进入生产的风险和后续真实数据 Change；不得用 Mock 数据默认冒充已接入 API。
8. 图标与文案一致性：相同功能在前后台或同一产品域内 MUST 使用相同图标和一致文案；不同功能 SHOULD 使用不同图标。用户可见文案必须产品化，避免暴露内部命令名、阶段脚本名或实现术语，除非原型明确要求。
9. 文档实时回填：实现或返修改变 prototype 意图、UI 行为、验收标准、非目标、Mock/API 边界或权限规则时，MUST 同步更新 active Change 文档和 linked REQ `requirement.md` / `acceptance.md` / `trace.md`。
10. 最终一致性：`/opsx-archive` MUST 在归档前确认 linked REQ 与最终 Change 设计、实现证据、1440px /关键交互截图、computed style 结果和 Mock/API 边界一致；不一致时阻断归档。

推荐知识库入口：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。

## UI Reference Replication Gate

当用户明确引用附件 HTML、截图、标注图、既有页面或参考稿，并要求“一对一复刻”“全面贴近”“保持一致”或等价目标时，UI Change MUST 在实现前建立 UI Reference Replication Contract。该契约是 Prototype-driven UI Gate 的增强形态，详细模板见 `docs/standards/prototype-ui-acceptance.md`。

1. 保真模式：先区分一对一复刻、风格迁移或局部一致；若只迁移风格，必须写明不复刻的组件和保留的业务语义。
2. 参考稿反向工程：在 `/explore` 或 `/req-complete` 阶段拆出组件清单、布局结构、状态矩阵、响应式、滚动/sticky、空态、卡片、按钮、浮层和品牌区等差异点。
3. Selector 映射：`/req-opsx` MUST 在 Change `design.md` 记录参考稿 selector、目标实现 selector、测试 selector、组件文件和状态类；无法定位 selector 的组件不得进入实现完成态。
4. 动作按钮矩阵：涉及按钮触发弹窗、抽屉、Popover 或操作面板时，详细事实源见 `docs/standards/prototype-ui-acceptance.md`；实现前 MUST 建立“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵，并按动作族一次性设计、实现和验收组件族，不得继续逐按钮问答返修。
5. Computed style 采样清单：对关键组件记录字体、字号、行高、宽高、padding、gap、边框、圆角、背景、颜色、position、z-index、overflow 等属性的期望、当前值和容差。
6. 分批实现与验收：按页面壳、标题/品牌、指标/筛选、看板列、空态、卡片、动作按钮与浮层、响应式和滚动/sticky 等批次推进；每批都需要截图或 computed style 证据。
7. 返修处理：若 `/opsx-modify` 暴露 Contract 缺口，先补齐契约、动作按钮矩阵和证据，再做局部修改；不得继续只按用户截图逐元素试改。
8. 归档门禁：`/opsx-archive` 必须确认 UI Reference Replication Contract、最终截图、computed style 采样、selector 映射、动作按钮矩阵、REQ 验收资料和 Change 证据一致。
