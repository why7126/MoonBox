---
title: Chat 关联 Issue 首次归档复验夹具设计
created_at: 2026-10-12 13:16:40
updated_at: 2026-10-12 13:29:23
---

# Chat 关联 Issue 首次归档复验夹具设计

## 背景与现状

BUG-0040 已在产品中迁移 Change 和 Issue，但归档轮次终态 stopped；关联 Issue 的同轮成功证据仍缺。

## 方案

以已评审且纳入 sprint-009 的 BUG-0042 虚拟夹具为主对象，建立关联 Change，完成归档前任务与交付证据门禁。随后由真实产品 Chat 执行首次归档，核对命令、目录、规格、Workflow Sync 和 Issue promote 的同轮结果。

## 测试策略

先验证 OpenSpec strict、语言、身份、Sprint、交付证据与关联 Issue 归档过渡权限；产品执行结果在 BUG-0026 验收文档回填。

## 风险与回滚

归档会真实移动本测试夹具和关联 Issue。仅在授权的专用样本执行；中断时保留原始状态和证据，禁止将宿主续跑记为产品首次成功。
