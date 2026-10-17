---
requirement_id: REQ-0027-requirement-center-command-chain-realization
title: 需求中心卡片全命令产品链路真实化
status: done
created_at: '2026-09-12 21:11:40'
updated_at: 2026-10-17 16:21:01
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
previous_requirement_id: REQ-0027-capture
priority: P1
---

# 需求中心卡片全命令产品链路真实化

## 原始描述

需求中心卡片全命令产品链路真实化：分析命令打开只读 Chat；生成、完善、评审、入迭代、生成 OpenSpec、开始开发、完成归档分别接入后端 controller、文件事实源写入、Workflow Sync 状态流转和回归断言。

## 背景

原 REQ-0027-capture 来自 BUG-0014 的部署验收测试记录，用于证明 Capture 创建、刷新、文档读取和持久化可用。用户本次明确要求直接使用 REQ-0027，并将其更新为需求中心卡片全命令产品链路真实化需求。

## 目标

- 需求中心卡片上的分析命令只打开只读 Chat，不写入需求、Sprint、OpenSpec 或归档事实。
- 生成、完善、评审、入迭代、生成 OpenSpec、开始开发、完成归档等命令入口接入后端 controller。
- 每个命令入口按现有治理流程写入对应文件事实源，并触发 Workflow Sync 完成状态流转。
- 为上述命令链路补齐回归断言，覆盖前端入口、后端控制器、文件写入和状态同步结果。

## 非目标

- 本记录不绕过 REQ 评审、Sprint 纳入或 OpenSpec Change 门禁。
- 本记录不直接修改 `src/`、`openspec/` 或 Sprint 四件套。
- 本记录不扩大到 BUG 卡片或独立 Change 卡片，除非后续 PRD 或 OpenSpec 明确纳入。

## 待澄清

- [ ] 后续 PRD 需确认每个卡片命令的具体按钮文案、禁用态、权限错误提示和只读 Chat 参数。
- [ ] 后续 OpenSpec 需声明 API、文件写入、Workflow Sync、Task Trace 或行为观测的适用范围与验证方式。

## 探索结论

（/req-explore 后人工确认写入）
