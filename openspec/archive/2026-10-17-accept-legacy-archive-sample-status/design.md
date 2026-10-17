---
title: 历史归档验收样本状态兼容设计
created_at: 2026-10-17 17:00:00
updated_at: 2026-10-17 17:00:00
---
# 历史归档验收样本状态兼容设计

## 背景与目标

历史归档计划含 `completed-source-archive`；当前计划解析拒绝该值，Sprint 关闭同步中断。保留原归档文件及完整验收 manifest。

## 技术决定

计划解析仅在 canonical `openspec/archive/` 目录允许此精确历史值；活动 Change 仍拒绝。验收勾选投影将该值视为需通过原 manifest 与附件哈希核验的已完成样本，不能仅凭状态文字标记通过。聚焦测试覆盖归档正例、活动负例和证据失效负例。

## 影响边界与验证

仅治理脚本与测试。`product_data_collection_observability: not_applicable`；`affected_layers: []`；原因：不修改 API、DB、request_logs、usage_events、Task Trace、Web 或请求封装。验证：聚焦单元回归、原 Sprint 同步重试及归档就绪门禁。
