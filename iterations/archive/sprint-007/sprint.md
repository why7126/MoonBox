---
note: workflow-sync — workflow-sync 自动同步 — 13/13 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-007
title: Capture 图文候选审阅与可靠创建迭代
status: planning
lifecycle_stage: change
created_at: '2026-09-15 00:03:01'
updated_at: 2026-09-29 14:44:19
---

# sprint-007 迭代规划

## 1. Sprint 目标

交付 REQ-0029 的“图文输入 → AI 整理 → 候选审阅 → 确认版本 → 服务端编号与批量采集”闭环，并交付 REQ-0037 的当前迭代归档入口与 Sprint archive readiness 门禁入口。

### Sprint 目标编号列表

- REQ-0029-capture-multimodal-candidate-review
- REQ-0037-current-iteration-archive-entry
- REQ-0036-requirement-center-document-drawer-simplification
- BUG-0017-compose-container-name-suffix-one
- BUG-0019-requirement-center-issue-title-overridden
- BUG-0023-requirement-center-acceptance-progress-task-classification
- optimize-opsx-modify-acceptance-fix-ledger
- unify-change-delivery-evidence-source
- add-change-delivery-evidence-source-check
- clarify-opsx-modify-repair-stage-flow
- sync-sprint-propose-bug-main-status
- add-capture-dedup-gate
- standardize-data-runtime-storage-layout

### REQ-0029-capture-multimodal-candidate-review 要点

REQ `REQ-0029-capture-multimodal-candidate-review`：新建 Capture 支持图文 AI 整理、候选审阅与确认后幂等批量采集。当前状态 done，估算 8 人天；archived `add-capture-multimodal-candidate-review`（2026-09-16 23:48:00）。

### REQ-0037-current-iteration-archive-entry 要点

REQ `REQ-0037-current-iteration-archive-entry`：当前迭代容量区域新增归档当前迭代入口。当前状态 done，估算 3 人天；archived `add-current-iteration-archive-entry`（2026-09-15 09:33:51）。

### REQ-0036-requirement-center-document-drawer-simplification 要点

REQ `REQ-0036-requirement-center-document-drawer-simplification`：需求中心文档抽屉简化与 Change 属性模块移除。当前状态 done，估算 1 人天；archived `remove-requirement-center-document-drawer-change-attributes`（2026-09-16 08:45:49）。

### BUG-0017-compose-container-name-suffix-one 要点

BUG `BUG-0017-compose-container-name-suffix-one`：容器名不应自动追加 -1 后缀。当前状态 done，估算 3 人天；archived `fix-compose-container-name-suffix-one`（2026-09-15 00:27:00）。

### BUG-0019-requirement-center-issue-title-overridden 要点

BUG `BUG-0019-requirement-center-issue-title-overridden`：需求中心阶段业务标题来源与文档中文标题校验。当前状态 done，估算 5 人天；archived `fix-requirement-center-stage-business-titles`（2026-09-29 14:18:37）。

### BUG-0023-requirement-center-acceptance-progress-task-classification 要点

BUG `BUG-0023-requirement-center-acceptance-progress-task-classification`：需求中心验收中卡片进度未按 tasks.md 分类统计返修任务。当前状态 done，估算 5 人天；archived `fix-requirement-center-acceptance-progress-task-classification`（2026-09-17 10:24:34）。

### optimize-opsx-modify-acceptance-fix-ledger 要点

Change `optimize-opsx-modify-acceptance-fix-ledger`：optimize opsx modify acceptance fix ledger。当前状态 archived，估算 1 人天；archived `optimize-opsx-modify-acceptance-fix-ledger`（2026-09-15 09:33:51）。

### unify-change-delivery-evidence-source 要点

Change `unify-change-delivery-evidence-source`：unify change delivery evidence source。当前状态 archived，估算 1 人天；archived `unify-change-delivery-evidence-source`（2026-09-15 09:53:14）。

### add-change-delivery-evidence-source-check 要点

Change `add-change-delivery-evidence-source-check`：add change delivery evidence source check。当前状态 archived，估算 1 人天；archived `add-change-delivery-evidence-source-check`（2026-09-15 09:38:43）。

### clarify-opsx-modify-repair-stage-flow 要点

Change `clarify-opsx-modify-repair-stage-flow`：clarify opsx modify repair stage flow。当前状态 archived，估算 1 人天；archived `clarify-opsx-modify-repair-stage-flow`（2026-09-15 09:52:59）。

### sync-sprint-propose-bug-main-status 要点

Change `sync-sprint-propose-bug-main-status`：sync sprint propose bug main status。当前状态 archived，估算 0.5 人天；archived `sync-sprint-propose-bug-main-status`（2026-09-17 23:59:59）。

### add-capture-dedup-gate 要点

Change `add-capture-dedup-gate`：add capture dedup gate。当前状态 archived，估算 0.5 人天；archived `add-capture-dedup-gate`（2026-09-17 23:59:59）。

### standardize-data-runtime-storage-layout 要点

Change `standardize-data-runtime-storage-layout`：standardize data runtime storage layout。当前状态 archived，估算 0.5 人天；archived `standardize-data-runtime-storage-layout`（2026-09-18 16:07:12）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0029-capture-multimodal-candidate-review | 新建 Capture 支持图文 AI 整理、候选审阅与确认后幂等批量采集 | done | 8 人天 | archived `add-capture-multimodal-candidate-review`（2026-09-16 23:48:00） |
| REQ | REQ-0037-current-iteration-archive-entry | 当前迭代容量区域新增归档当前迭代入口 | done | 3 人天 | archived `add-current-iteration-archive-entry`（2026-09-15 09:33:51） |
| REQ | REQ-0036-requirement-center-document-drawer-simplification | 需求中心文档抽屉简化与 Change 属性模块移除 | done | 1 人天 | archived `remove-requirement-center-document-drawer-change-attributes`（2026-09-16 08:45:49） |
| BUG | BUG-0017-compose-container-name-suffix-one | 容器名不应自动追加 -1 后缀 | done | 3 人天 | archived `fix-compose-container-name-suffix-one`（2026-09-15 00:27:00） |
| BUG | BUG-0019-requirement-center-issue-title-overridden | 需求中心阶段业务标题来源与文档中文标题校验 | done | 5 人天 | archived `fix-requirement-center-stage-business-titles`（2026-09-29 14:18:37） |
| BUG | BUG-0023-requirement-center-acceptance-progress-task-classification | 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务 | done | 5 人天 | archived `fix-requirement-center-acceptance-progress-task-classification`（2026-09-17 10:24:34） |
| Change | optimize-opsx-modify-acceptance-fix-ledger | optimize opsx modify acceptance fix ledger | archived | 1 人天 | archived `optimize-opsx-modify-acceptance-fix-ledger`（2026-09-15 09:33:51） |
| Change | unify-change-delivery-evidence-source | unify change delivery evidence source | archived | 1 人天 | archived `unify-change-delivery-evidence-source`（2026-09-15 09:53:14） |
| Change | add-change-delivery-evidence-source-check | add change delivery evidence source check | archived | 1 人天 | archived `add-change-delivery-evidence-source-check`（2026-09-15 09:38:43） |
| Change | clarify-opsx-modify-repair-stage-flow | clarify opsx modify repair stage flow | archived | 1 人天 | archived `clarify-opsx-modify-repair-stage-flow`（2026-09-15 09:52:59） |
| Change | sync-sprint-propose-bug-main-status | sync sprint propose bug main status | archived | 0.5 人天 | archived `sync-sprint-propose-bug-main-status`（2026-09-17 23:59:59） |
| Change | add-capture-dedup-gate | add capture dedup gate | archived | 0.5 人天 | archived `add-capture-dedup-gate`（2026-09-17 23:59:59） |
| Change | standardize-data-runtime-storage-layout | standardize data runtime storage layout | archived | 0.5 人天 | archived `standardize-data-runtime-storage-layout`（2026-09-18 16:07:12） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0029 | 新建 Capture 支持图文 AI 整理、候选审阅与确认后幂等批量采集 | P1 | done | archived `add-capture-multimodal-candidate-review`（2026-09-16 23:48:00） |
| REQ-0037 | 当前迭代容量区域新增归档当前迭代入口 | P1 | done | archived `add-current-iteration-archive-entry`（2026-09-15 09:33:51） |
| REQ-0036 | 需求中心文档抽屉简化与 Change 属性模块移除 | P2 | done | archived `remove-requirement-center-document-drawer-change-attributes`（2026-09-16 08:45:49） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0017 | 容器名不应自动追加 -1 后缀 | medium | done | archived `fix-compose-container-name-suffix-one`（2026-09-15 00:27:00） |
| BUG-0019 | 需求中心阶段业务标题来源与文档中文标题校验 | medium | done | archived `fix-requirement-center-stage-business-titles`（2026-09-29 14:18:37） |
| BUG-0023 | 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务 | medium | done | archived `fix-requirement-center-acceptance-progress-task-classification`（2026-09-17 10:24:34） |
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `add-current-iteration-archive-entry` | REQ-0037-current-iteration-archive-entry | archived | archived `add-current-iteration-archive-entry`（2026-09-15 09:33:51） |
| `fix-compose-container-name-suffix-one` | BUG-0017-compose-container-name-suffix-one | archived | archived `fix-compose-container-name-suffix-one`（2026-09-15 00:27:00） |
| `add-capture-multimodal-candidate-review` | REQ-0029-capture-multimodal-candidate-review | archived | archived `add-capture-multimodal-candidate-review`（2026-09-16 23:48:00） |
| `optimize-opsx-modify-acceptance-fix-ledger` | — | archived | archived `optimize-opsx-modify-acceptance-fix-ledger`（2026-09-15 09:33:51） |
| `unify-change-delivery-evidence-source` | — | archived | archived `unify-change-delivery-evidence-source`（2026-09-15 09:53:14） |
| `add-change-delivery-evidence-source-check` | — | archived | archived `add-change-delivery-evidence-source-check`（2026-09-15 09:38:43） |
| `clarify-opsx-modify-repair-stage-flow` | — | archived | archived `clarify-opsx-modify-repair-stage-flow`（2026-09-15 09:52:59） |
| `fix-requirement-center-stage-business-titles` | BUG-0019-requirement-center-issue-title-overridden | archived | archived `fix-requirement-center-stage-business-titles`（2026-09-29 14:18:37） |
| `fix-requirement-center-acceptance-progress-task-classification` | BUG-0023-requirement-center-acceptance-progress-task-classification | archived | archived `fix-requirement-center-acceptance-progress-task-classification`（2026-09-17 10:24:34） |
| `sync-sprint-propose-bug-main-status` | — | archived | archived `sync-sprint-propose-bug-main-status`（2026-09-17 23:59:59） |
| `remove-requirement-center-document-drawer-change-attributes` | REQ-0036-requirement-center-document-drawer-simplification | archived | archived `remove-requirement-center-document-drawer-change-attributes`（2026-09-16 08:45:49） |
| `add-capture-dedup-gate` | — | archived | archived `add-capture-dedup-gate`（2026-09-17 23:59:59） |
| `standardize-data-runtime-storage-layout` | — | archived | archived `standardize-data-runtime-storage-layout`（2026-09-18 16:07:12） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0029`、`REQ-0037`、`REQ-0036` 已纳入正式范围；BUG：`BUG-0017`、`BUG-0019`、`BUG-0023` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 6 个范围项关联 Change，另有 7 个纯 Change；13 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 30.5 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 32 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 101.67% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 未知 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 13/13 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 13/13 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 101.67% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-007-retrospective.md` | 13/13 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

| 来源 | 适用性 | 验收 gate |
|---|---|---|
| admin-media-upload-chain.md | media-upload | 6 条 AC-XCUT：状态机、即时回显、授权脱敏、实际 Web 端口、一次性身份、浏览器/容器/模型读取一致 |
| 20260912-capture-persistence.md | 批量采集 | 受理不等于成功；锁内编号；同版本幂等；读取屏障；已知镜像向前恢复；外部冲突不覆盖 |
| sprint-005-retrospective.md | 状态与证据 | 以真实文件及注册表为事实源，合成回归与真实部署观察分别验收，关闭前检查状态与路径残留 |

### 最近复盘 open 行动项审视

| 行动项 | 本 Sprint 承接方式 |
|---|---|
| S5-A001 | 关闭前检查本需求与Change状态/路径残留；不自动开发全局修复工具 |
| S5-A002 | 尝试用量采集，无法归因明确报告；不将0当真实消耗 |
| S5-A003 | 检查按当前需求/迭代聚焦；不新增Fact Sheet功能 |
| S5-A004 | 在本需求结果中保留正式记录、确认版本与来源映射，不扩展其他卡片 |
| S5-A005 | sprint-006 加入后125%已硬阻断，本次用户指定拆分；保留30人天容量 |
| S5-A006 | RC-003 与 AC-PROTOTYPE 覆盖动作族、真实视觉和权限门禁；不自动新建最佳实践Issue |

### 本次纳入约束

REQ-0029 的 RC-001 图片、来源授权与删除保留；RC-002 确认版本、幂等和恢复；RC-003 原型未模拟状态、UI Skeleton、真实视觉和质量样例。REQ-0037 的入口启用状态必须来自 Sprint archive readiness 汇总；当范围内任一 REQ、BUG 或独立 Change 未归档闭环时，入口隐藏或禁用并展示安全摘要。以上作为后续 Change 设计与验收门禁，不能因复用原型而省略。

## 8. 依赖 ASCII 树

```text
sprint-007
├── REQ-0029（已评审，纳入后创建 Change）
│   ├── 已有 Capture 受控写入与编号机制
│   ├── REQ-0028 附件接口协调（位于 sprint-006，不依赖其整体交付）
│   ├── UI Contract / Skeleton 首轮确认
│   ├── 候选版本与整批创建恢复
│   └── 真实图文样例、部署/权限、视觉与36条AC验收
└── REQ-0037（已评审，纳入后创建 Change）
    ├── 当前迭代容量区域与操作区入口
    ├── Sprint archive readiness 汇总
    ├── 未归档 REQ/BUG/独立 Change 安全摘要
    └── 权限、sign-off、Workflow Sync 与 Sprint archive 既有门禁
```

两个活动 Sprint 共存时，后续范围命令显式指定 Sprint。当前规划窗口采用默认两周，角色暂按1开发/1测试作估算，不代表已确认并行人员可用性；执行前安排共享资源顺序，容量不按人员或日期重新计算。

## 9. 发布计划

仅在关联 Change 完成实施、真实验收和归档后形成可发布范围。当前未创建 Change，不宣称功能上线。发布镜像、生产升级和正式发布通过各自命令处理。

## 10. 关联文档

- `issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/requirement.md`
- `issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/review.md`
- `issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/acceptance.md`
- `issues/requirements/review/REQ-0037-current-iteration-archive-entry/requirement.md`
- `issues/requirements/review/REQ-0037-current-iteration-archive-entry/review.md`
- `issues/requirements/review/REQ-0037-current-iteration-archive-entry/acceptance.md`
- `docs/knowledge-base/best-practices/admin-media-upload-chain.md`
- `docs/knowledge-base/incidents/20260912-capture-persistence.md`
- `docs/knowledge-base/retrospectives/sprint-005-retrospective.md`
- `docs/knowledge-base/retrospectives/sprint-007-retrospective.md`

## 产品数据采集与链路观测

`product_data_collection_observability: applicable`；`affected_layers` 为 usage_events、request_logs、task_traces、task_trace_spans。REQ-0029 图文上传与候选/确认任务四层均适用；REQ-0037 归档入口和门禁链路覆盖 usage_events、request_logs 与 task_traces，并继承 Sprint archive 的 Workflow Sync 观测要求。validation：需求已有声明与AC；实施验证可信request_id、节点结果、脱敏、观测故障降级和API/DB/客户端同步。事实源为 `docs/standards/product-data-collection-observability.md`。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-15 00:03:01 | /sprint-propose | 用户指定 sprint-007 承接 REQ-0029；XL 8人天，容量30，缓冲22；未迁移 sprint-006 既有范围。 |
| 2026-09-15 00:03:55 | /sprint-propose | 用户指定 sprint-007 追加 REQ-0037；M 3人天，总估算11人天，容量30，缓冲19。 |
| 2026-09-29 14:42:54 | /sprint-archive | 13/13 Change 已归档；Issue 子文档关闭态一致性、readiness、env ignore、stale scan 和 promote gate 通过；AI Usage Snapshot 自动发现不可用，按 warning 记录。 |

## BUG-0019 规划补充与横切预防

本次追加 BUG-0019-requirement-center-issue-title-overridden，L=5 人天。总估算23/30人天，剩余7人天（23.3%），低于30%建议缓冲；暂不增加额外范围，后续估算增长时优先重新排期未启动范围，不能静默压缩回归与真实观察。

知识库承接：沿用最近 sprint-005 复盘，S5-A004 的事实源可解释性用于阶段标题来源与回退验证，S5-A006 的视觉证据经验用于1440px观察；仅复用经验，不将其独立建议自动加入范围。admin-list 最佳实践适用于后台CRUD，本项为需求看板标题，分页和行内操作门禁不适用；保留对象身份、既有点击行为及长标题布局回归。

依赖顺序：BUG-0019 已批准 → 本 Sprint 正式纳入 → bug-opsx → 标题读取/生成校验实施 → 13项验收；未创建修复 Change，不依赖修改其他 Issue 的真实阶段。

product_data_collection_observability: not_applicable（仅本次 BUG-0019 增量）

affected_layers: web、治理文档读取、文档生成与校验；本项不新增行为事件、请求日志、Task Trace、DB或对象存储行为，既有Sprint其他范围的applicable声明保留。validation：规划核对完成，后续按AC-001至AC-013验证；实现若改变API/观测边界需重新评估。
