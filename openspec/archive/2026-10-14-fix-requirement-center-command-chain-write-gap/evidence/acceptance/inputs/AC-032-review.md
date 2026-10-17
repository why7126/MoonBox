---
title: AC-032 事实源 stale 提示分层复验
created_at: 2026-10-14 17:04:00
updated_at: 2026-10-14 17:04:00
---

# AC-032 事实源 stale 提示分层复验

结论：前端受控错误响应矩阵通过。被阻断的按钮不产生 Chat turn。

`requirement-center.test.tsx` 在写入型 `req-review` 按钮回传 `workspace_fact_source_stale` 时逐一断言：`local_governance_dirty` 显示阻断文件类别并建议提交或同步事实源；`manifest_mismatch` 显示两侧文件内容不一致、建议同步且明确无需 Git 提交；`git_snapshot_unreadable` 显示检查 Git 状态与服务日志；无 reason 的旧服务响应给标准部署脚本建议。前三种受控样本的 Toast 均不出现统一的“确认标准部署已更新”。本轮新增 Git 快照不可读的 Toast 断言。前端文件完整测试 126/126 通过；后端 `manifest_mismatch` API 响应由 AC-031 的隔离测试核对。

证据边界：三类 Toast 由真实组件加合成 API 响应验证；当前后端实际可产生 `manifest_mismatch` 与 `standard_deployment_outdated`，`local_governance_dirty` 和 `git_snapshot_unreadable` 为兼容原因的 UI 分支测试，本轮未对共享产品制造 Git 损坏。`product_data_collection_observability: applicable`；`affected_layers: [web_runtime, api]`；错误展示测试不采集原始路径或文档正文。
