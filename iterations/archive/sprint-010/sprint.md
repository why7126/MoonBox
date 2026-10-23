---
note: workflow-sync — workflow-sync 自动同步 — 10/10 Change archived；0 applied；Sprint `completed`
title: 自动验收与归档优化迭代
created_at: 2026-10-19 09:00:30
updated_at: 2026-10-20 08:22:43
sprint_id: sprint-010
status: completed
---

# 自动验收与归档优化迭代

经验复盘：[Sprint-010 复盘](../../../docs/knowledge-base/retrospectives/sprint-010-retrospective.md)；[治理恢复与归档验收实践](../../../docs/knowledge-base/best-practices/governance-recovery-archive-evidence.md)。4 项 open 建议，未自动创建 Issue/Change。

## 1. Sprint 目标

承接自动验收与归档治理优化，并纳入需求中心九阶段卡片扩宽与 Sprint 标签换行修复。追加 Capture 卡片负责人可读名称修复，保持身份键、权限与筛选语义。追加 BUG-0044 完成型阶段门禁、对象执行互斥、原会话续用与异常恢复修复。追加 BUG-0047 评审恢复记录初始化契约修复与恢复核验。容量以工作量与容量派生表为准。

### Sprint 目标编号列表

- REQ-0047-governance-command-durable-recovery
- BUG-0043-requirement-center-card-width-sprint-tag-wrap
- BUG-0028-requirement-center-card-owner-raw-user-id
- BUG-0044-requirement-stage-premature-transition-session-split
- BUG-0047-review-recovery-operation-record-missing
- BUG-0048-chat-legacy-panel-cleanup-removes-conversation
- BUG-0049-archive-wrapper-workflow-sync-unrecognized
- BUG-0050-archive-wrapper-proof-acceptance-fixture
- BUG-0051-archive-wrapper-proof-serial-fixture
- optimize-acceptance-archive-orchestration

### REQ-0047-governance-command-durable-recovery 要点

REQ `REQ-0047-governance-command-durable-recovery`：治理命令持久化阶段与幂等恢复闭环。当前状态 done，估算 8 人天；archived `add-governance-command-durable-recovery`（2026-10-19 18:28:26）。

### BUG-0043-requirement-center-card-width-sprint-tag-wrap 要点

BUG `BUG-0043-requirement-center-card-width-sprint-tag-wrap`：需求中心九阶段卡片宽度不足导致迭代标签换行。当前状态 done，估算 1 人天；archived `fix-requirement-center-card-width-sprint-tag-wrap`（2026-10-19 09:31:29）。

### BUG-0028-requirement-center-card-owner-raw-user-id 要点

BUG `BUG-0028-requirement-center-card-owner-raw-user-id`：需求中心 Capture 卡片直接显示内部用户标识。当前状态 done，估算 3 人天；archived `fix-requirement-center-owner-display`（2026-10-19 10:28:00）。

### BUG-0044-requirement-stage-premature-transition-session-split 要点

BUG `BUG-0044-requirement-stage-premature-transition-session-split`：需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂。当前状态 done，估算 8 人天；archived `fix-requirement-stage-completion-session-continuity`（2026-10-19 13:55:20）。

### BUG-0047-review-recovery-operation-record-missing 要点

BUG `BUG-0047-review-recovery-operation-record-missing`：评审恢复记录缺失导致成果未应用与卡片未流转。当前状态 done，估算 3 人天；archived `fix-review-recovery-operation-record-missing`（2026-10-19 15:36:46）。

### BUG-0048-chat-legacy-panel-cleanup-removes-conversation 要点

BUG `BUG-0048-chat-legacy-panel-cleanup-removes-conversation`：旧治理面板清理误删聊天会话区域。当前状态 done，估算 1 人天；archived `fix-chat-legacy-panel-cleanup-boundary`（2026-10-19 19:32:34）。

### BUG-0049-archive-wrapper-workflow-sync-unrecognized 要点

BUG `BUG-0049-archive-wrapper-workflow-sync-unrecognized`：归档包装脚本同步成功未识别导致看板停留验收中。当前状态 done，估算 3 人天；archived `fix-archive-wrapper-workflow-sync-proof`（2026-10-20 08:13:21）。

### BUG-0050-archive-wrapper-proof-acceptance-fixture 要点

BUG `BUG-0050-archive-wrapper-proof-acceptance-fixture`：归档包装脚本完成证明首次归档验收样本。当前状态 done，估算 0.5 人天；archived `fix-archive-wrapper-proof-acceptance-fixture`（2026-10-19 23:30:32）。

### BUG-0051-archive-wrapper-proof-serial-fixture 要点

BUG `BUG-0051-archive-wrapper-proof-serial-fixture`：归档包装证明无干扰串行验收样本。当前状态 done，估算 0.5 人天；archived `fix-archive-wrapper-proof-serial-fixture`（2026-10-19 23:53:43）。

### optimize-acceptance-archive-orchestration 要点

Change `optimize-acceptance-archive-orchestration`：optimize acceptance archive orchestration。当前状态 archived，估算 8 人天；archived `optimize-acceptance-archive-orchestration`（2026-10-19 23:59:59）。

## 横切预防清单

BUG-0049：继承 sprint-009 归档样本经验，区分首次归档样本与原执行恢复；AC-001 至 AC-007 覆盖可信同步证明、迁移失败、身份与摘要、幂等重启及真实看板一致性。管理后台表单、弹窗和上传规范不适用。product_data_collection_observability: applicable；affected_layers: 命令观测、私有操作凭证、对象门禁、Web投影；validation: 合成失败矩阵与真实归档/恢复分层验收。N/A：本次规划无API、DB或部署变更。

REQ-0047：引用评审恢复记录事故与原型驱动门禁；16项功能AC、3项KB和4项原型AC，先Skeleton再1440/390视觉；原轮次、唯一应用、预算与过期保护分层验收。

BUG-0047：复用 BUG-0044 完成门禁、对象互斥及成果保留契约；按 AC-001 至 AC-009 区分隔离故障注入与真实评审证据，核对实际部署模块版本。通用持久化恢复增量归属 REQ-0047，展示优化归属 REQ-0046，不纳入本次修复范围。

BUG-0044：按 AC-001 至 AC-012 建立逐入口证据矩阵；预检隔离对象、测试身份及浏览器，分别记录合成并发/故障注入和 1440px 真实观察。开始开发/返修及时投影，只读入口不锁定；项目对象互斥与个人会话权限分离。管理后台 CRUD 列表专项规范不适用于本次需求中心卡片流程。

保持真实证据、归档授权和副作用串行边界。BUG-0043 采用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 的视觉证据原则：九阶段×1440/768 双视口、computed style、长 ID 边界与真实/合成样本分开记录。

BUG-0028 按 AC-001 至 AC-008 覆盖名称回退、同名用户、REQ/BUG、刷新及权限；沿用视觉证据原则，记录 1440px 与原反馈视口、selector、computed style，合成断言与真实页面观察分开。

## 知识库承接

承接 sprint-009 复盘：局部阻塞不得放大，合成回归与真实观察分开；实施前确认浏览器、测试身份及环境。S9-A001 至 S9-A005 仍为 open 建议，本次不扩入正式范围。

## 依赖与发布

REQ-0047 → 复用已归档BUG-0044/0047 → req-opsx → 阶段与兼容/恢复调度 → 最小UI动作族 → 分层验收。REQ-0046协同反馈契约，不将其未评审范围纳入本Sprint。

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、usage_events、task_traces、task_trace_spans、Web、恢复调度。validation: REQ-0047 的 AC-001 至 AC-016、AC-KB及AC-PROTOTYPE覆盖部署兼容、阶段中断、幂等、预算、权限、过期保护和真实评审/视觉，均待实施；引用 docs/standards/product-data-collection-observability.md。N/A：本轮仅规划，无运行配置、schema、部署、对象存储或客户端生成变更。

BUG-0047：已评审 → sprint-010 → bug-opsx → 实施 → AC-001 至 AC-009 验收；复用已归档 BUG-0044，无需等待 REQ-0047 或 REQ-0046。

容量提示：36/30 人天（120%），超出 6 人天，fix 缓冲 0；后续低优先级新增项延后，返修优先，不擅自扩容。

product_data_collection_observability: applicable；affected_layers: Agent Workflow、API、request_logs、task_traces、task_trace_spans、Web 结果投影。validation: BUG-0047 根因证据已确认，AC-001 至 AC-009 修复验收待实施，覆盖初始化、缺失/损坏记录、重启、幂等、并发权限、真实评审和部署版本一致性；合成回归与真实观察分开。N/A：本次只更新规划文档，无 API、DB schema、部署、对象存储或客户端生成变更，具体实现影响由后续 Change 明确。

编排 → 复用 → 收尾；本轮不发布或归档。

product_data_collection_observability: applicable；affected_layers: Agent Workflow、Web 行为、对象会话 API、请求日志、Task Trace、Chat 轮次与阶段投影。validation: BUG-0044 按 AC-001 至 AC-012 验证完成门禁、会话续用、并发、权限、失败/未知恢复、外部同步和脱敏链路；合成回归与真实浏览器证据分别记录，当前均待实施。N/A：本轮只更新规划文档，无 API、DB schema、部署、对象存储或客户端生成变更；修复实现影响由后续 Change 设计明确。

BUG-0028 依赖：已通过评审 → 本 Sprint 纳入 → bug-opsx 定稿名称与身份契约 → 实施 → AC-001 至 AC-008 验收。没有新增跨 Issue 前置依赖。

BUG-0028 的 product_data_collection_observability: not_applicable；affected_layers: []；reason: 本次仅更新迭代规划，不调整 API、DB、日志、事件或请求封装。validation: 根因证据门禁通过，修复验收尚未开始；后续 Change 若调整身份解析 API 或持久化契约，重新声明层级及验证范围。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0047-governance-command-durable-recovery | 治理命令持久化阶段与幂等恢复闭环 | done | 8 人天 | archived `add-governance-command-durable-recovery`（2026-10-19 18:28:26） |
| BUG | BUG-0043-requirement-center-card-width-sprint-tag-wrap | 需求中心九阶段卡片宽度不足导致迭代标签换行 | done | 1 人天 | archived `fix-requirement-center-card-width-sprint-tag-wrap`（2026-10-19 09:31:29） |
| BUG | BUG-0028-requirement-center-card-owner-raw-user-id | 需求中心 Capture 卡片直接显示内部用户标识 | done | 3 人天 | archived `fix-requirement-center-owner-display`（2026-10-19 10:28:00） |
| BUG | BUG-0044-requirement-stage-premature-transition-session-split | 需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂 | done | 8 人天 | archived `fix-requirement-stage-completion-session-continuity`（2026-10-19 13:55:20） |
| BUG | BUG-0047-review-recovery-operation-record-missing | 评审恢复记录缺失导致成果未应用与卡片未流转 | done | 3 人天 | archived `fix-review-recovery-operation-record-missing`（2026-10-19 15:36:46） |
| BUG | BUG-0048-chat-legacy-panel-cleanup-removes-conversation | 旧治理面板清理误删聊天会话区域 | done | 1 人天 | archived `fix-chat-legacy-panel-cleanup-boundary`（2026-10-19 19:32:34） |
| BUG | BUG-0049-archive-wrapper-workflow-sync-unrecognized | 归档包装脚本同步成功未识别导致看板停留验收中 | done | 3 人天 | archived `fix-archive-wrapper-workflow-sync-proof`（2026-10-20 08:13:21） |
| BUG | BUG-0050-archive-wrapper-proof-acceptance-fixture | 归档包装脚本完成证明首次归档验收样本 | done | 0.5 人天 | archived `fix-archive-wrapper-proof-acceptance-fixture`（2026-10-19 23:30:32） |
| BUG | BUG-0051-archive-wrapper-proof-serial-fixture | 归档包装证明无干扰串行验收样本 | done | 0.5 人天 | archived `fix-archive-wrapper-proof-serial-fixture`（2026-10-19 23:53:43） |
| Change | optimize-acceptance-archive-orchestration | optimize acceptance archive orchestration | archived | 8 人天 | archived `optimize-acceptance-archive-orchestration`（2026-10-19 23:59:59） |

REQ：`REQ-0047` 已纳入正式范围；BUG：`BUG-0043`、`BUG-0028`、`BUG-0044`、`BUG-0047`、`BUG-0048`、`BUG-0049`、`BUG-0050`、`BUG-0051` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 9 个范围项关联 Change，另有 1 个纯 Change；10 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `optimize-acceptance-archive-orchestration` | — | archived | archived `optimize-acceptance-archive-orchestration`（2026-10-19 23:59:59） |
| `fix-requirement-center-card-width-sprint-tag-wrap` | BUG-0043-requirement-center-card-width-sprint-tag-wrap | archived | archived `fix-requirement-center-card-width-sprint-tag-wrap`（2026-10-19 09:31:29） |
| `fix-requirement-center-owner-display` | BUG-0028-requirement-center-card-owner-raw-user-id | archived | archived `fix-requirement-center-owner-display`（2026-10-19 10:28:00） |
| `fix-requirement-stage-completion-session-continuity` | BUG-0044-requirement-stage-premature-transition-session-split | archived | archived `fix-requirement-stage-completion-session-continuity`（2026-10-19 13:55:20） |
| `fix-review-recovery-operation-record-missing` | BUG-0047-review-recovery-operation-record-missing | archived | archived `fix-review-recovery-operation-record-missing`（2026-10-19 15:36:46） |
| `add-governance-command-durable-recovery` | REQ-0047-governance-command-durable-recovery | archived | archived `add-governance-command-durable-recovery`（2026-10-19 18:28:26） |
| `fix-chat-legacy-panel-cleanup-boundary` | BUG-0048-chat-legacy-panel-cleanup-removes-conversation | archived | archived `fix-chat-legacy-panel-cleanup-boundary`（2026-10-19 19:32:34） |
| `fix-archive-wrapper-workflow-sync-proof` | BUG-0049-archive-wrapper-workflow-sync-unrecognized | archived | archived `fix-archive-wrapper-workflow-sync-proof`（2026-10-20 08:13:21） |
| `fix-archive-wrapper-proof-acceptance-fixture` | BUG-0050-archive-wrapper-proof-acceptance-fixture | archived | archived `fix-archive-wrapper-proof-acceptance-fixture`（2026-10-19 23:30:32） |
| `fix-archive-wrapper-proof-serial-fixture` | BUG-0051-archive-wrapper-proof-serial-fixture | archived | archived `fix-archive-wrapper-proof-serial-fixture`（2026-10-19 23:53:43） |
<!-- workflow-sync:scope-changes:end -->

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0047 | 治理命令持久化阶段与幂等恢复闭环 | P1 | done | archived `add-governance-command-durable-recovery`（2026-10-19 18:28:26） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0043 | 需求中心九阶段卡片宽度不足导致迭代标签换行 | low | done | archived `fix-requirement-center-card-width-sprint-tag-wrap`（2026-10-19 09:31:29） |
| BUG-0028 | 需求中心 Capture 卡片直接显示内部用户标识 | medium | done | archived `fix-requirement-center-owner-display`（2026-10-19 10:28:00） |
| BUG-0044 | 需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂 | high | done | archived `fix-requirement-stage-completion-session-continuity`（2026-10-19 13:55:20） |
| BUG-0047 | 评审恢复记录缺失导致成果未应用与卡片未流转 | high | done | archived `fix-review-recovery-operation-record-missing`（2026-10-19 15:36:46） |
| BUG-0048 | 旧治理面板清理误删聊天会话区域 | high | done | archived `fix-chat-legacy-panel-cleanup-boundary`（2026-10-19 19:32:34） |
| BUG-0049 | 归档包装脚本同步成功未识别导致看板停留验收中 | high | done | archived `fix-archive-wrapper-workflow-sync-proof`（2026-10-20 08:13:21） |
| BUG-0050 | 归档包装脚本完成证明首次归档验收样本 | low | done | archived `fix-archive-wrapper-proof-acceptance-fixture`（2026-10-19 23:30:32） |
| BUG-0051 | 归档包装证明无干扰串行验收样本 | low | done | archived `fix-archive-wrapper-proof-serial-fixture`（2026-10-19 23:53:43） |
<!-- workflow-sync:scope-bugs:end -->

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 36 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 36.5 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 120.00% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 2026-10-19 09:00:30 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 2026-10-30 18:00:00 | `changes[]` 全部 apply 完成 | 10/10 已 apply 或 archive |
| 归档收口 | 2026-10-30 18:00:00 | `changes[]` 全部 archive，验收报告完成 sign-off | 10/10 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 120.00% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-010-retrospective.md` | 10/10 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

