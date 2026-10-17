---
title: 页面滚动底部浅色背景露出修复 Chat 工作台规格增量
created_at: 2026-10-04 23:54:49
updated_at: 2026-10-04 23:54:49
---

# 页面滚动底部浅色背景露出修复 Chat 工作台规格增量

## MODIFIED Requirements

### Requirement: 原型与Ops验收契约

系统 MUST 按已确认风格迁移实现；prototype仅为设计输入，最终验收以design、来源acceptance、1440px及交互截图、computed style、Mock/API边界和REQ最终一致性共同判定。

#### Scenario: 提交UI验收

- **WHEN** 页面实现完成准备验收
- **THEN** 提供Skeleton首轮确认、深浅窄屏和动作族证据，禁止以原稿模拟成功替代真实验收

#### Scenario: 深色工作台根层背景不露底

- **GIVEN** 用户访问 `/chat` 且工作台处于深色主题
- **WHEN** 页面向上滑动、触发边界 overscroll 或宿主短暂暴露浏览器根层
- **THEN** `html`、`body`、`#root` 与 Chat 工作台根容器的背景必须保持一致或等价深色
- **AND** 页面底部不得露出浅色全局背景
- **AND** Chat 输入区、会话内容区、侧边栏和执行详情面板下方不得出现透明穿透
- **AND** 验收证据必须包含 1440px 截图和 `html`、`body`、`#root`、`[data-testid=chat-shell]` 的 computed style

#### Scenario: 工作台根层背景不污染其他页面

- **WHEN** 用户从 `/chat` 离开到登录页、官网首页、管理后台或浅色主题工作台
- **THEN** 系统必须恢复对应页面的既有根层背景和滚动行为
- **AND** 深色工作台背景类、data 属性或 CSS 变量不得残留污染非工作台页面
