---
requirement_id: REQ-0037-current-iteration-archive-entry
title: 当前迭代容量区域新增归档当前迭代入口
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0031-requirement-center-current-iteration-capacity
created_at: 2026-09-14 23:31:06
updated_at: 2026-09-17 10:24:49
priority: P1
---

# 当前迭代容量区域新增归档当前迭代入口

## 1. 背景与价值

需求中心已经展示当前迭代容量已使用与总容量，并将当前迭代作为团队日常推进、验收和收尾的工作入口。当前用户在容量区域能判断 Sprint 负载，但当一个当前迭代已经投入实际工作量后，还缺少顺手可达的“归档当前迭代”入口。

用户本次明确提出：当当前迭代 `used_capacity > 0` 人天时，在容量条或当前迭代操作区显示归档入口；点击后进入确认流程，并沿用 Sprint archive 既有门禁，不能绕过未归档 Change、验收报告 sign-off、权限和 Workflow Sync 校验。

本需求作为 `REQ-0031-requirement-center-current-iteration-capacity` 的体验补充，重点不是新增一套归档流程，而是在当前迭代上下文中提高 Sprint 收尾入口的可发现性，同时保持治理门禁严谨。

## 2. 目标用户

- 产品负责人：在查看当前迭代容量和范围时，能够发现当前 Sprint 已具备收尾动作入口。
- 项目负责人：在迭代收尾阶段快速进入归档确认流程，并看到未满足门禁的具体原因。
- 研发与测试协作者：理解当前迭代仍有哪些 Change、验收或同步事项阻塞归档，避免误以为容量区域入口可绕过流程。
- 有归档权限的治理维护者：在权限允许时从需求中心发起归档确认，并让归档动作继续受后端与 Workflow Sync 事实源约束。

## 3. 范围

### 3.1 首版包含

- 在当前迭代容量区域或当前迭代操作区提供“归档当前迭代”入口。
- 入口展示条件至少基于当前迭代 `used_capacity > 0` 人天。
- 点击入口后进入归档确认流程，不直接执行 Sprint archive。
- 确认流程复用 Sprint archive 既有门禁，包括未归档 Change、验收报告 sign-off、权限和 Workflow Sync 校验。
- 门禁失败时展示明确失败项，并尽量提供跳转到相关 Change、验收报告或同步修复入口。
- 无归档权限、无当前迭代、容量为 0 或门禁未通过时，不提供可绕过的执行路径。
- 归档成功或失败后，需求中心当前迭代、容量、Scope、验收报告和 Workflow Sync 投影保持一致。

### 3.2 首版不包含

- 不新增独立 Sprint archive 状态机。
- 不新增绕过 `/sprint-archive`、Workflow Sync、OpenSpec Change 归档或验收 sign-off 的快捷路径。
- 不在本需求内改变 Sprint 容量计算、默认容量、显式容量覆盖或人天估算规则。
- 不在本需求内自动归档未完成 Change、自动补签验收报告或自动修复 Workflow Sync 漂移。
- 不在本需求内新增管理后台、微信小程序、移动端或桌面端入口。
- 不在本需求内重做需求中心整体工具栏、卡片阶段动作或 Sprint 筛选模型。

## 4. 功能要求

### FR-001 入口展示条件

当需求中心存在当前迭代，且该迭代 `used_capacity > 0` 人天时，系统应在当前迭代容量区域或当前迭代操作区提供“归档当前迭代”入口。

入口不得仅依赖前端文案、卡片数量或人工标记判断是否展示。容量判断应沿用需求中心当前迭代容量事实源；归档入口启用状态必须基于 Sprint archive readiness 汇总。若容量事实源缺失、无法计算或状态待核实，应避免展示可执行归档入口，并给出轻量说明。

当 `used_capacity = 0`、无当前迭代、当前用户无可见 Sprint、当前迭代解析失败，或 Sprint 范围内任一 REQ、BUG、独立 Change 未归档闭环时，系统不得提供可执行归档入口。后续设计可以选择完全隐藏入口，或展示禁用态和不可用原因；禁用或隐藏时应展示安全摘要，避免泄露不可见资源细节，但不得让用户进入可执行归档路径。

### FR-002 入口位置与视觉表达

入口应靠近当前迭代容量信息，优先考虑容量条相邻操作或当前迭代操作区，确保用户在查看容量时自然发现收尾动作。

当存在多个当前迭代时，每个迭代的归档入口必须能明确对应到具体 Sprint，不能用一个模糊入口让用户误归档其他迭代。若页面空间受限，可使用紧凑按钮、更多操作菜单或单个迭代详情操作，但必须保留 Sprint ID 或等价上下文。

入口视觉权重应低于容量核心数值和异常提示，高于普通辅助链接。归档是高风险操作，入口文案或 icon 必须表达动作含义，不能只用难以理解的符号。

### FR-003 确认流程

用户点击归档入口后，系统应进入确认流程，而不是直接执行归档。确认流程至少应展示：

- 目标 Sprint ID、当前状态和容量摘要。
- 本次归档将进入的 Sprint archive 流程说明。
- 当前门禁检查结果或正在检查状态。
- 归档成功后的主要影响，例如当前迭代从当前视图移出、Scope 和验收报告转入归档事实源。

确认流程应避免大段解释性说明，但必须让用户在执行前能识别目标 Sprint 和风险。用户取消确认后，不应改变 Sprint、REQ、BUG、Change 或 Workflow Sync 状态。

### FR-004 Sprint archive 门禁复用

归档入口必须复用 Sprint archive 既有门禁，不得在前端自行判定通过后直接写入归档结果。前端可根据 readiness 汇总提前隐藏或禁用入口，但最终裁判仍必须是 Sprint archive 后端/脚本门禁。

归档执行前必须确认：

- 当前 Sprint 范围内所有 REQ、BUG 和独立 Change 均已归档闭环。
- 关联 OpenSpec Change 均已完成归档或满足既有 Sprint archive 规则。
- 验收报告完成 sign-off 或满足既有豁免规则。
- 当前用户具备归档权限。
- Workflow Sync 校验通过，且不会绕过 `sprint.md`、`sprint.yaml`、`acceptance-report.md`、`release-note.md` 或 Issue trace 的同步规则。

门禁失败时，系统应展示失败项和修复方向。可跳转到 REQ、BUG、独立 Change、验收报告、Sprint 文档或同步动作入口；不能提供“强制归档”按钮绕过失败项。

### FR-005 权限与安全

归档入口展示与执行必须遵守当前用户权限。无权限用户不能执行归档；如产品选择展示禁用入口，禁用原因应是安全摘要，不泄露不可见 Sprint、Change、验收报告、内部路径、堆栈、密钥或 `.env` 内容。

前端仅作为用户入口和确认流程载体，最终归档权限、门禁结果和状态写入必须以后端或既有治理命令事实源为准。客户端传入的 Sprint ID、行为链路字段或门禁状态不得被服务端作为可信授权依据。

### FR-006 失败恢复与状态一致性

归档确认流程中的门禁检查、执行请求或 Workflow Sync 刷新失败时，页面应保留当前迭代容量和卡片上下文，并展示轻量失败信息。失败不应清空看板、伪装成归档成功或把当前迭代从默认视图移除。

归档成功后，需求中心应刷新当前迭代列表、容量区域、Scope 投影和相关卡片状态。若刷新失败，应提示用户刷新或查看 Sprint 事实源，不能继续展示已归档 Sprint 为当前迭代且不说明状态可能过期。

### FR-007 多当前迭代场景

当存在多个当前迭代时，归档入口应逐个 Sprint 呈现或在确认流程中要求用户明确选择目标 Sprint。系统不得默认选择编号最大、更新时间最新或容量最高的 Sprint 直接进入归档。

每个入口、确认流程和门禁结果都应绑定同一个目标 Sprint。迟到响应不得覆盖用户当前正在确认的目标 Sprint。

### FR-008 测试与文档同步

实现阶段应覆盖入口展示、隐藏或禁用、确认取消、门禁失败、权限拒绝、归档成功、Workflow Sync 失败、多当前迭代和刷新一致性的测试。

如新增或调整 API、OpenAPI、客户端生成类型、请求封装、行为事件、请求日志或 Task Trace，应同步 API、数据采集观测和相关测试。若完全复用既有 Sprint archive API 与观测链路，也应在 Change 文档中说明复用口径和不新增字段的原因。

## 5. UI 约束

- 沿用需求中心现有视觉体系、设计 token、容量指标和工具栏布局。
- 入口应贴近当前迭代容量区域或当前迭代操作区，不新增孤立的说明卡片。
- 归档入口应使用清晰动作文案或熟悉 icon，必要时通过 tooltip 表达“进入归档确认”。
- 高风险确认流程应清楚展示目标 Sprint，不得让用户在多当前迭代场景下误操作。
- 门禁失败信息应可扫描，避免用长段落堆叠所有规则；失败项、状态和修复入口应对齐。
- 窄屏、长 Sprint ID、多当前迭代、无权限和失败态下，文本不得与容量条、按钮、筛选器或卡片内容重叠。
- 禁用态或失败态不得只依赖颜色表达，应提供文本或 tooltip 辅助。

## 6. 关联需求

- REQ-0012-frontend-requirement-center：需求中心页面、卡片、筛选、当前迭代和文档入口基础。
- REQ-0031-requirement-center-current-iteration-capacity：父需求，提供当前迭代容量区域和容量口径。
- REQ-0034-requirement-center-default-current-iteration-cards：需对齐当前迭代识别、多个当前迭代和归档后默认范围刷新。
- Sprint archive 既有流程：本需求必须复用其未归档 Change、验收报告 sign-off、权限和 Workflow Sync 门禁。

## 7. 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 本需求新增 Web 端高风险归档入口和确认流程，预计涉及归档按钮点击、门禁检查、权限拒绝、归档执行请求和 Workflow Sync 结果刷新。Sprint archive 属于多步骤高风险写操作，应复用或补齐请求日志与任务链路观测。
  validation: 实现阶段需验证入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败的行为事件与请求日志只记录脱敏摘要；若归档执行复用既有 task_traces，应验证 trace/span 能定位校验、归档、同步和失败节点；不得记录完整文档正文、本机路径、Authorization、Cookie、密钥、真实 .env 或未脱敏错误堆栈。
```

## 8. 当前状态

```yaml
status: done
lifecycle_stage: review
iteration: sprint-007
openspec_changes:
  - add-current-iteration-archive-entry
generated_at: 2026-09-14 23:31:06
completed_at: 2026-09-14 23:35:53
reviewed_at: 2026-09-14 23:41:21
approved_at: 2026-09-14 23:41:21
last_refined_at: 2026-09-14 23:51:28
source_material:
  - capture.md
  - rules/requirement-management.md
  - docs/standards/product-data-collection-observability.md
  - REQ-0031-requirement-center-current-iteration-capacity/requirement.md
  - REQ-0034-requirement-center-default-current-iteration-cards/requirement.md
next: /opsx-apply REQ-0037-current-iteration-archive-entry
```
