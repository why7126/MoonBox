---
req_id: REQ-0049-sprint-archive-chat-entry
title: 迭代归档接入 Sprint 对象会话与命令预填
status: done
priority: P1
created_at: '2026-10-21 17:44:51'
updated_at: 2026-10-21 22:35:28
owner: 产品团队
source: 用户确认 explore 结论及需求归属
captured_via: req-capture
lifecycle_stage: plan
parent_requirement: REQ-0037-current-iteration-archive-entry
related_requirements:
- REQ-0039-requirement-center-card-chat-session-reuse
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 涉及 Sprint 对象会话解析、复用或创建、命令预填及归档工作流入口；本次仅采集需求，不实施接口或数据库变更。
  validation: 后续验证入口点击、会话复用/创建、项目隔离、预填不自动发送和归档门禁执行；观测仅记录脱敏对象及链路标识，不记录完整草稿。对象存储、部署与管理端本次不新增能力。
---

# 迭代归档接入 Sprint 对象会话与命令预填

## 一句话

Sprint 内所有对象已完成后，允许从归档按钮进入该 Sprint 的 Chat 对象会话，预填归档命令，由用户发送后执行最终归档检查。

## 原始描述

Sprint 内所有对象已完成后允许发起归档，点击归档按钮直接进入 Chat 工作台，复用已有 SPRINT 对象会话，没有则创建，输入框自动填入 `/sprint-archive sprint-xxx`，不自动发送；验收签署等最终归档门禁在命令执行时检查。

## 已确认范围

- 归档入口位于需求中心当前迭代容量区域，沿用用户截图标注的归档按钮位置与现有页面布局。
- 判断该 Sprint 完整范围内的 REQ、BUG 与 Change 是否全部完成，不以页面搜索或筛选后的可见对象代替完整范围。
- 全部对象完成后可发起归档会话；验收签署不再作为进入会话的前置条件，最终归档仍执行签署、权限和 Workflow Sync 等门禁。
- 点击后直接进入 Chat 工作台，以 SPRINT 为对象身份，并携带当前项目和具体 Sprint ID。
- 优先复用该对象已有可用会话；不存在时创建并关联。复用策略承接 REQ-0039，避免重复点击创建重复会话。
- 输入框预填具体 Sprint 的归档命令，不自动发送、不自动创建执行轮次、不将跳转视为归档成功。
- 权限、对象执行中保护、已有草稿保护与最终归档后状态刷新在需求完善阶段展开。

## 现状依据与探索结论

- 用户提供的截图标注了当前迭代容量区域的归档图标。
- 本会话浏览器只读观察：需求中心可见对象均已完成，两个 Sprint 入口仍因验收 sign-off 缺失禁用。该观察用于说明入口与执行门禁耦合，不代替每个 Sprint 完整范围的最终校验。
- `src/backend/app/services/requirement_center.py` 的归档就绪计算将 sign-off 与范围完成共同作为入口门禁。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的迭代归档确认仅显示手动执行命令提示；卡片动作已有对象会话及 Chat 跳转链路。
- `src/backend/app/governance/preparation.py` 的对象会话准备需补齐 SPRINT 身份与 sprint-archive 动作支持。

## 重复检查与归属

- REQ-0037 已交付当前迭代归档入口，本次为其入口行为与门禁分层增强。
- REQ-0039 已交付 REQ/BUG/CHANGE 会话复用，本次关联并扩展至 SPRINT。
- 用户明确选择作为 REQ-0037 的新子需求并关联 REQ-0039；保留两条历史归档事实，不重新打开原需求。
- 保持单条需求：入口可用条件、对象会话、命令预填和最终门禁共同构成一个可独立验收的迭代归档入口交付单元。
- 初判 P1：直接影响迭代闭环效率与上下文连续性，后续评审可调整。

## 建议验收方向

1. 全范围对象完成、验收签署未完成时，仍可点击进入 Sprint 会话；发送命令后执行最终门禁。
2. 仍有未完成对象时不可发起；搜索、筛选隐藏未完成对象不会改变判断。
3. 已有可用 Sprint 会话时复用，没有时创建；跨项目同编号 Sprint 不串会话。
4. 输入框包含目标 Sprint 的完整归档命令，不自动发送，不静默丢失已有草稿。
5. 重复点击、会话执行中、无权限和请求失败均有明确反馈，不产生重复执行。
6. 点击入口不改变 Sprint 归档状态；最终成功或失败后展示真实状态。

## 待澄清

- 后续需求生成明确空 Sprint、对象状态未知、容量缺失时的入口状态，以及非空草稿的合并/替换交互。
- 核对 SPRINT 对象关联已有数据模型是否可复用；本次不预设数据库迁移。

## 非目标

不自动发送归档命令，不绕过最终归档门禁，不在采集阶段开发代码、创建 Change 或纳入 Sprint。
