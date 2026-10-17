---
title: Chat 跨挂载复制窗口归档验收样本设计
created_at: 2026-10-12 08:59:27
updated_at: 2026-10-12 08:59:27
---

# Chat 跨挂载复制窗口归档验收样本设计

## 目标与边界

在产品对象 Chat 中首次执行 `/opsx-archive verify-chat-cross-mount-copy-archive`，验证完整唯一的旧目录与正在复制的同名标准目录短时共存时，轮次继续拥有归档权限，并最终完成标准目录、规格合并及 Workflow Sync。

本 Change 只定义和承载验收证据。BUG-0026 的代码修复保留在 `fix-chat-platform-opsx-archive-source-permission` 的 AF-014 台账。

## 设计决策

1. 在既有 `chat-archive-acceptance-evidence` 能力增加复制窗口场景，不新建重复能力。
2. 归档前完成任务、OpenSpec strict、中文、身份、目录与 Sprint 门禁；归档后核对产品轮次终态、命令退出码、唯一标准归档目录、规格和 Sprint 状态。
3. 如产品轮次中断，保留失败记录；检查三处目录的唯一性后才考虑宿主恢复，恢复不计入产品通过。

## 风险与回退

归档将真实移动本 Change 并合并规格，属于用户已授权的专用验收样本。身份冲突或门禁失败时停止并保留证据。
