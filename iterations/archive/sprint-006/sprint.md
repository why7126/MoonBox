---
note: workflow-sync — workflow-sync 自动同步 — 17/17 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-006
status: completed
lifecycle_stage: archive
created_at: 2026-09-14 11:50:43
updated_at: 2026-09-29 14:41:41
---

# sprint-006 迭代规划

## 1. Sprint 目标

聚焦 Workflow Sync 状态传播治理，优先修复 `req.complete` 后 REQ 状态投影残留旧值导致需求中心误报数据漂移的问题。

### Sprint 目标编号列表

- REQ-0030-requirement-center-sprint-completion-metrics
- REQ-0031-requirement-center-current-iteration-capacity
- REQ-0032-requirement-center-sprint-dropdown-status
- REQ-0033-requirement-center-filter-multiselect-search
- REQ-0034-requirement-center-default-current-iteration-cards
- REQ-0028-chat-skill-codex
- REQ-0035-chat-agent-model-reasoning-selector
- BUG-0020-req-complete-status-projection-drift
- BUG-0021-requirement-center-bug-card-severity-display
- BUG-0022-requirement-center-html-preview-auth-lost
- BUG-0018-standalone-change-acceptance-source-unverified
- optimize-openspec-language-change-scope
- enhance-workflow-sync-current-status-block
- solidify-req-opsx-execution-frontmatter-schema
- solidify-bug-opsx-execution-frontmatter-schema
- localize-openspec-cli-template-titles
- ignore-local-vite-cache-directory

### REQ-0030-requirement-center-sprint-completion-metrics 要点

REQ `REQ-0030-requirement-center-sprint-completion-metrics`：需求中心指标卡新增 Sprint 已完成与累计数量。当前状态 done，估算 3 人天；archived `add-requirement-center-sprint-completion-metrics`（2026-09-15 09:33:51）。

### REQ-0031-requirement-center-current-iteration-capacity 要点

REQ `REQ-0031-requirement-center-current-iteration-capacity`：需求中心显示当前迭代容量已使用与总容量。当前状态 done，估算 3 人天；archived `add-requirement-center-current-iteration-capacity`（2026-09-17 08:31:24）。

### REQ-0032-requirement-center-sprint-dropdown-status 要点

REQ `REQ-0032-requirement-center-sprint-dropdown-status`：需求中心 Sprint 下拉列表新增状态展示。当前状态 done，估算 3 人天；archived `add-requirement-center-sprint-dropdown-status`（2026-09-14 15:08:00）。

### REQ-0033-requirement-center-filter-multiselect-search 要点

REQ `REQ-0033-requirement-center-filter-multiselect-search`：需求中心筛选下拉框支持复选搜索多选与排序优化。当前状态 done，估算 3 人天；archived `add-requirement-center-filter-multiselect-search`（2026-09-17 08:30:50）。

### REQ-0034-requirement-center-default-current-iteration-cards 要点

REQ `REQ-0034-requirement-center-default-current-iteration-cards`：需求中心默认只显示当前迭代卡片。当前状态 done，估算 3 人天；archived `add-requirement-center-default-current-iteration-cards`（2026-09-17 08:26:26）。

### REQ-0028-chat-skill-codex 要点

REQ `REQ-0028-chat-skill-codex`：Chat 工作台支持多图片输入、仓库 Skill 快速引用与 Codex 截图基线体验增强。当前状态 done，估算 3 人天；archived `add-chat-workbench-image-skill-context`（2026-09-22 22:44:45）。

### REQ-0035-chat-agent-model-reasoning-selector 要点

REQ `REQ-0035-chat-agent-model-reasoning-selector`：聊天框新增 Agent、模型和推理程序选择。当前状态 done，估算 3 人天；archived `add-chat-agent-model-reasoning-selector`（2026-09-29 14:21:25）。

### BUG-0020-req-complete-status-projection-drift 要点

BUG `BUG-0020-req-complete-status-projection-drift`：req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移。当前状态 done，估算 1 人天；archived `fix-req-complete-status-projection-drift`（2026-09-14 12:16:41）。

### BUG-0021-requirement-center-bug-card-severity-display 要点

BUG `BUG-0021-requirement-center-bug-card-severity-display`：需求中心 BUG 卡片显示优先级 P 值而非严重性。当前状态 done，估算 3 人天；archived `fix-requirement-center-bug-card-severity-display`（2026-09-14 14:38:53）。

### BUG-0022-requirement-center-html-preview-auth-lost 要点

BUG `BUG-0022-requirement-center-html-preview-auth-lost`：需求中心卡片 HTML 预览直开受保护接口导致认证失败。当前状态 done，估算 1 人天；archived `fix-requirement-center-html-preview-auth-lost`（2026-09-14 15:55:27）。

### BUG-0018-standalone-change-acceptance-source-unverified 要点

BUG `BUG-0018-standalone-change-acceptance-source-unverified`：独立 Change 卡片误报验收来源待核实。当前状态 done，估算 1 人天；archived `fix-standalone-change-acceptance-source`（2026-09-15 00:11:09）。

### optimize-openspec-language-change-scope 要点

Change `optimize-openspec-language-change-scope`：optimize openspec language change scope。当前状态 archived，估算 1 人天；archived `optimize-openspec-language-change-scope`（2026-09-14 15:50:00）。

### enhance-workflow-sync-current-status-block 要点

Change `enhance-workflow-sync-current-status-block`：enhance workflow sync current status block。当前状态 archived，估算 0.5 人天；archived `enhance-workflow-sync-current-status-block`（2026-09-14 23:59:59）。

### solidify-req-opsx-execution-frontmatter-schema 要点

Change `solidify-req-opsx-execution-frontmatter-schema`：solidify req opsx execution frontmatter schema。当前状态 archived，估算 0.5 人天；archived `solidify-req-opsx-execution-frontmatter-schema`（2026-09-15 23:59:59）。

### solidify-bug-opsx-execution-frontmatter-schema 要点

Change `solidify-bug-opsx-execution-frontmatter-schema`：solidify bug opsx execution frontmatter schema。当前状态 archived，估算 0.5 人天；archived `solidify-bug-opsx-execution-frontmatter-schema`（2026-09-14 23:59:59）。

### localize-openspec-cli-template-titles 要点

Change `localize-openspec-cli-template-titles`：localize openspec cli template titles。当前状态 archived，估算 0.5 人天；archived `localize-openspec-cli-template-titles`（2026-09-15 00:26:00）。

### ignore-local-vite-cache-directory 要点

Change `ignore-local-vite-cache-directory`：ignore local vite cache directory。当前状态 archived，估算 0.25 人天；archived `ignore-local-vite-cache-directory`（2026-09-15 00:32:00）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0030-requirement-center-sprint-completion-metrics | 需求中心指标卡新增 Sprint 已完成与累计数量 | done | 3 人天 | archived `add-requirement-center-sprint-completion-metrics`（2026-09-15 09:33:51） |
| REQ | REQ-0031-requirement-center-current-iteration-capacity | 需求中心显示当前迭代容量已使用与总容量 | done | 3 人天 | archived `add-requirement-center-current-iteration-capacity`（2026-09-17 08:31:24） |
| REQ | REQ-0032-requirement-center-sprint-dropdown-status | 需求中心 Sprint 下拉列表新增状态展示 | done | 3 人天 | archived `add-requirement-center-sprint-dropdown-status`（2026-09-14 15:08:00） |
| REQ | REQ-0033-requirement-center-filter-multiselect-search | 需求中心筛选下拉框支持复选搜索多选与排序优化 | done | 3 人天 | archived `add-requirement-center-filter-multiselect-search`（2026-09-17 08:30:50） |
| REQ | REQ-0034-requirement-center-default-current-iteration-cards | 需求中心默认只显示当前迭代卡片 | done | 3 人天 | archived `add-requirement-center-default-current-iteration-cards`（2026-09-17 08:26:26） |
| REQ | REQ-0028-chat-skill-codex | Chat 工作台支持多图片输入、仓库 Skill 快速引用与 Codex 截图基线体验增强 | done | 3 人天 | archived `add-chat-workbench-image-skill-context`（2026-09-22 22:44:45） |
| REQ | REQ-0035-chat-agent-model-reasoning-selector | 聊天框新增 Agent、模型和推理程序选择 | done | 3 人天 | archived `add-chat-agent-model-reasoning-selector`（2026-09-29 14:21:25） |
| BUG | BUG-0020-req-complete-status-projection-drift | req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移 | done | 1 人天 | archived `fix-req-complete-status-projection-drift`（2026-09-14 12:16:41） |
| BUG | BUG-0021-requirement-center-bug-card-severity-display | 需求中心 BUG 卡片显示优先级 P 值而非严重性 | done | 3 人天 | archived `fix-requirement-center-bug-card-severity-display`（2026-09-14 14:38:53） |
| BUG | BUG-0022-requirement-center-html-preview-auth-lost | 需求中心卡片 HTML 预览直开受保护接口导致认证失败 | done | 1 人天 | archived `fix-requirement-center-html-preview-auth-lost`（2026-09-14 15:55:27） |
| BUG | BUG-0018-standalone-change-acceptance-source-unverified | 独立 Change 卡片误报验收来源待核实 | done | 1 人天 | archived `fix-standalone-change-acceptance-source`（2026-09-15 00:11:09） |
| Change | optimize-openspec-language-change-scope | optimize openspec language change scope | archived | 1 人天 | archived `optimize-openspec-language-change-scope`（2026-09-14 15:50:00） |
| Change | enhance-workflow-sync-current-status-block | enhance workflow sync current status block | archived | 0.5 人天 | archived `enhance-workflow-sync-current-status-block`（2026-09-14 23:59:59） |
| Change | solidify-req-opsx-execution-frontmatter-schema | solidify req opsx execution frontmatter schema | archived | 0.5 人天 | archived `solidify-req-opsx-execution-frontmatter-schema`（2026-09-15 23:59:59） |
| Change | solidify-bug-opsx-execution-frontmatter-schema | solidify bug opsx execution frontmatter schema | archived | 0.5 人天 | archived `solidify-bug-opsx-execution-frontmatter-schema`（2026-09-14 23:59:59） |
| Change | localize-openspec-cli-template-titles | localize openspec cli template titles | archived | 0.5 人天 | archived `localize-openspec-cli-template-titles`（2026-09-15 00:26:00） |
| Change | ignore-local-vite-cache-directory | ignore local vite cache directory | archived | 0.25 人天 | archived `ignore-local-vite-cache-directory`（2026-09-15 00:32:00） |

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0030 | 需求中心指标卡新增 Sprint 已完成与累计数量 | P1 | done | archived `add-requirement-center-sprint-completion-metrics`（2026-09-15 09:33:51） |
| REQ-0031 | 需求中心显示当前迭代容量已使用与总容量 | P1 | done | archived `add-requirement-center-current-iteration-capacity`（2026-09-17 08:31:24） |
| REQ-0032 | 需求中心 Sprint 下拉列表新增状态展示 | P2 | done | archived `add-requirement-center-sprint-dropdown-status`（2026-09-14 15:08:00） |
| REQ-0033 | 需求中心筛选下拉框支持复选搜索多选与排序优化 | P1 | done | archived `add-requirement-center-filter-multiselect-search`（2026-09-17 08:30:50） |
| REQ-0034 | 需求中心默认只显示当前迭代卡片 | P1 | done | archived `add-requirement-center-default-current-iteration-cards`（2026-09-17 08:26:26） |
| REQ-0028 | Chat 工作台支持多图片输入、仓库 Skill 快速引用与 Codex 截图基线体验增强 | P1 | done | archived `add-chat-workbench-image-skill-context`（2026-09-22 22:44:45） |
| REQ-0035 | 聊天框新增 Agent、模型和推理程序选择 | P1 | done | archived `add-chat-agent-model-reasoning-selector`（2026-09-29 14:21:25） |
<!-- workflow-sync:scope-requirements:end -->

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0020 | req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移 | medium | done | archived `fix-req-complete-status-projection-drift`（2026-09-14 12:16:41） |
| BUG-0021 | 需求中心 BUG 卡片显示优先级 P 值而非严重性 | medium | done | archived `fix-requirement-center-bug-card-severity-display`（2026-09-14 14:38:53） |
| BUG-0022 | 需求中心卡片 HTML 预览直开受保护接口导致认证失败 | medium | done | archived `fix-requirement-center-html-preview-auth-lost`（2026-09-14 15:55:27） |
| BUG-0018 | 独立 Change 卡片误报验收来源待核实 | medium | done | archived `fix-standalone-change-acceptance-source`（2026-09-15 00:11:09） |
<!-- workflow-sync:scope-bugs:end -->

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `fix-req-complete-status-projection-drift` | BUG-0020-req-complete-status-projection-drift | archived | archived `fix-req-complete-status-projection-drift`（2026-09-14 12:16:41） |
| `fix-requirement-center-bug-card-severity-display` | BUG-0021-requirement-center-bug-card-severity-display | archived | archived `fix-requirement-center-bug-card-severity-display`（2026-09-14 14:38:53） |
| `add-requirement-center-sprint-dropdown-status` | REQ-0032-requirement-center-sprint-dropdown-status | archived | archived `add-requirement-center-sprint-dropdown-status`（2026-09-14 15:08:00） |
| `add-requirement-center-current-iteration-capacity` | REQ-0031-requirement-center-current-iteration-capacity | archived | archived `add-requirement-center-current-iteration-capacity`（2026-09-17 08:31:24） |
| `add-requirement-center-filter-multiselect-search` | REQ-0033-requirement-center-filter-multiselect-search | archived | archived `add-requirement-center-filter-multiselect-search`（2026-09-17 08:30:50） |
| `add-requirement-center-sprint-completion-metrics` | REQ-0030-requirement-center-sprint-completion-metrics | archived | archived `add-requirement-center-sprint-completion-metrics`（2026-09-15 09:33:51） |
| `optimize-openspec-language-change-scope` | — | archived | archived `optimize-openspec-language-change-scope`（2026-09-14 15:50:00） |
| `add-requirement-center-default-current-iteration-cards` | REQ-0034-requirement-center-default-current-iteration-cards | archived | archived `add-requirement-center-default-current-iteration-cards`（2026-09-17 08:26:26） |
| `enhance-workflow-sync-current-status-block` | — | archived | archived `enhance-workflow-sync-current-status-block`（2026-09-14 23:59:59） |
| `fix-requirement-center-html-preview-auth-lost` | BUG-0022-requirement-center-html-preview-auth-lost | archived | archived `fix-requirement-center-html-preview-auth-lost`（2026-09-14 15:55:27） |
| `solidify-req-opsx-execution-frontmatter-schema` | — | archived | archived `solidify-req-opsx-execution-frontmatter-schema`（2026-09-15 23:59:59） |
| `solidify-bug-opsx-execution-frontmatter-schema` | — | archived | archived `solidify-bug-opsx-execution-frontmatter-schema`（2026-09-14 23:59:59） |
| `add-chat-workbench-image-skill-context` | REQ-0028-chat-skill-codex | archived | archived `add-chat-workbench-image-skill-context`（2026-09-22 22:44:45） |
| `fix-standalone-change-acceptance-source` | BUG-0018-standalone-change-acceptance-source-unverified | archived | archived `fix-standalone-change-acceptance-source`（2026-09-15 00:11:09） |
| `add-chat-agent-model-reasoning-selector` | REQ-0035-chat-agent-model-reasoning-selector | archived | archived `add-chat-agent-model-reasoning-selector`（2026-09-29 14:21:25） |
| `localize-openspec-cli-template-titles` | — | archived | archived `localize-openspec-cli-template-titles`（2026-09-15 00:26:00） |
| `ignore-local-vite-cache-directory` | — | archived | archived `ignore-local-vite-cache-directory`（2026-09-15 00:32:00） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0030`、`REQ-0031`、`REQ-0032`、`REQ-0033`、`REQ-0034`、`REQ-0028`、`REQ-0035` 已纳入正式范围；BUG：`BUG-0020`、`BUG-0021`、`BUG-0022`、`BUG-0018` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 11 个范围项关联 Change，另有 6 个纯 Change；17 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 30.25 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 33 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 100.83% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 未知 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 17/17 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 17/17 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 100.83% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-006-retrospective.md` | 17/17 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

| 来源 | 适用性 | 验收 gate 摘要 |
|---|---|---|
| Sprint-005 复盘 | applicable | 状态、路径、当前态看板必须以机器事实源和 Workflow Sync 校验为准 |

## 8. 依赖 ASCII 树

```text
sprint-006
└── BUG-0020 req.complete 状态传播漂移修复
    └── fix-req-complete-status-projection-drift 已归档
```

## 9. 发布计划

本 Sprint 初始范围为治理缺陷修复；发布说明由 `release-note.md` 和后续 Change 验收结果同步。

## 10. 关闭记录

Sprint 于 2026-09-29 14:40:34 完成归档闭环：17/17 Change 已归档，322/322 任务完成，readiness、stale scan、环境 ignore 策略和 Issue promote gate 均通过。AI Usage 自动发现未找到可归因 token_count command run，本次关闭报告按 `usage_mode: unavailable` / `estimated_fallback` 记录，不作为真实 token 统计。

复盘已沉淀到 `docs/knowledge-base/retrospectives/sprint-006-retrospective.md`，后续 `/sprint-propose` 应读取其中 open 行动项。

## 11. 关联文档

- `issues/bugs/archive/BUG-0020-req-complete-status-projection-drift/`
- `docs/knowledge-base/retrospectives/sprint-005-retrospective.md`

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-29 14:40:34 | /sprint-archive | 17/17 Change 已归档，Sprint 关闭并迁入 archive；AI Usage 使用 estimated fallback warning。 |
| 2026-09-14 11:50:43 | /sprint-propose | 创建 sprint-006 初始四件套，准备纳入 BUG-0020。 |
