---
title: 页面滚动底部浅色背景露出修复
created_at: 2026-10-04 23:54:49
updated_at: 2026-10-04 23:54:49
---

# 页面滚动底部浅色背景露出修复

## 背景

BUG-0027 记录了深色 Chat 工作台页面向上滑动或触发宿主 overscroll 时，底部露出大面积浅色背景的问题。用户截图与浏览器 computed style 取证显示，`[data-testid=chat-shell]` 为深色背景，但 `body` 仍是浅色背景，`html` 与 `#root` 透明，导致页面根层被短暂暴露时出现明显视觉断层。

该问题影响 Chat 工作台与复用 `.requirement-center` 的需求中心页面深色主题一致性。当前没有证据表明 API、数据库、权限或执行链路受影响，本次 Change 聚焦前端根层背景与滚动边界修复。

## 变更内容

- 为 `/chat` 与 `/requirement-center` 等深色工作台路由建立页面根层背景同步策略，确保 `html`、`body`、`#root` 与工作台根容器在深色主题下不会出现浅色穿透。
- 保持浅色主题、登录页、官网首页和管理后台既有背景行为不被误污染。
- 补充深浅主题、滚动边界、computed style 和 1440px 视觉证据的回归验证。
- 将 BUG-0027 与本 Change、`sprint-008` 建立双向追溯。

## 能力影响

### 修改能力

- `web-catalog-chat-workbench`：补充 Chat 工作台根层背景与 overscroll 边界一致性的验收场景。
- `web-catalog-requirement-center`：补充需求中心前台框架在深色主题下同步根层背景的验收场景。

## 影响范围

- Web 前台 UI：Chat 工作台、需求中心及共享前台工作台根层主题样式。
- 测试：前端样式/组件回归、浏览器 computed style 取证、1440px 视觉截图。
- 文档：BUG trace、Sprint 四件套、Change 文档和规格增量。

不涉及 API、数据库、对象存储、部署拓扑、权限边界、OpenAPI/Orval 生成或产品数据采集链路字段。

## 回滚方案

若修复导致浅色主题、登录页或管理后台背景异常，可回退本 Change 中的工作台根层背景同步逻辑，保留 `.requirement-center` / `.chat-shell` 原有局部背景样式，并通过 BUG-0027 验收项重新定位更小范围的路由级背景控制方案。
