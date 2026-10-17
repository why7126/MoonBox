---
title: AC-037 当前构建复验
created_at: 2026-10-14 17:20:00
updated_at: 2026-10-14 17:20:00
---

# AC-037 当前构建复验

- 证据性质：真实产品组件＋受控接口夹具；受测 Web 为 `localhost:39002` 当前部署构建，接口夹具记录见样式/证据 JSON。
- 观察：仅有一条 user 消息时，running assistant 独立渲染；1440 视口 history/block/article=1168、assistant col/activity/status=1126、user=760。历史恢复和 saved 阶段同脚本通过。
- 截图：[AC-037-当前产品场景-1440x1000.png](AC-037-当前产品场景-1440x1000.png)；数据：[AC-037-当前产品场景-1440x1000-style.json](AC-037-当前产品场景-1440x1000-style.json)。
- 界限：接口夹具证明实际渲染组件与浏览器 DOM；未模拟真实服务写入，写入效果须以独立产品轮次/后端证据判定。
- product_data_collection_observability: N/A，仅验收取证，不修改产品采集行为；affected_layers: Web 渲染与 Chat 接口夹具；validation: 浏览器断言通过。
