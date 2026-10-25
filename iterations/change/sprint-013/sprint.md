---
note: workflow-sync — workflow-sync 自动同步 — 4/4 Change archived；0 applied；Sprint `planning`
title: 受控规则替代证明迭代规划
sprint_id: sprint-013
status: planning
created_at: '2026-10-22 13:17:23'
updated_at: 2026-10-24 21:28:24
---

# 受控规则替代证明迭代规划

## REQ-0050 当前范围说明（2026-10-23）

BUG-0063 已归档，生效规则按正常验收处理同条文后继，不再要求独立兼容证明。REQ-0050 当前只交付差异说明与现行归档门禁复用，取消额外规则确认；旧依赖图和授权文字是规划历史，不表示仍需先归档 BUG-0063。

## 1. Sprint 目标

### Sprint 目标编号列表

- REQ-0050-controlled-rule-replacement-proof
- REQ-0051-card-persistent-info-tags
- product-manager-readable-agent-output
- fix-git-scan-regex-false-positive

### REQ-0050-controlled-rule-replacement-proof 要点

REQ `REQ-0050-controlled-rule-replacement-proof`：规则修改说明与安全归档。当前状态 done，估算 13 人天；archived `add-controlled-rule-replacement-proof`（2026-10-22 13:24:21）。

### REQ-0051-card-persistent-info-tags 要点

REQ `REQ-0051-card-persistent-info-tags`：需求中心卡片常驻根因状态与开发人天标签。当前状态 done，估算 3 人天；archived `add-card-persistent-info-tags`（2026-10-22 20:02:47）。

### product-manager-readable-agent-output 要点

Change `product-manager-readable-agent-output`：product manager readable agent output。当前状态 archived，估算 0.5 人天；archived `product-manager-readable-agent-output`（2026-10-23 23:59:59）。

### fix-git-scan-regex-false-positive 要点

Change `fix-git-scan-regex-false-positive`：fix git scan regex false positive。当前状态 archived，估算 0.5 人天；archived `fix-git-scan-regex-false-positive`（2026-10-24 23:59:59）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0050-controlled-rule-replacement-proof | 规则修改说明与安全归档 | done | 13 人天 | archived `add-controlled-rule-replacement-proof`（2026-10-22 13:24:21） |
| REQ | REQ-0051-card-persistent-info-tags | 需求中心卡片常驻根因状态与开发人天标签 | done | 3 人天 | archived `add-card-persistent-info-tags`（2026-10-22 20:02:47） |
| Change | product-manager-readable-agent-output | product manager readable agent output | archived | 0.5 人天 | archived `product-manager-readable-agent-output`（2026-10-23 23:59:59） |
| Change | fix-git-scan-regex-false-positive | fix git scan regex false positive | archived | 0.5 人天 | archived `fix-git-scan-regex-false-positive`（2026-10-24 23:59:59） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0050 | 规则修改说明与安全归档 | P1 | done | archived `add-controlled-rule-replacement-proof`（2026-10-22 13:24:21） |
| REQ-0051 | 需求中心卡片常驻根因状态与开发人天标签 | P2 | done | archived `add-card-persistent-info-tags`（2026-10-22 20:02:47） |
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
| `add-controlled-rule-replacement-proof` | REQ-0050-controlled-rule-replacement-proof | archived | archived `add-controlled-rule-replacement-proof`（2026-10-22 13:24:21） |
| `add-card-persistent-info-tags` | REQ-0051-card-persistent-info-tags | archived | archived `add-card-persistent-info-tags`（2026-10-22 20:02:47） |
| `product-manager-readable-agent-output` | — | archived | archived `product-manager-readable-agent-output`（2026-10-23 23:59:59） |
| `fix-git-scan-regex-false-positive` | — | archived | archived `fix-git-scan-regex-false-positive`（2026-10-24 23:59:59） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0050`、`REQ-0051` 已纳入正式范围；BUG：无 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 2 个范围项关联 Change，另有 2 个纯 Change；4 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 17 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 18 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 56.67% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 13 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 43.33% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | pass：未超过容量 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 2026-10-22 13:17:23 | 四件套创建并纳入正式范围 | planning |
| 范围实现完成 | 2026-11-05 18:00:00 | `changes[]` 全部 apply 完成 | 4/4 已 apply 或 archive |
| 归档收口 | 2026-11-05 18:00:00 | `changes[]` 全部 archive，验收报告完成 sign-off | 4/4 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 无明显派生风险 | low | 容量、缓冲和 Change 状态未触发风险阈值 | 按既有计划推进 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-013-retrospective.md` | 4/4 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 验收重点

REQ-0050包含20项功能、4项media-upload横切及4项原型门禁，当前未实施。覆盖精确义务映射、可信授权、首次启用、并发撤销、完整归档链、恢复幂等和独立签署；有效AC进度与最终准入分开。

## 规划依据与估算

用户明确选择新建sprint-013。sprint-012已有34/30人天，追加13人天将达47/30，超过36人天硬上限，因此拆出新需求而非扩大旧容量或倒扣历史交付。新迭代XXL/13故事点/13人天：证明与授权3，可信首次启用3，并发及恢复3，审批UI与真实端到端验收4。容量30，使用43.33%，剩余17人天（56.67%）；至少保留9人天用于返修，不将全部余量默认授权为新范围。

计划窗口为自规划日起两周，是目标而非交付承诺；一名开发和一名测试为规划资源假设。安全自举、真实授权及跨存储提交存在估算风险，若设计发现需增长先重算容量，不降低保护来追赶日期。新增主能力1项，未创建Change。

## 跨迭代依赖与执行顺序

```text
REQ-0047和BUG-0062既有恢复基线 + BUG-0063已交付兼容追加事实
  -> REQ-0050创建独立Change
  -> 信任根/授权/自举设计 + UI Contract与Skeleton
  -> 通用验证器及精确启用转换 + 项目围栏和恢复检查点
  -> 独立隔离样本首次成功/拒绝/恢复 + 真实UI/CLI联合验收
  -> 机制自身归档影响在精确引导清单内核验，完成策略转换
  -> BUG-0063另行批准具体替代并按授权归档
  -> sprint-012完整关闭条件重新检查
```

最后两步为跨迭代后续事项，不把BUG-0063移入本迭代，不自动授权其归档、签署或关闭sprint-012。本机制不能要求BUG-0063先归档作为启用前提；已交付代码只能作为有版本指纹的基础，不能冒充已生效规格。机制归档和启用自身循环风险在Change设计先闭合，无独立可信根则保持阻断。

## 横切预防清单

- media-upload：沿用admin-media-upload-chain.md，AC-XCUT-001—004覆盖状态机、同会话回显、真实部署端口、一次性身份及成功附件拒绝后保留；不使用失败附件代替成功路径证据。
- governance-recovery-archive-evidence.md：真实首次成功、失败拒绝与原操作恢复分别留证；保持历史journal/manifest和原AC。
- 20261022-compatible-requirement-successor.md：兼容追加与显式替代分开，未知语义默认拒绝，所有后继逐边验证。
- 原型拆解已完成；Skeleton、1440与390视口、深浅主题、selector与computed style待实施。admin-list/admin-form/admin-modal不适用，本需求是前台Chat局部审阅。

## 知识承接边界

承接最近sprint-011复盘的S10-A002（证据分层与串行样本）及S11-A001（追加范围、缓冲与外部关闭依赖）；仅落实本需求适用部分，不宣称整体行动关闭或自动创建跟进事项。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: usage_events、request_logs、task_traces、task_trace_spans、授权审计、归档执行和Workflow Sync；validation: REQ-0050 AC-003/004/019/020。遵循docs/standards/product-data-collection-observability.md。仅保留安全关联及必要证据摘要，遥测不作为授权依据。N/A：本轮仅规划，无API、DB、UI、部署、安全实现或客户端生成修改；后续按实际设计同步。

## 发布计划

全部适用AC与部署版本一致性核验通过后，分别完成Change归档、Sprint签署与关闭；镜像和生产发布按独立发布链执行。本规划不启用策略、不执行正式替代、不构建镜像或发布。

## 关联文档

- issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/requirement.md
- issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/acceptance.md
- issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/review.md
- issues/bugs/review/BUG-0063-compatible-requirement-successor-blocked/trace.md
- iterations/change/sprint-012/sprint.yaml

## 卡片常驻信息标签追加范围说明

用户明确指定将 REQ-0051-card-persistent-info-tags 纳入 sprint-013，M / 3 人天：数据投影与状态兼容1、标签及文档交互1、测试视觉验收与文档1。不替换已有范围，总投入16/30人天，剩余14人天（46.7%），保留超过30%的返修缓冲。

依赖：
```text
REQ-0051（已评审）
  ├─ 已交付 REQ-0031：Sprint 人天来源
  ├─ 已交付 REQ-0020：文档查看能力
  └─ req-opsx → UI Skeleton → 数据与标签实现 → 18项验收 → 归档
```
与REQ-0050无业务前置依赖；同一工作区验证需保持样本隔离，Sprint整体关闭仍受已有范围约束。

横切预防：prototype-driven-ui-gate.md 对应4项原型AC；需求中心读取性能事故对应AC-XCUT-001/002，复用快照与权限失效，防止逐卡下载；sprint-011当前事实与历史证据区分对应AC-XCUT-003。S10-A001/A002、S11-A001仅承接本需求适用部分；S10-A003与S9-A001不属本次卡片功能范围，保留原行动状态。

product_data_collection_observability: applicable；affected_layers: web、api、usage_events、request_logs；validation: REQ-0051 AC-007/009/011。N/A：不新增长任务、Task Trace/span、DB结构、对象存储写入或部署变更；复用既有文档读取权限与请求观测，遥测失败不阻断读取。

关联：issues/requirements/review/REQ-0051-card-persistent-info-tags/requirement.md、acceptance.md、review.md及prototype/web/context.md。
