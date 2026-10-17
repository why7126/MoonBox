---
title: Chat 归档收尾窗口归档验收样本设计
created_at: 2026-10-12 09:09:37
updated_at: 2026-10-12 09:09:37
---

# Chat 归档收尾窗口归档验收样本设计

## 目标与边界

在产品对象 Chat 中首次执行 `/opsx-archive verify-chat-archive-finalize-window`，验证轮次从标准目录和规格合并继续运行到 Workflow Sync、命令完成和终态；若中断，保留原始原因码。

本 Change 只定义和承载验收证据。BUG-0026 的代码修复与诊断改进保留在 `fix-chat-platform-opsx-archive-source-permission` 的 AF-014/AF-015 台账。

## 设计决策

1. 在既有 `chat-archive-acceptance-evidence` 能力增加收尾窗口场景，不新建重复能力。
2. 归档前完成任务、OpenSpec strict、中文、身份、目录与 Sprint 门禁；归档后核对产品轮次终态、命令退出码、唯一标准归档目录、规格和 Sprint 状态。
3. 如产品轮次中断，保留失败记录；检查三处目录的唯一性后才考虑宿主恢复，恢复不计入产品通过。

## 风险与回退

归档将真实移动本 Change 并合并规格，属于用户已授权的专用验收样本。身份冲突或门禁失败时停止并保留证据。
