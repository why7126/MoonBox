---
title: AC-049 产品轮次缺口诊断
created_at: 2026-10-14 17:26:00
updated_at: 2026-10-14 17:26:00
---

# AC-049 产品轮次缺口诊断

- 当前 `test_chat_incomplete_objects.py` 5 项 HTTP 集成回归通过，覆盖 marker-only `.openspec.yaml`、原历史/关联可读、缺文档返回尚未就绪、ACL 与符号链接拒绝。
- `/opsx-propose` 未接入 Chat 真实写入链路，不能要求 completed 产品命令轮次。此项验证的是 marker-only 暂存期间既有 Chat HTTP 历史/关联读取，已由 `TestClient` 对同一 FastAPI 路由和仓库夹具实测。
- 结论：5 项 HTTP 集成回归通过。证据边界：未采集浏览器历史页面视觉；本 AC 没有视觉门禁。
- product_data_collection_observability: N/A，无采集逻辑变更；affected_layers: Chat、治理对象读取；validation: 5 项后端 HTTP 集成回归及只读产品数据库盘点。
