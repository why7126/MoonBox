---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档权限与工具路径修复评审
status: done
created_at: 2026-10-09 10:53:00
updated_at: 2026-10-13 18:51:16
owner: 产品团队
---

# 产品内纯治理 Change 归档权限与工具路径修复评审

## 评审结论

通过，确认按关联 BUG 单独修复。用户已明确要求新建关联 BUG 并继续修复产品内归档；本评审不表示已修复或已进入 Sprint。

## 评审依据

| 检查项 | 结论 |
|---|---|
| 可复现与根因 | root-cause.md 为 confirmed，七项证据包含原轮次权限决策、工具退出结果、代码路径和镜像探针。 |
| 严重等级 | high：产品内正式归档闭环受阻，但宿主标准脚本可安全完成目标 Change；未见数据损坏。 |
| 回归验收 | AC-001 至 AC-005 覆盖纯治理授权、负向权限、真实沙箱 PATH、隔离归档和产品真实观察。 |
| 范围与关联 | BUG-0026 仅覆盖 REQ/BUG 来源；本条为纯治理主对象与命令路径，关联但不重复。 |
| 热修路径 | 不放宽普通治理 profile，不跳过 OpenSpec；先纳入有容量的 active Sprint。 |

## 数据采集与链路观测

`product_data_collection_observability: applicable`，涉及既有 Chat 权限决策、请求日志与任务轨迹核对；本次评审不新增采集字段。验证摘要见 acceptance.md，未触碰 API、DB 结构、UI 或客户端生成。
