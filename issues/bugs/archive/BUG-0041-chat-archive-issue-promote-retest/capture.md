---
bug_id: BUG-0041-chat-archive-issue-promote-retest
title: Chat 关联 Issue 首次归档复验夹具
status: done
created_at: '2026-10-12 13:13:36'
updated_at: 2026-10-12 13:36:40
severity: low
environment: local
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
source: 用户授权的 BUG-0026 AC-001 专用验收夹具
---

# Chat 关联 Issue 首次归档复验夹具

## 现象

这是用户明确授权的测试夹具，不代表新发现的产品缺陷。BUG-0026 已有纯治理 Change 在产品首次归档成功，但缺关联 Issue 在同一首次归档轮次完成阶段迁移的证据。

## 复现与验收操作

1. 建立仅含治理规格的关联 Change，按正常评审、Sprint、OpenSpec 和 apply 门禁准备。
2. 从需求中心进入该 Issue 对象 Chat，首次发送归档命令。
3. 核对同一产品轮次的规格合并、Change 移动、Workflow Sync、Issue promote 与最终完成状态。

## 期望与实际

期望：验收夹具按标准流程归档并保留可复核证据。实际：BUG-0040 产品轮次已对账为 stopped，本复验夹具尚未执行；本对象只用于补齐 BUG-0026 AC-001，不计作独立生产缺陷。

## 判重与边界

BUG-0026 是被验收的真实缺陷，BUG-0040 首次归档已实际移动，但产品轮次最终 stopped，不能用于 AC-001 签收；BUG-0036 是 Bug 生成链路夹具且声明不纳入 Sprint。本夹具专门验证首次归档的关联 Issue promote；目的、触发阶段和证据与 BUG-0036 不同，关联 BUG-0026。
