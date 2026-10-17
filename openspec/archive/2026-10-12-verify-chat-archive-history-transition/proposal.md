---
title: Chat 归档历史引用过渡验收样本提案
created_at: 2026-10-12 09:25:51
updated_at: 2026-10-12 09:25:51
---

# Chat 归档历史引用过渡验收样本提案

## 背景与原因

BUG-0026 的上轮产品归档在 CLI 旧目录阶段因历史引用再授权中断；宿主恢复不构成产品首次归档成功。用户已授权专用纯治理样本，需复验 AF-015 修复。

## 变更内容

- 在既有归档验收证据能力补充历史引用过渡期的判定。
- 本 Change 事前完成治理任务和门禁，供产品对象 Chat 首次归档。
- 核对轮次终态、命令结果、标准目录、规格和 Workflow Sync；中断与恢复分开记载。

## 能力范围

### 修改能力

- `chat-archive-acceptance-evidence`：补充旧目录阶段历史引用授权的验收规则。

## 影响范围

仅治理文档与归档后规格。`product_data_collection_observability: N/A`，`affected_layers: []`；本 Change 不改变 API、DB、请求日志、行为事件、Task Trace、Web 请求封装、UI、部署、安全实现或客户端生成。验证只核对既有轮次脱敏状态和文件事实源。
