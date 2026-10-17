---
title: AC-034 真实仓库工作区模式复验
created_at: 2026-10-14 17:04:00
updated_at: 2026-10-14 17:04:00
---

# AC-034 真实仓库工作区模式复验

结论：通过已有隔离产品真实轮次及后端测试。

单项验收脚本核对共享本地产品既有 BUG-0037 Generate turn `bfaba014-622d-4099-8fe4-0aebeb4524e6` 完成命令，关联会话 `workspace_id=source`。独立交叉核对的隔离产品仓库绑定显式为 `workspace_mode: source`：BUG-1001 Generate turn `6a66a033-9e73-425b-9458-0f36f8318091` completed，会话 `workspace_id=source`；候选 applied，application applied/verified。隔离事实源存在相对路径 `issues/bugs/plan/BUG-1001-bug-0025/bug.md`，对应会话副本目录不存在；文件 SHA-256、轮次状态与数据库关联的脱敏核对见 `AC-033-035-product-audit.json`。两轮来自不同数据库，不混称同一轮；本轮没有重复写入事实源。

`test_source_workspace_mode_generate_writes_directly_without_second_apply`、执行器 source 身份与 worker 可写挂载测试通过；测试确认同一源目录读取、直接写入、无二次人工应用。`product_data_collection_observability: applicable`；`affected_layers: [executor, governance, db_projection]`；无新 DB schema、API schema 或安全配置变化。
