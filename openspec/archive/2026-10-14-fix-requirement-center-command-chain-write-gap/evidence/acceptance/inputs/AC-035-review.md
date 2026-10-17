---
title: AC-035 真实仓库模式治理与恢复门禁复验
created_at: 2026-10-14 17:04:00
updated_at: 2026-10-14 17:04:00
---

# AC-035 真实仓库模式治理与恢复门禁复验

结论：受控后端回归与隔离产品轮次联合通过；串行冲突、撤权和未知任务恢复为合成回归，未在共享工作区制造并发冲突。

单项验收脚本核对共享本地产品既有 BUG-0037 Generate turn `bfaba014-622d-4099-8fe4-0aebeb4524e6`；独立交叉核对的隔离 BUG-1001 source 模式真实轮次 completed，候选与 application applied/verified，存在 Task Trace 与执行工具事件，事实源文件存在且无会话副本，见 `AC-033-035-product-audit.json`。两轮来自不同数据库。`test_chat.py` 的项目锁、成员撤权、source 工作区身份、会话删除、diff 状态、未知任务恢复及脱敏观测测试，与 `test_governance_candidates.py` 的对象状态、固定产物 allowlist 和项目级串行应用测试均通过；`test_chat_platform.py` 确认 source 挂载可写且权限配置独立。三文件合计 117 passed、1 skipped；当前 Change 的五项复验新增测试另行单项运行。

`product_data_collection_observability: applicable`；`affected_layers: [api, executor, governance, request_logs, task_trace, board_projection]`。请求日志与 Task Trace 只核对数量及脱敏字段，不写入原始 prompt、令牌、源路径或客户数据。未改 DB schema 或客户端生成物。
