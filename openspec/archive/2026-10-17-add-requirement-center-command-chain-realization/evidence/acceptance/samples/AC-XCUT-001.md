---
title: AC-XCUT-001 受理与事实源持久性复验
created_at: 2026-10-13 20:05:00
updated_at: 2026-10-17 16:10:00
status: passed
---

# AC-XCUT-001 受理与事实源持久性复验

结论：通过。此项为横切合同，下面使用三个独立隔离对象覆盖不同故障窗口，不将其写成同一操作或同一轮次。隔离数据库仅作只读核验，未导出正文或凭据。

| 条件 | 真实产品和事实源证据 | 结论 |
|---|---|---|
| HTTP 202 仅代表受理 | 隔离产品请求日志的服务端路由模板统计：Capture 确认 POST 有 3 条 202、整理 POST 有 2 条 202、文档 PUT 有 2 条 202。确认任务另有终态与 Issue 关联，见 [浮层提交轮次](AC-PROTOTYPE-005.md)；因此未以 202 推断完成。 | 通过 |
| 未知终态复用身份 | `REQ-9300-ac013-window-resume` 的 `req-generate` 轮次 `6b2fa52a-a0de-4c00-b155-5045cfcdc025` 在真实 Chrome 关窗、重进后进入 unknown；恢复器按原外部 thread/turn ID 执行 `reconcile_unknown`，读取执行器 completed 后落账同一轮次，未重新发送命令。见 [关窗恢复轮次](AC-013.md)与[脱敏身份摘要](AC-013-window-resume-live.json)。 | 通过 |
| 刷新及重启读取真实文件 | 上述对象 `requirement.md` 落盘、trace 转 draft 后，需求中心刷新进入规划中；隔离 API/Worker 重启后同一轮次完成态与文档入口仍可读，七动作投影重读矩阵同时验证 API 文档字节与文件、registry、CHANGELOG、trace 一致。见 [投影矩阵](AC-013-projection-matrix-readonly.json)。 | 通过 |
| 外部修改阻断恢复 | `REQ-9317-capture` 治理准备后对 `capture.md` 做受控外部修改，产品命令返回 409/2606 `workspace_fact_source_stale`；未创建写入轮次，卡片仍为 captured；原字节随后恢复。见 [事实源门禁](AC-019.md)。该窗口在命令提交前阻断，不冒称执行后的恢复冲突。 | 通过 |

边界：202 样本是 Capture 接口，unknown 样本是 `req-generate`，外部编辑样本是另一 REQ；它们共同验证横切合同，不能用于宣称单一 REQ 连续经历全部故障。
