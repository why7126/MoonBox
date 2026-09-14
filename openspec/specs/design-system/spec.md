---
purpose: Design System 生效规格
content: MoonBox Token、组件、预览和校验基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-08-15 15:24:58
owner: MoonBox 产品团队
---

# 设计系统

## Purpose

定义 MoonBox 设计 Token、组件预览、校验基线与 UI 交互治理要求，确保 Web 与管理端界面在视觉语言、组件使用和浮层交互上保持一致。
## Requirements
### Requirement: Token 化 UI 基线

MoonBox SHALL 在 `src/shared/design-system/tokens/` 提供设计 Token，并在 `src/web/src/styles/globals.css` 中映射为 CSS 变量。

#### Scenario: 现代 Ops 工作台 Token 可用

- **GIVEN** Web 应用已加载全局样式
- **WHEN** 登录后工作台、需求中心或管理后台页面使用 MoonBox 语义变量
- **THEN** 深浅主题均可使用画布背景、侧边栏背景、卡片背景、浮层背景、输入背景和层级面板背景 Token
- **AND** 深浅主题均可使用主文本、次级文本、弱提示文本、标题文本、禁用文本和等宽信息文本 Token
- **AND** 系统必须提供主强调金、强调 hover、强调弱底、警告、危险、成功和信息状态 Token
- **AND** 系统必须提供边框、虚线边框、hover 边框、focus 边框、分隔线、圆角、阴影、间距、控件高度、图标尺寸和动效时长 Token

#### Scenario: 品牌层与工作台层 Token 分离

- **WHEN** 页面处于公开首页、登录页或产品手册等品牌叙事场景
- **THEN** 系统可以继续使用宝盒叙事、衬线标题和品牌视觉 Token
- **WHEN** 页面处于登录后的产品工作台、需求中心、Agent/Skill/任务中心或管理后台
- **THEN** 系统必须使用现代 Ops 工作台 Token
- **AND** 页面不得继续依赖公开品牌叙事 Token 作为高频操作区默认样式

### Requirement: 设计系统预览

MoonBox SHALL 在 `src/web/src/pages/dev/DesignSystemPage.tsx` 提供设计系统预览页。

#### Scenario: 预览页展示现代 Ops 组件

- **GIVEN** 开发者打开设计系统预览页
- **WHEN** React 应用完成渲染
- **THEN** 页面必须展示现代 Ops 深浅主题 Token 示例
- **AND** 页面必须展示 Sidebar、Header、统计卡、Toolbar、搜索、segmented、筛选 Popover、Kanban、Card、Drawer、Modal、Toast 和 AI 入口的样式基线或等价组件示例

### Requirement: 设计系统校验

MoonBox SHALL 提供 `scripts/validate-design-system.py`，用于发现硬编码颜色和绕过组件体系的原生控件使用。

#### Scenario: 现代 Ops 硬编码样式校验

- **GIVEN** 源码遵守现代 Ops Token 与组件使用规则
- **WHEN** 校验脚本运行
- **THEN** 脚本成功退出
- **AND** 脚本必须能发现新增工作台、需求中心和管理后台页面中的未授权硬编码颜色
- **AND** 脚本必须能发现绕过设计系统的确认弹窗、toast、状态标签或主要按钮样式

#### Scenario: 工作台字体和尺寸校验

- **WHEN** 工作台页面展示长 REQ/BUG ID、命令、版本号、状态码或计数
- **THEN** 系统必须使用等宽字体或等价可扫描样式
- **AND** 桌面和窄屏下文本不得溢出、重叠或遮挡主操作

### Requirement: 浮层外部点击捕获阶段验收

MoonBox SHALL 在声明支持点击外部关闭的弹窗、Popover、Dropdown、Date/Time Picker 或其他可交互浮层中，将 capture 阶段外部点击关闭链路纳入 UI Contract、验收标准或交互证据。

#### Scenario: 弹窗内阻止冒泡时外部点击仍可关闭

- **GIVEN** 浮层声明支持点击外部区域关闭
- **AND** 浮层内部按钮、输入、滚动容器或嵌套菜单存在 `stopPropagation` 或等价阻止冒泡逻辑
- **WHEN** 用户点击浮层内部可交互区域
- **THEN** 浮层不得被误关闭
- **WHEN** 用户点击浮层外部、遮罩或页面其他可点击区域
- **THEN** 浮层必须按 UI Contract 关闭或回到预期状态
- **AND** 验收证据必须说明外部点击关闭监听位于 capture 阶段或具备不受内部 `stopPropagation` 影响的等价机制

