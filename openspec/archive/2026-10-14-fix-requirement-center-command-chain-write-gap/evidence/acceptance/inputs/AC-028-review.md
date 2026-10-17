---
title: AC-028 当前构建复验
created_at: 2026-10-14 17:20:00
updated_at: 2026-10-14 17:20:00
---

# AC-028 当前构建复验

- 证据性质：真实产品组件＋受控接口夹具；受测 Web 为 `localhost:39002` 当前部署构建，接口夹具记录见样式/证据 JSON。
- 观察：执行摘要在截图中为左对齐轻量 meta；正文和 status 满宽。工具摘要精确宽度另由 AC-030 Playwright CSS 矩阵验证。
- 截图：[AC-028-当前产品场景-1440x1000.png](AC-028-当前产品场景-1440x1000.png)；数据：[AC-028-当前产品场景-1440x1000-style.json](AC-028-当前产品场景-1440x1000-style.json)。
- 界限：接口夹具证明实际渲染组件与浏览器 DOM；未模拟真实服务写入，写入效果须以独立产品轮次/后端证据判定。
- product_data_collection_observability: N/A，仅验收取证，不修改产品采集行为；affected_layers: Web 渲染与 Chat 接口夹具；validation: 浏览器断言通过。
