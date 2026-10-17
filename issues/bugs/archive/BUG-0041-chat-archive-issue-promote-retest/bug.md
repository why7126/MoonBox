---
bug_id: BUG-0041-chat-archive-issue-promote-retest
title: Chat 关联 Issue 首次归档复验夹具
status: done
severity: low
owner: MoonBox 产品团队
discovered_at: '2026-10-12 13:13:56'
environment: local
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
related_requirement: null
related_change: null
created_at: 2026-10-12 13:13:56
updated_at: 2026-10-12 13:36:39
---

# Chat 关联 Issue 首次归档复验夹具

## 现象与范围

这是 BUG-0026 AC-001 的授权验收夹具，不是独立生产缺陷。目标是让关联 Issue 在产品首次归档轮次完成规格合并、状态同步和 Issue 阶段迁移。

## 复现步骤

1. 按正式治理链路准备本夹具与纯治理 Change。
2. 在 source 模式 MoonBox 需求中心进入本 Issue 对象 Chat，并首次归档关联 Change。
3. 逐项核对脚本退出码、轮次终态、Change 及 Issue 目录与 Sprint 事实源。

## 期望与实际

期望同轮完成并留证。BUG-0040 产品轮次已对账为 stopped，本复验样本尚未执行，实际结果待首次归档。

## 影响与分级

仅本地验收数据；severity=low 是夹具标识，不描述客户影响。此前 BUG-0026 的真实缺陷和产品证据仍由原 Issue 承载。

## 根因状态

本对象不主张新的缺陷根因。待验证的证据缺口是关联 Issue 的首次归档与 promote 同轮；BUG-0026 Change 的既有 root-cause 和 AF-015 记录承载产品修复根因。
