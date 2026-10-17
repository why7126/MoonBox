---
title: AC-033 当前治理投影同步与同会话续接复验
created_at: 2026-10-14 17:04:00
updated_at: 2026-10-14 17:04:00
---

# AC-033 当前治理投影同步与同会话续接复验

结论：通过。当前文件 manifest/revision 决定写入准备，无关未提交文件不单独阻断；版本变化和工作区未应用修改仍拒绝覆盖。

共享本地产品既有 BUG-0037 专用对象同一会话中，`bug-generate` turn `bfaba014-622d-4099-8fe4-0aebeb4524e6` 与后续 `bug-complete` turn `f946c910-5c33-4f19-89ee-aa0beb41223f` 均 completed；对应候选与 application 为 applied/verified，详情见 `AC-033-035-product-audit.json`。该产品轮次绑定 source 模式；隔离副本模式的同步行为由后端测试核对，不能把此产品轮次称为副本模式。

`test_governance_candidates.py` 覆盖无 `.git` 治理投影、未提交事实源、全写入命令同步、隔离工作区当前文件基线、版本变化与未应用工作区修改拒绝覆盖；所有测试通过。`product_data_collection_observability: applicable`；`affected_layers: [api, executor, governance, chat_events]`；未改数据库或客户端生成物。
