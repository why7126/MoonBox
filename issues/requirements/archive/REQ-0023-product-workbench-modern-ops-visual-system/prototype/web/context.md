---
requirement_id: REQ-0023-product-workbench-modern-ops-visual-system
prototype: web-modern-ops-visual-system
status: draft
created_at: 2026-08-30 23:24:18
updated_at: 2026-08-30 23:24:30
---

# Web 原型拆解

## 页面清单

| 页面 | 路由/入口 | 说明 |
|---|---|---|
| 公开首页 | `/` | 可保留 MoonBox 品牌叙事与宝盒感，不作为现代 Ops 试点首屏 |
| 登录页 | `/login` | 需评估是否作为品牌过渡页，连接公开品牌和工作台 |
| 产品工作台 Shell | `/requirements` 等登录后入口 | 现代 Ops 视觉系统的主承载区域 |
| 需求中心 | `/requirements` | 首个试点页面，对齐附件看板风格 |
| 管理后台 | `/admin/*` | 共享列表、弹窗、toast、侧边栏和状态组件规范 |

## 关键区域

- 左侧 Sidebar：品牌标识、版本、导航分组、active 态、用户区、空间与主题入口。
- 顶部标题区：英文 eyebrow、页面标题、主操作按钮。
- 统计区：总量、需求、Bug、阻塞、趋势或风险提示。
- 工具栏：搜索、类型 segmented、筛选 Popover、刷新图标按钮。
- 看板区：横向 9 阶段列、列计数、空列状态、卡片、文档链接、主动作、辅助动作。
- 浮层与抽屉：筛选 Popover、用户菜单、空间切换、右侧 Markdown/任务/AI 抽屉、确认弹窗、toast。

## 组件层级

```text
App Shell
  Sidebar
    Brand
    Navigation
    User Menu
  Main
    Page Header
    Stats Grid
    Toolbar
      Search
      Segmented Control
      Filter Popover
      Refresh Icon Button
    Kanban Board
      Column
        Column Header
        Empty State / Card List
          Card
            ID / Sprint
            Title
            Priority / Owner
            Document Links
            Progress / Blocked
            Footer Actions
    Right Drawer / Modal / Toast
```

## 状态矩阵

| 状态 | 期望表现 |
|---|---|
| 默认深色 | 现代 Ops 深色画布，面板层级清晰，金色强调不过量 |
| 浅色主题 | 背景、面板、边框、文本和状态色均可读，不只是深色反转 |
| 空列 | 虚线边框或轻量占位，提示该阶段暂无对象 |
| 阻塞 | 使用警告色和明确文案，不能只靠数字或图标 |
| 加载 | skeleton 不改变布局高度 |
| 错误 | 保留当前数据或展示稳定错误面板，不清空结构 |
| Popover 打开 | 不遮挡主操作，支持外部点击和 Esc 关闭 |
| 抽屉打开 | 看板不发生列宽异常跳动，抽屉内点击不误关闭 |
| 窄屏 | 关键导航、筛选、主动作和横向看板仍可触达 |

## 交互触发

- 点击类型 segmented 即时切换筛选。
- 点击筛选按钮打开 Popover，应用后显示 active badge。
- 点击刷新图标进入 loading 态，完成后恢复。
- 横向滚动看板时显示边缘提示，表头与列内容保持对齐。
- 点击卡片文档链接打开右侧抽屉或新 Tab。
- 点击 AI 入口打开右侧聊天抽屉。
- 弹窗、Popover、Dropdown 和抽屉均提供可理解退出路径。

## 数据依赖

- 需求中心默认继续读取真实 REQ、BUG、Sprint、OpenSpec 与文档接口。
- 原型中的示例数据仅用于视觉验收和设计说明，不写入治理文档、后端接口或数据库。
- 本需求不新增 API、DB、日志、行为埋点或 Task Trace 字段；如后续设计要求新增行为事件，需要在 Change 中重新声明观测影响。

## 响应式断点

| 视口 | 验收重点 |
|---|---|
| 1440px 桌面 | 首屏信息密度、侧边栏、统计、工具栏、看板列、浮层层级 |
| 1024px 平板/窄桌面 | Sidebar 折叠、工具栏换行、看板横向滚动 |
| 390px 移动 | 主要动作可触达、抽屉全屏、文本不溢出、横向内容有明确滚动路径 |

## 1440px 验收焦点

- 左侧 Sidebar 宽度、品牌区、版本徽标、导航 active 态与用户区不重叠。
- 标题区、统计区和工具栏之间的垂直节奏紧凑但不拥挤。
- 统计卡有数字、标签和趋势/风险提示，视觉层级明确。
- 筛选 Popover 与按钮位置对齐，打开后不遮挡刷新按钮和主操作。
- Kanban 列宽、列间距、卡片内边距、卡片左侧状态边和空列占位稳定。
- 右侧抽屉、确认弹窗和 toast 层级高于看板，且不造成主体布局位移。

## PNG 策略

当前阶段以 `prototype.html` 和本拆解文档表达结构、层级与视觉方向；PNG 截图不作为 `/req-complete` 阻塞项。后续 `/opsx-apply` 必须生成 1440px 和关键交互截图作为长期验收证据。
