---
note: workflow-sync — workflow-sync 自动同步 — 4/4 Change archived；0 applied；Sprint `completed`
title: 统一工作区、恢复保护与受控合入迭代规划
sprint_id: sprint-015
created_at: '2026-10-29 06:45:27'
updated_at: 2026-10-29 16:44:48
---

# 统一工作区、恢复保护与受控合入迭代规划

## 1. Sprint 目标

建立默认主源码目录、按交付链路隔离开发、恢复保护和迭代操作权限确认合入的完整闭环。模块统一 moonbox-，首期保持 Web。

### Sprint 目标编号列表

- REQ-0042-agent-runtime-version-space-isolation
- REQ-0054-workspace-recovery-points
- REQ-0055-sprint-authorized-worktree-merge
- add-isolated-candidate-validation

### REQ-0042-agent-runtime-version-space-isolation 要点

REQ `REQ-0042-agent-runtime-version-space-isolation`：统一主源码目录与交付链路工作区及模块化执行架构。当前状态 done，估算 13 人天；archived `update-unified-workspace-runtime`（2026-10-29 06:51:35）。

### REQ-0054-workspace-recovery-points 要点

REQ `REQ-0054-workspace-recovery-points`：工作区恢复点复用保留与冲突恢复。当前状态 done，估算 8 人天；archived `add-workspace-recovery-points`（2026-10-29 06:51:35）。

### REQ-0055-sprint-authorized-worktree-merge 要点

REQ `REQ-0055-sprint-authorized-worktree-merge`：继承迭代操作权限的工作区成果确认合入。当前状态 done，估算 8 人天；archived `add-sprint-authorized-worktree-merge`（2026-10-29 06:51:35）。

### add-isolated-candidate-validation 要点

Change `add-isolated-candidate-validation`：add isolated candidate validation。当前状态 archived，估算 5 人天；archived `add-isolated-candidate-validation`（2026-10-29 13:05:07）。

## 2. Scope

正式范围由 sprint.yaml 与 Workflow Sync 派生。

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0042-agent-runtime-version-space-isolation | 统一主源码目录与交付链路工作区及模块化执行架构 | done | 13 人天 | archived `update-unified-workspace-runtime`（2026-10-29 06:51:35） |
| REQ | REQ-0054-workspace-recovery-points | 工作区恢复点复用保留与冲突恢复 | done | 8 人天 | archived `add-workspace-recovery-points`（2026-10-29 06:51:35） |
| REQ | REQ-0055-sprint-authorized-worktree-merge | 继承迭代操作权限的工作区成果确认合入 | done | 8 人天 | archived `add-sprint-authorized-worktree-merge`（2026-10-29 06:51:35） |
| Change | add-isolated-candidate-validation | add isolated candidate validation | archived | 5 人天 | archived `add-isolated-candidate-validation`（2026-10-29 13:05:07） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0042 | 统一主源码目录与交付链路工作区及模块化执行架构 | P1 | done | archived `update-unified-workspace-runtime`（2026-10-29 06:51:35） |
| REQ-0054 | 工作区恢复点复用保留与冲突恢复 | P1 | done | archived `add-workspace-recovery-points`（2026-10-29 06:51:35） |
| REQ-0055 | 继承迭代操作权限的工作区成果确认合入 | P1 | done | archived `add-sprint-authorized-worktree-merge`（2026-10-29 06:51:35） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `update-unified-workspace-runtime` | REQ-0042-agent-runtime-version-space-isolation | archived | archived `update-unified-workspace-runtime`（2026-10-29 06:51:35） |
| `add-workspace-recovery-points` | REQ-0054-workspace-recovery-points | archived | archived `add-workspace-recovery-points`（2026-10-29 06:51:35） |
| `add-sprint-authorized-worktree-merge` | REQ-0055-sprint-authorized-worktree-merge | archived | archived `add-sprint-authorized-worktree-merge`（2026-10-29 06:51:35） |
| `add-isolated-candidate-validation` | REQ-0048-chat-isolated-acceptance-orchestration | archived | archived `add-isolated-candidate-validation`（2026-10-29 13:05:07） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0042`、`REQ-0054`、`REQ-0055` 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 3 个范围项关联 Change，另有 1 个纯 Change；4 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

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
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 4/4 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 4/4 已 archive，0 待归档 |
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
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-015-retrospective.md` | 4/4 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

引用 docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md：三需求各3项横切AC，覆盖class级联、computed width、低视口滚动和操作可达。原型拆解已完成；Skeleton、1440px及关键视口深浅主题、真实API和最终文档一致性为实现门禁。无管理端CRUD列表、独立表单及上传，不额外套用无关专题。

## 8. 依赖与开放顺序

```text
REQ-0042 工作区身份、模块接口与主目录路径
  -> REQ-0054 主目录恢复保护 -> 独立开发工作树恢复接入
  -> REQ-0055 候选验证、迭代权限确认与持久合入
三项联合验收 -> 独立 worktree 正式开放 -> 受控归档与后续发布
```

REQ-0053内容分块、REQ-0047持久恢复作为已有能力复用。REQ-0048为关联验收编排依赖，未纳入本次范围，不视为已交付；创建Change时核对可复用能力，若供应接口未就绪则先完成独立部分，集成开放保持阻断，不静默扩大本Sprint范围。子Change串行复用同链路开发树，模块拆分不要求独立微服务。

## 9. 发布计划

本轮只规划，不创建开发Change、不部署。逐REQ验收后仍需联合验证、OpenSpec归档与正式发布流程；版本号未指定，不预分配版本标签。

## 10. 关联文档

三条REQ均位于 issues/requirements/review/；各自review.md为评审结论，acceptance.md为验收要求，prototype/web/context.md为原型策略。正式Change创建后由同步补充关联。

## 11. 规划依据与容量风险

sprint-014 原估算33/30人天，追加本组29人天将达62/30，超过36人天硬上限，故选下一个连续编号sprint-015；不扣除已完成项来掩盖原规划总量。新迭代29/30人天，占96.7%，仅余1人天（3.3%），低于建议30%缓冲；超过剩余量的返修需重新规划，后续追加优先延期或替换。估算不等于交付承诺，日期为两周规划窗口，人员值沿用当前迭代规划假设，不代表已确认人员投入。

估算：0042 XXL/13人天（身份与模块接口4、执行隔离及迁移4、双库并发与UI验证5）；0054 XL/8人天（采集复用与引用3、恢复及故障保护3、兼容容量与UI验证2）；0055 XL/8人天（权限与版本2、候选合入及对账3、并发撤权与UI验证3）。实现设计发现新依赖或工作量变化时重算，不减少既定验收来满足容量。

## 12. 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: web、api、db、agent_workflow、usage_events、request_logs、task_traces、task_trace_spans。三REQ已引用 docs/standards/product-data-collection-observability.md，AC-DATA覆盖脱敏、权限、失败恢复与真实样本；validation: 本轮为规划一致性检查，运行态验收未执行。移动端/桌面端未启用，首期不新增对象存储后端；若设计改变此边界需补齐验收与备份契约。

## 范围承接决定（2026-10-29）

用户确认REQ-0048未交付的完整Chat环境编排、原操作续接、停止撤权、角色矩阵与完整产品/视觉验收转入sprint-016。本迭代保留add-isolated-candidate-validation已交付子范围和原5人天估算；不重复开发或搬迁归档Change，不关闭REQ-0048。为遵守最多两个活动迭代，先关闭本迭代，再正式创建sprint-016承接。

## 关闭记录

2026-10-29 16:30:18：当前正式范围通过关闭门禁，change → archive（/sprint-archive）；REQ-0048剩余范围按用户授权由后续sprint-016承接。

## 经验复盘回链

[统一工作区交付与跨迭代承接经验复盘](../../../docs/knowledge-base/retrospectives/sprint-015-retrospective.md)：记录部分交付、归属同步、运行生命周期与用量覆盖边界；仅知识回链，不改变关闭状态。
