---
note: workflow-sync — workflow-sync 自动同步 — 5/5 Change archived；0 applied；Sprint `completed`
title: 直接命令完成证明与安全恢复迭代规划
sprint_id: sprint-012
status: completed
created_at: '2026-10-21 11:39:09'
updated_at: 2026-10-27 16:18:36
---

# 直接命令完成证明与安全恢复迭代规划

## 迭代关闭记录（2026-10-23 22:42:09）

按用户 `/sprint-archive sprint-012` 授权完成关闭：5项Change均已归档（本次跳过5项），83/83任务完成，关联1项REQ、4项BUG已关闭。严格归档、目录、环境忽略策略和陈旧扫描通过；迭代由change迁入archive，状态completed。累计估算34人天、容量30人天及原计划窗口保持不变，估算不表示实际投入。历史规划和阶段性验收记录保留，最终结论见acceptance-report.md。产品版本未随本次关闭发布。

## 1. Sprint 目标

建立直接命令通用完成证明、最终核验与安全恢复，保留正确性门禁。

### Sprint 目标编号列表

- REQ-0049-sprint-archive-chat-entry
- BUG-0060-direct-command-completion-proof-drift
- BUG-0061-cross-entry-continuation-guard-convergence
- BUG-0062-archive-requirement-scope-conflict
- BUG-0063-compatible-requirement-successor-blocked

### REQ-0049-sprint-archive-chat-entry 要点

REQ `REQ-0049-sprint-archive-chat-entry`：迭代归档接入 Sprint 对象会话与命令预填。当前状态 done，估算 5 人天；archived `add-sprint-archive-chat-entry`（2026-10-21 18:34:08）。

### BUG-0060-direct-command-completion-proof-drift 要点

BUG `BUG-0060-direct-command-completion-proof-drift`：Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段。当前状态 done，估算 8 人天；archived `fix-direct-command-completion-proof`（2026-10-21 14:09:29）。

### BUG-0061-cross-entry-continuation-guard-convergence 要点

BUG `BUG-0061-cross-entry-continuation-guard-convergence`：产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断。当前状态 done，估算 8 人天；archived `fix-cross-entry-continuation-guard`（2026-10-27 16:18:35）。

### BUG-0062-archive-requirement-scope-conflict 要点

BUG `BUG-0062-archive-requirement-scope-conflict`：归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻。当前状态 done，估算 5 人天；archived `fix-archive-requirement-scope-conflict`（2026-10-21 19:11:19）。

### BUG-0063-compatible-requirement-successor-blocked 要点

BUG `BUG-0063-compatible-requirement-successor-blocked`：同条文兼容追加被归档后继冲突门禁拒绝。当前状态 done，估算 8 人天；archived `fix-compatible-requirement-successor`（2026-10-23 21:46:21）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0049-sprint-archive-chat-entry | 迭代归档接入 Sprint 对象会话与命令预填 | done | 5 人天 | archived `add-sprint-archive-chat-entry`（2026-10-21 18:34:08） |
| BUG | BUG-0060-direct-command-completion-proof-drift | Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段 | done | 8 人天 | archived `fix-direct-command-completion-proof`（2026-10-21 14:09:29） |
| BUG | BUG-0061-cross-entry-continuation-guard-convergence | 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断 | done | 8 人天 | archived `fix-cross-entry-continuation-guard`（2026-10-27 16:18:35） |
| BUG | BUG-0062-archive-requirement-scope-conflict | 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻 | done | 5 人天 | archived `fix-archive-requirement-scope-conflict`（2026-10-21 19:11:19） |
| BUG | BUG-0063-compatible-requirement-successor-blocked | 同条文兼容追加被归档后继冲突门禁拒绝 | done | 8 人天 | archived `fix-compatible-requirement-successor`（2026-10-23 21:46:21） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0049 | 迭代归档接入 Sprint 对象会话与命令预填 | P1 | done | archived `add-sprint-archive-chat-entry`（2026-10-21 18:34:08） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0060 | Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段 | high | done | archived `fix-direct-command-completion-proof`（2026-10-21 14:09:29） |
| BUG-0061 | 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断 | high | done | archived `fix-cross-entry-continuation-guard`（2026-10-27 16:18:35） |
| BUG-0062 | 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻 | high | done | archived `fix-archive-requirement-scope-conflict`（2026-10-21 19:11:19） |
| BUG-0063 | 同条文兼容追加被归档后继冲突门禁拒绝 | high | done | archived `fix-compatible-requirement-successor`（2026-10-23 21:46:21） |
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `fix-direct-command-completion-proof` | BUG-0060-direct-command-completion-proof-drift | archived | archived `fix-direct-command-completion-proof`（2026-10-21 14:09:29） |
| `fix-cross-entry-continuation-guard` | BUG-0061-cross-entry-continuation-guard-convergence | archived | archived `fix-cross-entry-continuation-guard`（2026-10-27 16:18:35） |
| `fix-archive-requirement-scope-conflict` | BUG-0062-archive-requirement-scope-conflict | archived | archived `fix-archive-requirement-scope-conflict`（2026-10-21 19:11:19） |
| `add-sprint-archive-chat-entry` | REQ-0049-sprint-archive-chat-entry | archived | archived `add-sprint-archive-chat-entry`（2026-10-21 18:34:08） |
| `fix-compatible-requirement-successor` | BUG-0063-compatible-requirement-successor-blocked | archived | archived `fix-compatible-requirement-successor`（2026-10-23 21:46:21） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0049` 已纳入正式范围；BUG：`BUG-0060`、`BUG-0061`、`BUG-0062`、`BUG-0063` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 5 个范围项关联 Change，另有 0 个纯 Change；5 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 34 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 34 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 113.33% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 未知 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 5/5 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 5/5 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 113.33% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-012-retrospective.md` | 5/5 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 验收重点

## BUG-0061 纳入时规划记录（历史）

BUG-0060已归档，保留原8人天历史范围；用户明确选择sprint-012追加已批准BUG-0061，估算XL/8人天/8故事点。该次纳入时合计16/30人天（53.33%）。本次用户选择追加已评审 REQ-0049，L/5人天/5故事点，同期BUG-0062追加5人天后，当前合计26/30人天（86.67%），剩余4人天（13.33%）；未超容量，但缓冲低于建议30%。未变更sprint-011或扩容。BUG-0061已创建fix-cross-entry-continuation-guard，已实施部署，真实联合链路通过。

## 横切预防清单

- 复用 docs/knowledge-base/best-practices/governance-recovery-archive-evidence.md：首次成功、失败拒绝、历史恢复和重启回读分别留证，保留旧证明与未知历史事实。
- 动作级输入依赖、预期输出、验证器和版本化逐文件清单；区分说明收尾、无关并发与真实相关冲突，不整体忽略 Markdown、注册表或共享约束。
- 最终稳定版本签认，复读相关指纹及 operation/version 围栏；检查、退出0和模型成功文本不替代证明。
- 权限、绑定、隔离、全局唯一性/引用/容量门禁及既有评审/归档证明继续生效；损坏、缺失、未知版本和真实冲突保持阻断。
- BUG-0055 历史逐文件归因缺口保留；恢复重建当前核验依据，不伪造原同步证明，不重放 bug-opsx、不重复创建 Change、不手改保护或阶段。

## 跨迭代依赖与执行顺序

```text
BUG-0052 / BUG-0060 已归档能力 -> 兼容基线
BUG-0061 已批准并纳入 -> bug-opsx设计后继证明与事件语义
  -> 证明采集 / 差异分类 / 安全恢复实现
  -> dry-run、内部失败外层0、并发版本、缺证与真实冲突回归
  -> 稳定版本部署核对
  -> 隔离REQ/BUG：产品受阻 -> CLI续接 -> 产品核验 -> 实际发送归档 -> 业务终态
  -> 等价隔离对象CLI归档对照
  -> BUG-0055最新现场核对 -> 安全恢复 -> 产品实际动作及归档终态核验
  -> 14项AC证据签认 -> 归档就绪 -> 独立发布流程
```

BUG-0055保留在sprint-011，其排序实现不迁入本迭代；跨迭代仅承接旧apply保护与后继交付恢复。先核实其当前状态、新执行占用、权限、绑定及证据；若已完成或归档则验证幂等终态，不按旧截图重放。恢复不追认旧轮成功，不重放原命令或重复合并规格。缺证/冲突只阻断相关样本，其他可执行项继续。

## 联合验收与证据计划

BUG-0060历史验收见其归档证据，不重置为待执行；BUG-0061以其acceptance.md的AC-001—014为准，真实联合证据已采集。

| 验证组 | BUG-0061 AC | 证据与通过条件 |
|---|---|---|
| 后继与完成语义 | 001—003 | 原步骤不变，独立后继记录；start/progress不等于完成；dry-run/check、分号换行/引号与内部非零外层0正确拒绝 |
| 差异与安全恢复 | 004—007 | 派生输出、合法续接、无关并发和真实冲突分别判定；版本、权限、快照竞争及重复/中断恢复 |
| 展示与实际归档 | 008—010 | 1440与390视口，刷新/重进；产品实际发送至归档业务终态；等价CLI正反例一致，不以ready/按钮可点代替 |
| 专用协议与现场 | 011—012 | 评审/归档门禁保留；跨日迁移/中断不重复合并；BUG-0055最新现场安全恢复，保留旧记录 |
| 通用及证据边界 | 013—014 | REQ/BUG支持动作矩阵、观测脱敏；19项累计差异与历史归因partial分开记录 |

完整入口前检、修改稳定后集中验证，受影响范围增量复验及有效证据复用。正常样本串行，并发测试受控注入竞争。产品轮次、CLI、合成、视觉和部署证据分别报告；证据归属后续Change的evidence/acceptance。模型调用遵循届时有效授权；本规划不执行模型样本或正式归档。

## 知识库承接说明

采用最近 sprint-010 复盘 S10-A002 的证据分层实践，不代表该通用行动整体完成。S10-A001/A003/A004 保留原状态和范围，不自动新增 Issue。admin-list/admin-form/admin-modal/media-upload 不适用于本次 Chat 治理完成契约。

## 发布计划

先完成 Change 设计、实现、必要API/DB/UI/客户端文档同步及本地回归，再部署核对版本并执行上述联合验收。全部适用 AC 有效通过后才能报告归档就绪，发布按独立流程确认；本次不部署、不恢复现场、不归档、不发布。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Chat、治理API、完成证明、执行保护、文件清单、卡片投影、CLI及恢复。validation: 本次仅规划和状态校验，产品验收待执行。实施按 docs/standards/product-data-collection-observability.md 同步必要错误码与脱敏关联键、操作版本、摘要和诊断，不收集无关正文或凭证。N/A：本轮没有API、数据库、UI、部署、安全策略或生成客户端变更；未来schema影响由Change设计确认。

## 关联文档

- [缺陷与追溯](../../../issues/bugs/archive/BUG-0060-direct-command-completion-proof-drift/trace.md)
- [验收标准](../../../issues/bugs/archive/BUG-0060-direct-command-completion-proof-drift/acceptance.md)
- [跨迭代现场](../sprint-011/sprint.md)

## 新增关联范围

- [BUG-0061追溯](../../../issues/bugs/review/BUG-0061-cross-entry-continuation-guard-convergence/trace.md)
- [BUG-0061验收](../../../issues/bugs/review/BUG-0061-cross-entry-continuation-guard-convergence/acceptance.md)

## REQ-0049 规划补充

用户明确指定 sprint-012。REQ-0049 已评审，作为 REQ-0037 子需求关联 REQ-0039；本次新增1条需求，不新增 BUG 或 Change。5人天分解：会话与准入1.5、导航与草稿保护1、权限/幂等回归1、原型确认与真实链路验收1.5。沿用30人天显式容量，保留原BUG及归档成果，不重置其验收结果。同期BUG-0062纳入后，缓冲为4人天（13.33%），低于建议30%。优先交付已确定范围；若新增迁移或执行器适配成本，应重估并延后低优先级增强，不静默扩容。

```text
REQ-0037 / REQ-0039 已交付能力 + BUG-0060 / BUG-0061 执行保护基线
  → REQ-0049 需求评审通过 → 本次纳入 sprint-012
  → req-opsx：确认 SPRINT 身份、准入、API/DB 兼容与输入消费契约
  → UI Skeleton 首轮确认 → 实现及回归 → 隔离项目真实验收
  → 全部 AC 与视觉门禁有效通过 → 按授权归档
```

原型预览受 URL 策略限制、真实视觉证据尚缺属明确实施门禁，不是产品验收通过。真实归档样本使用隔离项目，不能以本 Sprint 自身作为唯一验收对象导致完成判定循环；不为取证提前归档 sprint-012。

横切预防承接原型驱动门禁：1440×900、768×900、390×844，原型/动作矩阵/selector/computed style 与最终文档一致。承接 S10-A002 的首次成功/失败拒绝/原执行恢复及串行样本实践；S10-A001/A003/A004 维持原状态，不扩大通用治理范围。

product_data_collection_observability: applicable；affected_layers: web、api、usage_events、request_logs、task_traces、task_trace_spans。validation: REQ-0049 的21项功能、3项知识库、6项原型 AC，重点验证准备不发送、跨项目隔离、重复请求、草稿保护、签署执行门禁和最终事实回读。N/A：不新增对象存储、部署拓扑、管理端或移动端能力；API/DB/客户端生成是否变更在 Change 设计确认并同步。

- [REQ-0049需求](../../../issues/requirements/review/REQ-0049-sprint-archive-chat-entry/requirement.md)
- [REQ-0049验收](../../../issues/requirements/review/REQ-0049-sprint-archive-chat-entry/acceptance.md)

## BUG-0062 条文冲突修复规划

用户明确选择sprint-012纳入BUG-0062-archive-requirement-scope-conflict，L／5故事点／5人天。同期REQ-0049新增5人天，当前迭代合计26/30人天（86.67%），剩余4人天（13.33%）；容量及120%硬门禁通过，但低于建议30%缓冲。保留原容量与计划窗口，不追加未经估算的范围，增长时重算门禁。

范围：模块与Requirement条文组合判冲突、保留真实AC进度和具体恢复原因、统一Sprint预检与产品/CLI/Workflow Sync深层判定。BUG-0060、BUG-0061已归档，作为兼容基线；BUG-0062尚无Change，11项AC未开始，不能复用旧通过结论宣称完成。

依赖顺序：已归档证明与当前REQ-0046证据 → BUG-0062独立Change → 解析及安全负例 → 进度/诊断与共享预检 → 稳定版本及跨入口验收 → 归档就绪。sprint-011只为受影响现场，先保持未关闭；修复通过后按授权重新执行关闭，不迁入本迭代、不重复归档原Change。

复用S10-A002与治理恢复证据分层实践；保留旧manifest、journal、首次execution及原条文。合成、产品观察、CLI和部署证据分开，视觉按实际影响建立1440px及关键交互证据；admin-list/admin-form/admin-modal/media-upload不适用。未整体承接其他open行动。

product_data_collection_observability: applicable；reason: 条文冲突判断及诊断传播影响治理链路和迭代关闭；affected_layers: agent_workflow_governance、归档准入、验收/诊断投影、Sprint预检与Workflow Sync。validation：本轮规划、根因与Scope门禁；实施后按AC-001—011核验条文冲突、证据完整性、并发、真实进度及四入口一致性。N/A：本轮不改API、DB、UI、部署、安全或客户端；未来响应契约变化时同步相应文档、OpenAPI、客户端和测试，不新增原文或凭证采集。

发布与验收：BUG-0062全部适用AC通过后才能声明修复完成；依次完成Change归档、Sprint关闭，再进入独立发布流程。本次不部署、不执行真实归档或模型样本。

## BUG-0063 兼容追加与产品防复发规划

正式纳入 BUG-0063-compatible-requirement-successor-blocked（high、已评审），XL／8故事点／8人天。保持30人天容量与原计划窗口；当前合计34/30人天（113.3%），超额4人天、无剩余返修缓冲，未超过36人天硬上限。已归档26人天不从累计估算扣除，无可替换的未交付低优先项；后续非必要范围延后，新增或返修导致超过36人天时先拆分/调整范围，不降低验收门禁。预计存在延期风险，估算或窗口变动另行记录。

范围：统一版本化兼容追加证明、后继影响写入前预检、产品逐项可操作诊断、四入口一致判定及持续防回归。保留破坏性修改、断链、篡改、不确定语义和并发变化的拒绝，禁止对象ID或标题特判，不修改历史证明。人工sign-off和旧路径收尾仍是独立关闭条件。

执行依赖：
```text
BUG-0060/0061/0062已归档基线与BUG-0063评审
  -> 新Change设计受支持追加契约及UI/API诊断
  -> 通用证明与后继预检 -> 产品反馈与共享准入
  -> 正负例/多跳/跨Sprint/并发/幂等稳定回归
  -> 稳定部署及真实产品与CLI分层验收
  -> 18项AC逐项证据 -> Change归档
  -> sprint-012最新门禁复核 -> 按授权关闭
```

知识承接：复用最近sprint-011复盘中的S10-A002（正常/失败/恢复分层及串行样本）与S11-A001（追加范围、缓冲和外部关闭依赖显式说明）。本次不移出历史已交付项，明确无剩余缓冲与签署/链接依赖；承接仅限本BUG，不宣称通用行动已关闭。S10-A001当前引用实践用于收尾校验，其他open行动不自动纳入。

横切预防：复用 governance-recovery-archive-evidence.md；合成、真实模型轮次、部署指纹及视觉证据分别签认，历史manifest/journal不变；UI实际受影响时补原型契约、1440px与关键窄屏、selector/computed style。admin-list/admin-form/admin-modal/media-upload不适用：本项为现有Chat诊断和证明机制。

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档后继证明、API准入诊断、Web反馈、Sprint预检、Workflow Sync；validation: BUG-0063 AC-001—018，尤其证据保真、共享错误、并发及脱敏。N/A：本轮仅规划，无DB、对象存储、部署或客户端生成变更；未来若变更响应契约，实施时同步OpenAPI/客户端与测试，不新增原始Prompt或凭证采集。

发布与验收：18项AC尚未开始，不借用历史通过结果。新Change按正常OpenSpec流程实施，真实样本使用隔离环境；本规划不执行实际归档、不发布镜像或关闭Sprint。

## 经验复盘

已完成[跨入口续接与迭代归档经验复盘](../../../docs/knowledge-base/retrospectives/sprint-012-retrospective.md)，包含流程、设计、质量、复用与模型Token分析；6项open行动中5项沿用前序ID，未自动创建Issue或变更后续Sprint范围。
