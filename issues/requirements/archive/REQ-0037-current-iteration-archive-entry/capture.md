---
req_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
status: done
created_at: '2026-09-14 23:15:32'
updated_at: 2026-09-17 10:24:49
recorded_by: product
source: 用户反馈
parent_requirement: REQ-0031-requirement-center-current-iteration-capacity
priority: P1
---

# 一句话
在当前迭代容量区域为已有工作量的迭代提供“归档当前迭代”入口，并复用 Sprint archive 的全部既有门禁与同步校验。

# 原始描述
当前迭代容量区域新增归档当前迭代入口：当当前迭代 used_capacity 大于 0 人天时，在容量条或当前迭代操作区显示归档入口；点击后进入确认流程并沿用 Sprint archive 既有门禁，不能绕过未归档 Change、验收报告 sign-off、权限和 Workflow Sync 校验。

# 背景与范围
- 来源：用户通过 `/req-capture` 提出需求。
- 当前需求中心已展示当前迭代容量已使用与总容量；当迭代已有工作量时，用户需要从同一上下文发现归档当前迭代的入口。
- 入口展示条件为当前迭代 `used_capacity > 0` 人天；入口位置可在容量条或当前迭代操作区，后续需求细化阶段确认最终 UI 承载。
- 点击入口后进入确认流程，不直接执行归档；必须沿用 Sprint archive 既有门禁，不新增绕过路径。
- 必须保留未归档 Change、验收报告 sign-off、权限和 Workflow Sync 校验，不因前端入口新增而降低归档条件。
- 初判 P1：该入口影响当前 Sprint 闭环路径的可发现性，并涉及归档门禁、权限与 Workflow Sync 追溯；属于迭代治理体验增强。
- 本条作为 `REQ-0031-requirement-center-current-iteration-capacity` 的当前迭代容量区域 refinement 单独记录，不改写父需求状态。

# 待澄清
- [ ] 入口最终放在容量条内还是当前迭代操作区；需结合 1440px 与窄视口空间确认。
- [ ] 确认流程需要展示哪些门禁检查结果、失败原因和跳转修复入口。
- [ ] `used_capacity = 0` 或无当前迭代时入口是否完全隐藏，还是以禁用态提示归档不可用原因。

# 建议验收方向
- 当前迭代 `used_capacity > 0` 人天时，容量区域或操作区可发现“归档当前迭代”入口；`used_capacity = 0` 或无当前迭代时不提供可执行归档入口。
- 点击入口进入确认流程，且不会绕过未归档 Change、验收报告 sign-off、权限和 Workflow Sync 校验。
- 门禁失败时给出明确失败项和修复入口；门禁通过后才允许继续归档动作。
- 无归档权限的用户不能执行归档；UI 状态与后端权限结果保持一致。
- 归档成功或失败后，当前迭代、容量、Scope、验收报告和 Workflow Sync 投影保持一致。

# 探索结论
当前仅完成需求采集；后续需通过 `/req-explore` 或 `/req-generate` 明确 UI 承载、确认流程、权限反馈和 Sprint archive 门禁复用细节。

# 影响层与观测
- product_data_collection_observability: applicable
- affected_layers: [web, request_logs, task_traces]
- reason: 需求涉及 Web 端归档入口和 Sprint archive 高风险多步骤操作。若后续实现复用既有归档 API 与观测链路，可不新增数据结构；但 PRD 与 Change 必须声明行为入口、请求日志、Task Trace 或明确复用现有链路的 N/A 原因。
- validation: 需求生成阶段需补充入口点击、权限拒绝、门禁失败、归档成功和 Workflow Sync 同步的验证摘要；参考 `docs/standards/product-data-collection-observability.md`。
