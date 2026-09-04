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

#### Scenario: 主题 Token 可用

- **GIVEN** Web 应用已加载全局样式
- **WHEN** 页面使用 MoonBox 语义变量
- **THEN** 深浅主题均可使用背景、面板、边框、强调色、正文、标题和次级文字 Token

### Requirement: 设计系统预览

MoonBox SHALL 在 `src/web/src/pages/dev/DesignSystemPage.tsx` 提供设计系统预览页。

#### Scenario: 预览页可渲染

- **GIVEN** 开发者打开设计系统预览页
- **WHEN** React 应用完成渲染
- **THEN** 页面展示核心 Token 示例和基础 UI 控件

### Requirement: 设计系统校验

MoonBox SHALL 提供 `scripts/validate-design-system.py`，用于发现硬编码颜色、CSS `content` 原始非 ASCII 符号和绕过组件体系的原生控件使用。

#### Scenario: 校验通过

- **GIVEN** 源码遵守 Token、CSS 生成内容与组件使用规则
- **WHEN** 校验脚本运行
- **THEN** 脚本成功退出

#### Scenario: CSS content 非 ASCII 符号必须使用 escape 写法

- **WHEN** CSS 文件通过 `content` 属性生成分隔点、箭头、勾号或其他非 ASCII 符号
- **THEN** 非 ASCII 符号必须使用 CSS escape 写法，例如 `\00B7` 或 `\2713`
- **AND** 不得在 `content` 字符串中直接写入原始非 ASCII 符号
- **AND** ASCII 字符、空字符串、`attr()` 和 `counter()` 用法不得被误判为违规

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

