---
bug_id: BUG-0069-chat-interrupted-successor-proof-missing
title: Chat 中断缺少旧同步证明导致外部接续完成后仍受限
status: done
severity: high
created_at: '2026-10-27 16:37:42'
updated_at: 2026-10-27 18:44:32
owner: 产品团队
environment: local docker
related_requirement: null
related_bug: BUG-0061-cross-entry-continuation-guard-convergence
lifecycle_stage: archive
---

# Chat 中断缺少旧同步证明导致外部接续完成后仍受限

## 现象与复现

BUG-0056 的 Chat apply 轮次已停止，缺少正式同步成功证明。外部 Codex 接续完成后，研发6/6、测试7/7、验收8/8，但需求卡片仍“结果待核对”，仅显示查看执行；状态详情最近核验06:57:57。步骤：Chat中断且未形成同步证明→外部完成实现、正式同步和验收→打开需求中心并展开状态详情。

## 期望与实际

期望保留旧执行历史，通过独立后继完成证据核验解除当前对象限制；实际现有入口与后端均依赖旧成功同步证明，不能进入恢复。

## 判重与授权

原BUG-0061已归档，用户于2026-10-27明确授权新建关联BUG承接本次复发，并复用已有根因、8项验收和本次复发评审，继续Sprint规划。保留原归档历史。本次只处理无旧同步证明分支，保持一条，不复制历史dry-run修复或BUG-0056性能范围。

## 证据来源

来源为BUG-0061 capture.md的2026-10-27补证、root-cause.md R1至R6及review.md本次复发评审。用户截图codex-clipboard-c03d9ee4-af24-4c87-b0fc-f8e9b13691e3.png留在对话。新建文档不代表重跑现场或解除保护。
