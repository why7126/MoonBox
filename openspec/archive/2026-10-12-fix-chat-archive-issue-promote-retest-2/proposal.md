---
title: Chat 关联 Issue 首次归档复验夹具提案
created_at: 2026-10-12 13:16:40
updated_at: 2026-10-12 13:16:40
---

# Chat 关联 Issue 首次归档复验夹具提案

## 背景

BUG-0042-chat-archive-issue-promote-retest-2 是用户授权的虚拟验收样本，用于验证关联 Issue 的产品首次归档与阶段迁移；不代表新生产缺陷。

## 变更内容

补充中断后独立复验的证据规则。归档前完成任务和门禁，产品轮次核对规格合并、唯一目录、Workflow Sync、Issue promote 和最终状态。

## 能力影响

修改 `chat-archive-acceptance-evidence` 的验收要求。

## 影响范围

仅治理文档和已生效规格。数据采集与链路观测 N/A，`affected_layers: []`；API、DB、UI、部署、安全和客户端生成均不涉及。验证复用脱敏轮次事件与文件事实。

## 回退方案

归档前保留活动 Change；归档失败时按唯一事实源续跑，并把宿主恢复单独记录。
