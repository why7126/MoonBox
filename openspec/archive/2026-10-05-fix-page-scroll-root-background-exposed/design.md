---
title: 页面滚动底部浅色背景露出修复设计
created_at: 2026-10-04 23:54:49
updated_at: 2026-10-04 23:54:49
---

# 页面滚动底部浅色背景露出修复设计

## 背景与现状

Chat 工作台页面把深色主题挂在 `<main className="requirement-center theme-... chat-shell">` 及其子树上，`body` 仍使用全局浅色背景，`html` 与 `#root` 背景透明。`.chat-shell` 使用 `height: 100dvh` 与 `overflow: hidden`，当浏览器、宿主 WebView 或页面边界 overscroll 暴露根层时，用户看到的是浅色 `body` 背景。

需求中心页面同样复用 `.requirement-center` 前台工作台壳，修复需要覆盖 Chat 与需求中心，避免只修复单个页面后在另一个工作台继续露底。

## 根因

根因是深色工作台主题只覆盖业务页面根容器，没有同步覆盖浏览器滚动根层和 React 根节点。证据链来自 BUG-0027：

- `body.backgroundColor=rgb(244, 246, 250)`。
- `[data-testid=chat-shell].backgroundColor=rgb(10, 13, 20)`。
- `html` 与 `#root` 透明，`body` 是 scrolling element。
- `.chat-shell` 固定为视口高度并隐藏内部溢出，无法覆盖宿主 overscroll 暴露出的根层。

## 修复方案

1. 在前台工作台路由挂载时，为页面根层设置可撤销的工作台背景状态。
2. 深色主题下使 `html`、`body`、`#root` 与工作台根容器使用一致或等价的深色背景。
3. 浅色主题下使根层背景与浅色工作台背景一致，避免留下深色污染。
4. 离开 Chat / 需求中心等工作台路由时恢复非工作台页面的全局背景行为。
5. 保留 `.requirement-center` 与 `.chat-shell` 自身背景，避免内部布局变化时透明穿透。

实现阶段可以选择 CSS 类、data 属性或 React effect 管理根层状态，但必须满足可撤销、路由隔离、主题切换即时生效和测试可观测。

## 测试策略

- 前端单测或组件测试覆盖工作台路由挂载、主题切换和卸载后的根层状态。
- 浏览器验收覆盖 `/chat` 深色主题 1440px 视口，记录 `html`、`body`、`#root`、`[data-testid=chat-shell]` computed style。
- 浏览器验收覆盖向上滑动或触发边界 overscroll 后不露出浅色背景。
- 回归 `/requirement-center` 深浅主题根层背景。
- 回归登录页、官网首页、管理后台背景不被工作台背景类或变量污染。

## 风险

- 根层样式若清理不完整，可能污染登录页或其他浅色页面。
- 主题切换若只更新工作台容器，不更新根层，仍会产生深浅不一致。
- 不同浏览器和宿主环境对 overscroll 绘制存在差异，需要 computed style 与截图证据共同验收。

## 回滚方案

若根层同步导致非工作台页面背景异常，回退新增的根层类或变量绑定，恢复全局 `body` 背景默认值；保留 BUG-0027 验收证据，后续改用更窄的路由容器或宿主滚动层方案。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 只调整 Web 前台工作台根层背景与视觉验收，不新增或修改 API、数据库、请求日志、usage_events、Task Trace、对象存储或请求封装字段。
  validation: 通过前端测试、浏览器 computed style、视觉截图和页面回归证明；无需新增请求日志或行为埋点验证。
```
