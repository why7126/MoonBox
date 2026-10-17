---
note: workflow-sync — workflow-sync 自动同步 — 20/20 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-009
title: 本地数据边界与快照轮转迭代
status: completed
lifecycle_stage: archive
created_at: '2026-10-08 14:40:30'
updated_at: 2026-10-17 17:00:32
---

# 本地数据边界与快照轮转迭代

## 1. Sprint 目标

统一本地数据挂载边界，完成旧 SQLite 数据安全迁移和自动快照轮转；修复 Chat 助手输出与需求中心验收投影、文档入口问题。

### Sprint 目标编号列表

- REQ-0043-unify-data-mount-and-snapshot-rotation
- REQ-0044-shared-project-verification-environment
- BUG-0030-chat-assistant-output-missing-from-conversation
- BUG-0034-chat-standalone-archive-scope-tool-path
- BUG-0035-requirement-center-acceptance-readiness-projection
- BUG-0040-chat-archive-issue-promote-fixture
- BUG-0041-chat-archive-issue-promote-retest
- BUG-0042-chat-archive-issue-promote-retest-2
- migrate-local-host-ports-to-39000-range
- add-git-sync-skill
- harden-browser-evidence-access-verdict
- verify-chat-source-archive-e2e
- verify-chat-archive-transition-window
- verify-chat-cross-mount-copy-archive
- verify-chat-archive-finalize-window
- verify-chat-archive-history-transition
- harden-automated-acceptance-evidence
- harden-opsx-acceptance-preflight-evidence-coverage
- fix-sprint-close-stale-history-scan
- accept-legacy-archive-sample-status

### REQ-0043-unify-data-mount-and-snapshot-rotation 要点

REQ `REQ-0043-unify-data-mount-and-snapshot-rotation`：统一 data 目录边界与本地数据挂载及快照轮转。当前状态 done，估算 8 人天；archived `add-local-data-mount-and-snapshot-rotation`（2026-10-08 17:44:19）。

### REQ-0044-shared-project-verification-environment 要点

REQ `REQ-0044-shared-project-verification-environment`：平台提供跨空间项目验证环境。当前状态 done，估算 8 人天；archived `add-shared-project-verification-environment`（2026-10-08 22:48:00）。

### BUG-0030-chat-assistant-output-missing-from-conversation 要点

BUG `BUG-0030-chat-assistant-output-missing-from-conversation`：Chat 工作台已有助手输出事件但对话正文为空。当前状态 done，估算 5 人天；archived `fix-chat-assistant-output-missing-from-conversation`（2026-10-09 10:34:57）。

### BUG-0034-chat-standalone-archive-scope-tool-path 要点

BUG `BUG-0034-chat-standalone-archive-scope-tool-path`：产品内纯治理 Change 归档因权限与命令路径缺失失败。当前状态 done，估算 3 人天；archived `fix-chat-standalone-archive-scope-tool-path`（2026-10-13 18:51:16）。

### BUG-0035-requirement-center-acceptance-readiness-projection 要点

BUG `BUG-0035-requirement-center-acceptance-readiness-projection`：需求中心卡片验收进度与归档门禁不一致且验收文档入口消失。当前状态 done，估算 5 人天；archived `fix-requirement-center-acceptance-readiness-projection`（2026-10-13 08:26:09）。

### BUG-0040-chat-archive-issue-promote-fixture 要点

BUG `BUG-0040-chat-archive-issue-promote-fixture`：Chat 首次归档关联 Issue 迁移验收夹具。当前状态 done，估算 0.1 人天；archived `fix-chat-archive-issue-promote-fixture`（2026-10-12 11:57:38）。

### BUG-0041-chat-archive-issue-promote-retest 要点

BUG `BUG-0041-chat-archive-issue-promote-retest`：Chat 关联 Issue 首次归档复验夹具。当前状态 done，估算 0.1 人天；archived `fix-chat-archive-issue-promote-retest`（2026-10-12 13:36:39）。

### BUG-0042-chat-archive-issue-promote-retest-2 要点

BUG `BUG-0042-chat-archive-issue-promote-retest-2`：Chat 关联 Issue 首次归档复验夹具。当前状态 done，估算 0.1 人天；archived `fix-chat-archive-issue-promote-retest-2`（2026-10-12 14:14:17）。

### migrate-local-host-ports-to-39000-range 要点

Change `migrate-local-host-ports-to-39000-range`：migrate local host ports to 39000 range。当前状态 archived，估算 2 人天；archived `migrate-local-host-ports-to-39000-range`（2026-10-17 23:59:59）。

### add-git-sync-skill 要点

Change `add-git-sync-skill`：add git sync skill。当前状态 archived，估算 1 人天；archived `add-git-sync-skill`（2026-10-10 23:59:59）。

### harden-browser-evidence-access-verdict 要点

Change `harden-browser-evidence-access-verdict`：harden browser evidence access verdict。当前状态 archived，估算 1 人天；archived `harden-browser-evidence-access-verdict`（2026-10-09 23:59:59）。

### verify-chat-source-archive-e2e 要点

Change `verify-chat-source-archive-e2e`：verify chat source archive e2e。当前状态 archived，估算 0.1 人天；archived `verify-chat-source-archive-e2e`（2026-10-11 23:59:59）。

### verify-chat-archive-transition-window 要点

Change `verify-chat-archive-transition-window`：verify chat archive transition window。当前状态 archived，估算 0.1 人天；archived `verify-chat-archive-transition-window`（2026-10-12 23:59:59）。

### verify-chat-cross-mount-copy-archive 要点

Change `verify-chat-cross-mount-copy-archive`：verify chat cross mount copy archive。当前状态 archived，估算 0.1 人天；archived `verify-chat-cross-mount-copy-archive`（2026-10-12 23:59:59）。

### verify-chat-archive-finalize-window 要点

Change `verify-chat-archive-finalize-window`：verify chat archive finalize window。当前状态 archived，估算 0.1 人天；archived `verify-chat-archive-finalize-window`（2026-10-12 23:59:59）。

### verify-chat-archive-history-transition 要点

Change `verify-chat-archive-history-transition`：verify chat archive history transition。当前状态 archived，估算 0.1 人天；archived `verify-chat-archive-history-transition`（2026-10-12 23:59:59）。

### harden-automated-acceptance-evidence 要点

Change `harden-automated-acceptance-evidence`：harden automated acceptance evidence。当前状态 archived，估算 1 人天；archived `harden-automated-acceptance-evidence`（2026-10-12 23:59:59）。

### harden-opsx-acceptance-preflight-evidence-coverage 要点

Change `harden-opsx-acceptance-preflight-evidence-coverage`：harden opsx acceptance preflight evidence coverage。当前状态 archived，估算 1 人天；archived `harden-opsx-acceptance-preflight-evidence-coverage`（2026-10-12 23:59:59）。

### fix-sprint-close-stale-history-scan 要点

Change `fix-sprint-close-stale-history-scan`：fix sprint close stale history scan。当前状态 archived，估算 0.1 人天；archived `fix-sprint-close-stale-history-scan`（2026-10-17 23:59:59）。

### accept-legacy-archive-sample-status 要点

Change `accept-legacy-archive-sample-status`：accept legacy archive sample status。当前状态 archived，估算 0.09 人天；archived `accept-legacy-archive-sample-status`（2026-10-17 23:59:59）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0043-unify-data-mount-and-snapshot-rotation | 统一 data 目录边界与本地数据挂载及快照轮转 | done | 8 人天 | archived `add-local-data-mount-and-snapshot-rotation`（2026-10-08 17:44:19） |
| REQ | REQ-0044-shared-project-verification-environment | 平台提供跨空间项目验证环境 | done | 8 人天 | archived `add-shared-project-verification-environment`（2026-10-08 22:48:00） |
| BUG | BUG-0030-chat-assistant-output-missing-from-conversation | Chat 工作台已有助手输出事件但对话正文为空 | done | 5 人天 | archived `fix-chat-assistant-output-missing-from-conversation`（2026-10-09 10:34:57） |
| BUG | BUG-0034-chat-standalone-archive-scope-tool-path | 产品内纯治理 Change 归档因权限与命令路径缺失失败 | done | 3 人天 | archived `fix-chat-standalone-archive-scope-tool-path`（2026-10-13 18:51:16） |
| BUG | BUG-0035-requirement-center-acceptance-readiness-projection | 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失 | done | 5 人天 | archived `fix-requirement-center-acceptance-readiness-projection`（2026-10-13 08:26:09） |
| BUG | BUG-0040-chat-archive-issue-promote-fixture | Chat 首次归档关联 Issue 迁移验收夹具 | done | 0.1 人天 | archived `fix-chat-archive-issue-promote-fixture`（2026-10-12 11:57:38） |
| BUG | BUG-0041-chat-archive-issue-promote-retest | Chat 关联 Issue 首次归档复验夹具 | done | 0.1 人天 | archived `fix-chat-archive-issue-promote-retest`（2026-10-12 13:36:39） |
| BUG | BUG-0042-chat-archive-issue-promote-retest-2 | Chat 关联 Issue 首次归档复验夹具 | done | 0.1 人天 | archived `fix-chat-archive-issue-promote-retest-2`（2026-10-12 14:14:17） |
| Change | migrate-local-host-ports-to-39000-range | migrate local host ports to 39000 range | archived | 2 人天 | archived `migrate-local-host-ports-to-39000-range`（2026-10-17 23:59:59） |
| Change | add-git-sync-skill | add git sync skill | archived | 1 人天 | archived `add-git-sync-skill`（2026-10-10 23:59:59） |
| Change | harden-browser-evidence-access-verdict | harden browser evidence access verdict | archived | 1 人天 | archived `harden-browser-evidence-access-verdict`（2026-10-09 23:59:59） |
| Change | verify-chat-source-archive-e2e | verify chat source archive e2e | archived | 0.1 人天 | archived `verify-chat-source-archive-e2e`（2026-10-11 23:59:59） |
| Change | verify-chat-archive-transition-window | verify chat archive transition window | archived | 0.1 人天 | archived `verify-chat-archive-transition-window`（2026-10-12 23:59:59） |
| Change | verify-chat-cross-mount-copy-archive | verify chat cross mount copy archive | archived | 0.1 人天 | archived `verify-chat-cross-mount-copy-archive`（2026-10-12 23:59:59） |
| Change | verify-chat-archive-finalize-window | verify chat archive finalize window | archived | 0.1 人天 | archived `verify-chat-archive-finalize-window`（2026-10-12 23:59:59） |
| Change | verify-chat-archive-history-transition | verify chat archive history transition | archived | 0.1 人天 | archived `verify-chat-archive-history-transition`（2026-10-12 23:59:59） |
| Change | harden-automated-acceptance-evidence | harden automated acceptance evidence | archived | 1 人天 | archived `harden-automated-acceptance-evidence`（2026-10-12 23:59:59） |
| Change | harden-opsx-acceptance-preflight-evidence-coverage | harden opsx acceptance preflight evidence coverage | archived | 1 人天 | archived `harden-opsx-acceptance-preflight-evidence-coverage`（2026-10-12 23:59:59） |
| Change | fix-sprint-close-stale-history-scan | fix sprint close stale history scan | archived | 0.1 人天 | archived `fix-sprint-close-stale-history-scan`（2026-10-17 23:59:59） |
| Change | accept-legacy-archive-sample-status | accept legacy archive sample status | archived | 0.09 人天 | archived `accept-legacy-archive-sample-status`（2026-10-17 23:59:59） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0043 | 统一 data 目录边界与本地数据挂载及快照轮转 | P1 | done | archived `add-local-data-mount-and-snapshot-rotation`（2026-10-08 17:44:19） |
| REQ-0044 | 平台提供跨空间项目验证环境 | P1 | done | archived `add-shared-project-verification-environment`（2026-10-08 22:48:00） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0030 | Chat 工作台已有助手输出事件但对话正文为空 | high | done | archived `fix-chat-assistant-output-missing-from-conversation`（2026-10-09 10:34:57） |
| BUG-0034 | 产品内纯治理 Change 归档因权限与命令路径缺失失败 | high | done | archived `fix-chat-standalone-archive-scope-tool-path`（2026-10-13 18:51:16） |
| BUG-0035 | 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失 | medium | done | archived `fix-requirement-center-acceptance-readiness-projection`（2026-10-13 08:26:09） |
| BUG-0040 | Chat 首次归档关联 Issue 迁移验收夹具 | low | done | archived `fix-chat-archive-issue-promote-fixture`（2026-10-12 11:57:38） |
| BUG-0041 | Chat 关联 Issue 首次归档复验夹具 | low | done | archived `fix-chat-archive-issue-promote-retest`（2026-10-12 13:36:39） |
| BUG-0042 | Chat 关联 Issue 首次归档复验夹具 | low | done | archived `fix-chat-archive-issue-promote-retest-2`（2026-10-12 14:14:17） |
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `add-local-data-mount-and-snapshot-rotation` | REQ-0043-unify-data-mount-and-snapshot-rotation | archived | archived `add-local-data-mount-and-snapshot-rotation`（2026-10-08 17:44:19） |
| `migrate-local-host-ports-to-39000-range` | — | archived | archived `migrate-local-host-ports-to-39000-range`（2026-10-17 23:59:59） |
| `fix-chat-assistant-output-missing-from-conversation` | BUG-0030-chat-assistant-output-missing-from-conversation | archived | archived `fix-chat-assistant-output-missing-from-conversation`（2026-10-09 10:34:57） |
| `add-shared-project-verification-environment` | REQ-0044-shared-project-verification-environment | archived | archived `add-shared-project-verification-environment`（2026-10-08 22:48:00） |
| `add-git-sync-skill` | — | archived | archived `add-git-sync-skill`（2026-10-10 23:59:59） |
| `fix-chat-standalone-archive-scope-tool-path` | BUG-0034-chat-standalone-archive-scope-tool-path | archived | archived `fix-chat-standalone-archive-scope-tool-path`（2026-10-13 18:51:16） |
| `harden-browser-evidence-access-verdict` | — | archived | archived `harden-browser-evidence-access-verdict`（2026-10-09 23:59:59） |
| `fix-requirement-center-acceptance-readiness-projection` | BUG-0035-requirement-center-acceptance-readiness-projection | archived | archived `fix-requirement-center-acceptance-readiness-projection`（2026-10-13 08:26:09） |
| `verify-chat-source-archive-e2e` | — | archived | archived `verify-chat-source-archive-e2e`（2026-10-11 23:59:59） |
| `verify-chat-archive-transition-window` | — | archived | archived `verify-chat-archive-transition-window`（2026-10-12 23:59:59） |
| `verify-chat-cross-mount-copy-archive` | — | archived | archived `verify-chat-cross-mount-copy-archive`（2026-10-12 23:59:59） |
| `verify-chat-archive-finalize-window` | — | archived | archived `verify-chat-archive-finalize-window`（2026-10-12 23:59:59） |
| `verify-chat-archive-history-transition` | — | archived | archived `verify-chat-archive-history-transition`（2026-10-12 23:59:59） |
| `fix-chat-archive-issue-promote-fixture` | BUG-0040-chat-archive-issue-promote-fixture | archived | archived `fix-chat-archive-issue-promote-fixture`（2026-10-12 11:57:38） |
| `fix-chat-archive-issue-promote-retest` | BUG-0041-chat-archive-issue-promote-retest | archived | archived `fix-chat-archive-issue-promote-retest`（2026-10-12 13:36:39） |
| `fix-chat-archive-issue-promote-retest-2` | BUG-0042-chat-archive-issue-promote-retest-2 | archived | archived `fix-chat-archive-issue-promote-retest-2`（2026-10-12 14:14:17） |
| `harden-automated-acceptance-evidence` | — | archived | archived `harden-automated-acceptance-evidence`（2026-10-12 23:59:59） |
| `harden-opsx-acceptance-preflight-evidence-coverage` | — | archived | archived `harden-opsx-acceptance-preflight-evidence-coverage`（2026-10-12 23:59:59） |
| `fix-sprint-close-stale-history-scan` | — | archived | archived `fix-sprint-close-stale-history-scan`（2026-10-17 23:59:59） |
| `accept-legacy-archive-sample-status` | — | archived | archived `accept-legacy-archive-sample-status`（2026-10-17 23:59:59） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0043`、`REQ-0044` 已纳入正式范围；BUG：`BUG-0030`、`BUG-0034`、`BUG-0035`、`BUG-0040`、`BUG-0041`、`BUG-0042` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 8 个范围项关联 Change，另有 12 个纯 Change；20 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 35.99 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 46 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 119.97% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 未知 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 20/20 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 20/20 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 119.97% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-009-retrospective.md` | 20/20 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

- 本范围不涉及管理端列表、表单、弹窗或媒体上传，UI best-practices 为 N/A。
- 数据迁移、快照删除和恢复均需独立留证；不可将合成回归视作真实运行态验收。
- 产品数据采集与链路观测：applicable；DB、chat_messages、execution_events、request_logs、task_traces、task_trace_spans 适用。BUG-0030 关联消息 API 与 Web 展示，按 AC-001至AC-009 验证；新增 usage_events 与请求封装改动暂为 N/A，因当前未新增交互入口或请求协议，修复定案后重新评估。
- BUG-0030 根因仍为 hypothesis；评审豁免不延伸到 bug-opsx 或 apply。历史数据已删除，隔离合成回归用于验证当前机制，真实页面观察单独留证，不冒充原实例根因。
- BUG-0035 验收按 `acceptance.md` 的 AC-001 至 AC-011 核对卡片状态、归档门禁与已生成 MD 的持续入口；分别保留 1440px、390px 视觉证据和真实产品观察。治理上下文与授权文档读取适用，新增行为事件、DB schema 和客户端请求协议目前为 N/A，Change 定案时复核。
- 容量达到 32/30 人天且返修缓冲为 0；若实际投入超出计划，优先保障已纳入的高严重度缺陷及 BUG-0035 验收门禁，建议将尚未启动的新增体验工作移至后续 Sprint，调整正式范围前重算容量并同步四件套。

## 8. 依赖

```text
REQ-0043 已评审
└── sprint-009 规划
    └── req-opsx 创建 Change
        └── 实现、验证与验收
```

BUG-0030 依赖：已评审 → sprint-009 → 根因门禁与 bug-opsx → 修复及 AC-001至AC-009 验收；与本地数据挂载项无已知实现先后依赖。

BUG-0035 依赖：已评审 → sprint-009 → bug-opsx 创建 Change → 修复及 AC-001 至 AC-011 验收；归档门禁需以验收事实为准。

## 9. 发布计划

完成 Change 验收后，按发布流程确认部署、升级和恢复计划；本规划不代表正式发布。

## 10. 关联文档

- `issues/requirements/review/REQ-0043-unify-data-mount-and-snapshot-rotation/requirement.md`
- `issues/requirements/review/REQ-0043-unify-data-mount-and-snapshot-rotation/acceptance.md`
- `docs/knowledge-base/retrospectives/sprint-007-retrospective.md`

- `issues/bugs/review/BUG-0030-chat-assistant-output-missing-from-conversation/acceptance.md`
- `issues/bugs/review/BUG-0030-chat-assistant-output-missing-from-conversation/review.md`
- `issues/bugs/review/BUG-0035-requirement-center-acceptance-readiness-projection/acceptance.md`
- `issues/bugs/review/BUG-0035-requirement-center-acceptance-readiness-projection/trace.md`

## 迭代关闭

2026-10-17 16:53:49，用户确认总体验收通过并授权关闭。20/20 Change 已归档、152/152 任务完成；归档就绪与关闭扫描通过。`sprint.archive` Workflow Sync 发现归档 Change 的 AC-005 样本状态值不符合当前 schema，受控兼容 Change 已归档，关闭同步已续接。发布说明仍为 draft；AI 用量无可归属本地会话，使用 estimated_fallback。

2026-10-17 17:00:07 关闭复核：20/20 Change 已归档，152/152 任务完成，Sprint 总体验收获用户确认；归档就绪、Issue 子文档、env ignore 与陈旧扫描通过。发布说明保留 draft。

## Sprint 经验复盘回链

2026-10-17：复盘已沉淀至 [Sprint-009 经验复盘](../../../docs/knowledge-base/retrospectives/sprint-009-retrospective.md)。行动项 S9-A001 至 S9-A005 为建议，未自动创建 Issue/Change。
