---
title: AC-023 执行器预检与治理校验错误分类复验
created_at: 2026-10-14 15:00:00
updated_at: 2026-10-14 15:00:00
---

# AC-023 执行器预检与治理校验错误分类复验

结论：通过。两条异常路径在真实后端产品 API 与候选终态中得到不同错误码；聚焦回归 3 passed。

## 执行器不可用：隔离产品 39101/39102

在专用隔离数据中建立 captured 测试对象 `BUG-1003-ac-023-preflight`，通过产品 `governance-preparations` API 生成候选 `1913da4c-1e2b-5192-9c5e-d1458b6e9d2a`。仅停用隔离 Chat Worker，随后通过同一产品的发送 API 提交 `/bug-generate BUG-1003-ac-023-preflight`。响应为 HTTP 503、业务码 2505、`kind=executor_unavailable`，消息明确指出“执行器 sandbox/dry-run 预检未通过”。候选记录为 `prepared/executor_unavailable`，会话执行轮次为 0，证明阻断发生在入队与执行前。隔离 Worker 已立即恢复，后端健康；测试管理员原密码哈希已恢复。

## 治理候选不合规：共享产品 39002

既有真实产品 `/bug-generate BUG-0036-bug` 轮次 `9c06a865-0e53-4fde-910c-45dd953041c4` 已完成执行；候选 `a4a6c11f-7232-5a37-8e94-607d2e3bf31c` 为 `rejected/governance_validation_failed`，无 application。真实浏览器历史页显示轻量“治理结果未通过校验”提示，截图及历史入口记录见 `AC-020-review.md`。该路径发生在执行完成后的候选收集与治理边界校验，不是执行器不可用。

## 回归与分类核对

`src/backend/tests/test_governance_candidates.py` 三个聚焦测试通过：`test_preflight_marks_executor_unavailable_before_send`、`test_source_workspace_rejected_candidate_restores_governance_facts`、`test_completion_rejection_exposes_only_fixed_rule_identifier`。发送入口 `request_turn` 先调用 `check_send`，再进入 `enqueue`；前者在 Worker 不可用时写入候选 `executor_unavailable` 并抛出同 kind 错误。完成后的治理候选拒绝归入 `governance_validation_failed`，两者没有被折叠为同一错误。

证据边界：执行器不可用发生于发送前，因此按设计没有 turn ID；验收计划中的产品 turn ID 归属治理校验失败路径。隔离测试对象和产品数据库只用于本地取证，不作为仓库交付文件。
