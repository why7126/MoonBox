---
title: AC-017 当前构建复验
created_at: 2026-10-14 17:20:00
updated_at: 2026-10-14 17:20:00
---

# AC-017 当前构建复验

- 证据性质：真实产品组件＋受控接口夹具；受测 Web 为 `localhost:39002` 当前部署构建，接口夹具记录见样式/证据 JSON。
- 观察：1440 视口 assistant 外层=1168，对话历史=1168；user=760，保持右侧限宽。
- 截图：[AC-017-当前产品场景-1440x1000.png](AC-017-当前产品场景-1440x1000.png)；数据：[AC-017-当前产品场景-1440x1000-style.json](AC-017-当前产品场景-1440x1000-style.json)。
- 界限：接口夹具证明实际渲染组件与浏览器 DOM；未模拟真实服务写入，写入效果须以独立产品轮次/后端证据判定。
- product_data_collection_observability: N/A，仅验收取证，不修改产品采集行为；affected_layers: Web 渲染与 Chat 接口夹具；validation: 浏览器断言通过。
