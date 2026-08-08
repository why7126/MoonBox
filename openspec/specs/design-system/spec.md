---
purpose: Design System 生效规格
content: MoonBox Token、组件、预览和校验基线
created_at: 2026-07-29 23:10:00
updated_at: 2026-07-29 23:10:00
owner: MoonBox 产品团队
---

# 设计系统

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

MoonBox SHALL 提供 `scripts/validate-design-system.py`，用于发现硬编码颜色和绕过组件体系的原生控件使用。

#### Scenario: 校验通过

- **GIVEN** 源码遵守 Token 与组件使用规则
- **WHEN** 校验脚本运行
- **THEN** 脚本成功退出
