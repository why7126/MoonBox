---
title: AC-031 写入前事实源门禁复验
created_at: 2026-10-14 17:04:00
updated_at: 2026-10-14 17:04:00
---

# AC-031 写入前事实源门禁复验

结论：后端受控 API/数据库门禁通过。被阻断的发送没有产品 turn，因此验收计划以命令型负向检查记录，不虚构一个完成轮次。

`test_governance_candidates.py` 使用隔离临时 source_root、治理投影和 SQLite：完整对象 ID、registry path、trace status、必需文档缺失或不一致时，`prepare_object_session` 返回治理校验失败，会话和 turn 数仍为 0；source_root 与投影当前文件 revision 不一致时，`/api/v1/chat/object-sessions` 返回 409 `workspace_fact_source_stale / manifest_mismatch`，响应不含源路径和对象 ID，数据库仍无会话或 turn。只读 `req-explore` 在事实源存在未提交文件时仍可创建会话。前置门禁按 `source_root` 与投影当前文件快照核对，非以 Git 提交与否作为单独阻断条件；当文件经同步可被执行器看到时符合 AC-033 的允许语义。

本轮新增 registry path、trace status、必需文档三个无会话断言，以及 stale API 无会话/turn 断言。复验命令为 `src/backend/.venv/bin/python -m pytest -q src/backend/tests/test_governance_candidates.py`。`product_data_collection_observability: applicable`；`affected_layers: [api, governance, chat_events]`；验证包含响应脱敏与无执行记录。未改 DB schema、API schema 或部署配置。
