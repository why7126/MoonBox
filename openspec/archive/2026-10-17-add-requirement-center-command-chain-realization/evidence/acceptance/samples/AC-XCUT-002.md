---
title: AC-XCUT-002 开始、进度与完成分离复验
created_at: 2026-10-13 20:05:00
updated_at: 2026-10-17 15:43:00
status: passed
---

# AC-XCUT-002 开始、进度与完成分离复验

隔离项目 `moonbox-validation` 的完整对象 `REQ-9105-governance-sprint-zero-active`、Change `add-isolated-project-connection-status` 提供同对象三阶段事实；[AC-007 原始轮次记录](AC-007.md)及其脱敏截图是本项复用的真实产品证据。

| 阶段 | 轮次或同步事实 | 卡片和治理事实 |
|---|---|---|
| 启动，0/11 | `/opsx-apply` 轮次 `be251e47-a0e1-4b10-870d-e91cf1058f11` 执行 `opsx.start`；轮次后因额度停止，不将受理当成完成 | Change `in_progress`、`started_at` 已记录、`completed_at: null`；卡片“研发中”“研发 0/11”“查看进度” |
| 任务进度 | 续接轮次 `eb5ff07b-3a7f-4f39-9e0d-72f6e974b1fa` 完成 1/11；后续隔离实施推进到 6/11 | `opsx.progress` 后 Change 仍 `in_progress`，卡片显示“研发中”“研发 6/11”“查看进度”，不是 applied |
| 实施完成 | 同一 Change 任务 11/11、验证及交付记录齐全后才执行 `opsx.apply` Workflow Sync，退出码 0 | `status: applied`、`completed_at` 真正写入，卡片进入“验收中”；没有自动归档 |

另用 `REQ-9104-review-approve` 的[已登录 0/12 卡片截图](../visual/AC-007-real-product/requirements-development-1440-20261014.png)交叉核对：轮次 `a14c0a85-98b6-4f92-97a8-66b51d4a3d88` 的 `opsx.start` 已落盘而 Chat 终态为 stopped，卡片仍按文件事实显示研发中；任务临时全勾但缺证据时，独立轮次 `a7b8320e-81eb-48fb-a8d7-80cf36fd9413` 拒绝 `opsx.apply`。

自动验收当前可只读核验的 completed `opsx-apply` 轮次为 `903b6ef7-5940-4c15-b024-a73e8a3d085f`；上述较早的 `REQ-9105` 启动轮次已不在当前隔离数据库中，保留其原始脱敏记录与截图，不把当前 DB 查询伪称为对历史轮次的直接重读。这个当前轮次仅作为命令执行身份的机器复验，三阶段语义仍以 `REQ-9105` 原始同对象证据为准。

历史兼容负向只做只读核对：隔离项目规范归档内旧 Change `build-api-standard` 的 trace 已标记 `archived` 且没有 `execution.started_at`；读取时没有为其写入虚构启动时间。`tests/unit/test_workflow_execution.py` 的旧状态投影回归在 2026-10-17 为 14/14 通过，退出码 0。此项是合成兼容回归，不冒充旧 Change 当年的产品轮次。

结论：**passed**。启动、进度和完成分别由实际命令及文件事实决定，旧终态仍可读取且不补造历史时间。
