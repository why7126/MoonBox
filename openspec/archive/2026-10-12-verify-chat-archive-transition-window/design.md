---
title: Chat 归档迁移窗口验收样本设计
created_at: 2026-10-11 11:30:53
updated_at: 2026-10-11 11:30:53
---

# Chat 归档迁移窗口验收样本设计

## 目标与边界

使用已授权的纯治理替代样本，验证 `/opsx-archive verify-chat-archive-transition-window` 在产品对象 Chat 内首次执行时，权限不因 CLI 临时旧目录而撤销，并由标准脚本完成唯一标准归档、规格合并和 Workflow Sync。

本 Change 不修改产品代码、环境或运行数据。BUG-0026 的实现修复和回归留在 `fix-chat-platform-opsx-archive-source-permission` 的 AF-013 台账中。

## 设计决策

1. 在既有 `chat-archive-acceptance-evidence` 能力中补充迁移窗口证据规则，避免再新建重复能力。
2. 任务和交付证据先完成，再从产品对象会话执行归档；最终证据分别记录 CLI 临时目录、标准目录、命令退出码和轮次终态。
3. 如中断，先确认 active、旧归档、标准归档是否唯一，再按项目标准脚本恢复，不把恢复计作产品通过。

## 风险与回退

归档会真实移动本 Change 并修改已生效规格；用户已授权专用样本验收。目录或身份冲突时停止，保留全部文件供核对。
