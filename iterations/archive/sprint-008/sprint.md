---
note: workflow-sync — workflow-sync 自动同步 — 13/13 Change archived；0 applied；Sprint `completed`
sprint_id: sprint-008
title: 需求中心治理命令链真实写入迭代
status: completed
lifecycle_stage: archive
created_at: '2026-09-29 16:03:21'
updated_at: 2026-10-17 16:45:27
---

# 需求中心治理命令链真实写入迭代

## 1. Sprint 目标

修复需求中心看板命令展示与真实治理写入链路不一致的问题，优先让 BUG 生成和未实现命令提示回到可追溯事实源，避免用户把普通 Chat 回复或前端模拟流转误认为正式治理结果。

### Sprint 目标编号列表

- REQ-0039-requirement-center-card-chat-session-reuse
- REQ-0027-requirement-center-command-chain-realization
- BUG-0025-requirement-center-command-chain-write-gap
- BUG-0024-login-expired-refresh-not-redirect-login
- BUG-0026-chat-platform-opsx-archive-source-permission
- BUG-0027-page-scroll-bottom-light-background-exposed
- BUG-0029-chat-workbench-nonempty-page-scroll
- BUG-0033-opsx-apply-governance-scope-source-readonly
- enable-agent-browser-product-evidence
- prevent-issue-iteration-tool-dirs
- add-automated-opsx-acceptance
- prefer-codex-browser-for-evidence
- verify-archived-acceptance-artifact-supplement

### REQ-0039-requirement-center-card-chat-session-reuse 要点

REQ `REQ-0039-requirement-center-card-chat-session-reuse`：需求中心卡片动作复用对象会话。当前状态 done，估算 3 人天；archived `add-requirement-center-card-chat-session-reuse`（2026-09-30 09:18:07）。

### REQ-0027-requirement-center-command-chain-realization 要点

REQ `REQ-0027-requirement-center-command-chain-realization`：需求中心卡片全命令产品链路真实化。当前状态 done，估算 8 人天；archived `add-requirement-center-command-chain-realization`（2026-10-04 10:43:55）。

### BUG-0025-requirement-center-command-chain-write-gap 要点

BUG `BUG-0025-requirement-center-command-chain-write-gap`：需求中心看板展示完整治理命令链但多数命令未接入真实写入。当前状态 done，估算 5 人天；archived `fix-requirement-center-command-chain-write-gap`（2026-09-29 16:07:39）。

### BUG-0024-login-expired-refresh-not-redirect-login 要点

BUG `BUG-0024-login-expired-refresh-not-redirect-login`：登录失效时，页面刷新也没有重新定位到登录页。当前状态 done，估算 3 人天；archived `fix-chat-auth-expired-redirect-login`（2026-10-04 12:47:38）。

### BUG-0026-chat-platform-opsx-archive-source-permission 要点

BUG `BUG-0026-chat-platform-opsx-archive-source-permission`：Chat 平台无法归档 source 工作区 Change 且状态未知。当前状态 done，估算 3 人天；archived `fix-chat-platform-opsx-archive-source-permission`（2026-10-05 12:13:08）。

### BUG-0027-page-scroll-bottom-light-background-exposed 要点

BUG `BUG-0027-page-scroll-bottom-light-background-exposed`：页面向上滑动时底部露出浅色背景。当前状态 done，估算 3 人天；archived `fix-page-scroll-root-background-exposed`（2026-10-05 00:10:12）。

### BUG-0029-chat-workbench-nonempty-page-scroll 要点

BUG `BUG-0029-chat-workbench-nonempty-page-scroll`：Chat 工作台非空白对话出现页面级滚动条及底部布局异常。当前状态 done，估算 1 人天；archived `fix-chat-workbench-nonempty-page-scroll`（2026-10-12 23:01:32）。

### BUG-0033-opsx-apply-governance-scope-source-readonly 要点

BUG `BUG-0033-opsx-apply-governance-scope-source-readonly`：产品内执行 opsx-apply 误授治理写权限导致源码只读。当前状态 done，估算 3 人天；archived `fix-opsx-apply-governance-scope-source-readonly`（2026-10-12 23:44:08）。

### enable-agent-browser-product-evidence 要点

Change `enable-agent-browser-product-evidence`：enable agent browser product evidence。当前状态 archived，估算 1 人天；archived `enable-agent-browser-product-evidence`（2026-10-11 23:59:59）。

### prevent-issue-iteration-tool-dirs 要点

Change `prevent-issue-iteration-tool-dirs`：prevent issue iteration tool dirs。当前状态 archived，估算 1 人天；archived `prevent-issue-iteration-tool-dirs`（2026-10-09 23:59:59）。

### add-automated-opsx-acceptance 要点

Change `add-automated-opsx-acceptance`：add automated opsx acceptance。当前状态 archived，估算 3 人天；archived `add-automated-opsx-acceptance`（2026-10-12 23:59:59）。

### prefer-codex-browser-for-evidence 要点

Change `prefer-codex-browser-for-evidence`：prefer codex browser for evidence。当前状态 archived，估算 0.3 人天；archived `prefer-codex-browser-for-evidence`（2026-10-13 23:59:59）。

### verify-archived-acceptance-artifact-supplement 要点

Change `verify-archived-acceptance-artifact-supplement`：verify archived acceptance artifact supplement。当前状态 archived，估算 0.5 人天；archived `verify-archived-acceptance-artifact-supplement`（2026-10-17 23:59:59）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| REQ | REQ-0039-requirement-center-card-chat-session-reuse | 需求中心卡片动作复用对象会话 | done | 3 人天 | archived `add-requirement-center-card-chat-session-reuse`（2026-09-30 09:18:07） |
| REQ | REQ-0027-requirement-center-command-chain-realization | 需求中心卡片全命令产品链路真实化 | done | 8 人天 | archived `add-requirement-center-command-chain-realization`（2026-10-04 10:43:55） |
| BUG | BUG-0025-requirement-center-command-chain-write-gap | 需求中心看板展示完整治理命令链但多数命令未接入真实写入 | done | 5 人天 | archived `fix-requirement-center-command-chain-write-gap`（2026-09-29 16:07:39） |
| BUG | BUG-0024-login-expired-refresh-not-redirect-login | 登录失效时，页面刷新也没有重新定位到登录页 | done | 3 人天 | archived `fix-chat-auth-expired-redirect-login`（2026-10-04 12:47:38） |
| BUG | BUG-0026-chat-platform-opsx-archive-source-permission | Chat 平台无法归档 source 工作区 Change 且状态未知 | done | 3 人天 | archived `fix-chat-platform-opsx-archive-source-permission`（2026-10-05 12:13:08） |
| BUG | BUG-0027-page-scroll-bottom-light-background-exposed | 页面向上滑动时底部露出浅色背景 | done | 3 人天 | archived `fix-page-scroll-root-background-exposed`（2026-10-05 00:10:12） |
| BUG | BUG-0029-chat-workbench-nonempty-page-scroll | Chat 工作台非空白对话出现页面级滚动条及底部布局异常 | done | 1 人天 | archived `fix-chat-workbench-nonempty-page-scroll`（2026-10-12 23:01:32） |
| BUG | BUG-0033-opsx-apply-governance-scope-source-readonly | 产品内执行 opsx-apply 误授治理写权限导致源码只读 | done | 3 人天 | archived `fix-opsx-apply-governance-scope-source-readonly`（2026-10-12 23:44:08） |
| Change | enable-agent-browser-product-evidence | enable agent browser product evidence | archived | 1 人天 | archived `enable-agent-browser-product-evidence`（2026-10-11 23:59:59） |
| Change | prevent-issue-iteration-tool-dirs | prevent issue iteration tool dirs | archived | 1 人天 | archived `prevent-issue-iteration-tool-dirs`（2026-10-09 23:59:59） |
| Change | add-automated-opsx-acceptance | add automated opsx acceptance | archived | 3 人天 | archived `add-automated-opsx-acceptance`（2026-10-12 23:59:59） |
| Change | prefer-codex-browser-for-evidence | prefer codex browser for evidence | archived | 0.3 人天 | archived `prefer-codex-browser-for-evidence`（2026-10-13 23:59:59） |
| Change | verify-archived-acceptance-artifact-supplement | verify archived acceptance artifact supplement | archived | 0.5 人天 | archived `verify-archived-acceptance-artifact-supplement`（2026-10-17 23:59:59） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
| REQ-0039 | 需求中心卡片动作复用对象会话 | P1 | done | archived `add-requirement-center-card-chat-session-reuse`（2026-09-30 09:18:07） |
| REQ-0027 | 需求中心卡片全命令产品链路真实化 | P1 | done | archived `add-requirement-center-command-chain-realization`（2026-10-04 10:43:55） |
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0025 | 需求中心看板展示完整治理命令链但多数命令未接入真实写入 | medium | done | archived `fix-requirement-center-command-chain-write-gap`（2026-09-29 16:07:39） |
| BUG-0024 | 登录失效时，页面刷新也没有重新定位到登录页 | medium | done | archived `fix-chat-auth-expired-redirect-login`（2026-10-04 12:47:38） |
| BUG-0026 | Chat 平台无法归档 source 工作区 Change 且状态未知 | high | done | archived `fix-chat-platform-opsx-archive-source-permission`（2026-10-05 12:13:08） |
| BUG-0027 | 页面向上滑动时底部露出浅色背景 | medium | done | archived `fix-page-scroll-root-background-exposed`（2026-10-05 00:10:12） |
| BUG-0029 | Chat 工作台非空白对话出现页面级滚动条及底部布局异常 | medium | done | archived `fix-chat-workbench-nonempty-page-scroll`（2026-10-12 23:01:32） |
| BUG-0033 | 产品内执行 opsx-apply 误授治理写权限导致源码只读 | high | done | archived `fix-opsx-apply-governance-scope-source-readonly`（2026-10-12 23:44:08） |
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `fix-requirement-center-command-chain-write-gap` | BUG-0025-requirement-center-command-chain-write-gap | archived | archived `fix-requirement-center-command-chain-write-gap`（2026-09-29 16:07:39） |
| `add-requirement-center-card-chat-session-reuse` | REQ-0039-requirement-center-card-chat-session-reuse | archived | archived `add-requirement-center-card-chat-session-reuse`（2026-09-30 09:18:07） |
| `add-requirement-center-command-chain-realization` | REQ-0027-requirement-center-command-chain-realization | archived | archived `add-requirement-center-command-chain-realization`（2026-10-04 10:43:55） |
| `fix-chat-platform-opsx-archive-source-permission` | BUG-0026-chat-platform-opsx-archive-source-permission | archived | archived `fix-chat-platform-opsx-archive-source-permission`（2026-10-05 12:13:08） |
| `fix-chat-auth-expired-redirect-login` | BUG-0024-login-expired-refresh-not-redirect-login | archived | archived `fix-chat-auth-expired-redirect-login`（2026-10-04 12:47:38） |
| `fix-page-scroll-root-background-exposed` | BUG-0027-page-scroll-bottom-light-background-exposed | archived | archived `fix-page-scroll-root-background-exposed`（2026-10-05 00:10:12） |
| `enable-agent-browser-product-evidence` | — | archived | archived `enable-agent-browser-product-evidence`（2026-10-11 23:59:59） |
| `fix-chat-workbench-nonempty-page-scroll` | BUG-0029-chat-workbench-nonempty-page-scroll | archived | archived `fix-chat-workbench-nonempty-page-scroll`（2026-10-12 23:01:32） |
| `fix-opsx-apply-governance-scope-source-readonly` | BUG-0033-opsx-apply-governance-scope-source-readonly | archived | archived `fix-opsx-apply-governance-scope-source-readonly`（2026-10-12 23:44:08） |
| `prevent-issue-iteration-tool-dirs` | — | archived | archived `prevent-issue-iteration-tool-dirs`（2026-10-09 23:59:59） |
| `add-automated-opsx-acceptance` | — | archived | archived `add-automated-opsx-acceptance`（2026-10-12 23:59:59） |
| `prefer-codex-browser-for-evidence` | — | archived | archived `prefer-codex-browser-for-evidence`（2026-10-13 23:59:59） |
| `verify-archived-acceptance-artifact-supplement` | — | archived | archived `verify-archived-acceptance-artifact-supplement`（2026-10-17 23:59:59） |
<!-- workflow-sync:scope-changes:end -->

REQ：`REQ-0039`、`REQ-0027` 已纳入正式范围；BUG：`BUG-0025`、`BUG-0024`、`BUG-0026`、`BUG-0027`、`BUG-0029`、`BUG-0033` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 8 个范围项关联 Change，另有 5 个纯 Change；13 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 34.8 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 36 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 116.00% | `estimated_person_days / capacity_person_days` |
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
| 容量超出计划值 | medium | 容量占用 116.00% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-008-retrospective.md` | 13/13 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->

## 7. 横切预防清单

| 来源 | 适用性 | 验收 gate |
|---|---|---|
| sprint-007-retrospective.md | 高风险入口、需求中心事实源、AI Usage | 入口只做 readiness/确认/权限说明；真实执行必须有后端治理候选与应用事实；用量不可用时明确 warning |
| product-data-collection-observability.md | API、DB、Agent Workflow、Task Trace | 声明四层观测适用，验证 governance candidate/application、request_logs、task_trace/spans 与事实源写入一致 |

## 8. 依赖 ASCII 树

```text
sprint-008
└── BUG-0025（已创建 Change，apply 已完成，待验收归档）
    ├── 扩展 governance-preparations 支持 bug-generate
    ├── 扩展 candidate validate / writer kind 写入 BUG 文档边界
    ├── 前端非 demo 路径区分已实现与未实现命令
    └── 观测与回归测试覆盖治理候选、应用和事实源投影
```

## 9. 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: BUG-0025 修复范围涉及需求中心治理动作入口、聊天治理准备 API、治理候选/应用数据库记录、Agent Workflow 写入链路和前端行为触发。
  validation: 后续 Change 需验证行为事件、请求日志、governance candidate/application、task trace/spans 与 trace/registry/CHANGELOG 写入一致。
```

## BUG-0033 纳入约束

新增 BUG-0033-opsx-apply-governance-scope-source-readonly，严重度 high、根因 confirmed，估算 M / 3 人天。优先解除 BUG-0029 的产品内 apply 实现权限阻塞；BUG-0033 尚未创建 Change，纳入规划不表示已经修复。保留现有 30 人天容量，纳入后 30/30 人天，剩余缓冲 0，低于 30% 建议值；后续新增范围先重算容量，不自动扩容。

承接既有 S7-A004 高风险操作入口门禁与 S7-A005 事实源一致性经验：权限来自服务端可信治理事实，不以 UI 标签或模型执行结束判定写入、实施或验收成功。现有 UI 类 best-practices 对该后端权限修复不直接适用，最终回归采用 BUG-0033 acceptance.md 的合法/非法字段组合与权限边界矩阵。

product_data_collection_observability: applicable；affected_layers: Agent Workflow 权限决策、执行器、request_logs/task_traces/task_trace_spans 的关联留痕。validation：后续 Change 按 AC-011 关联同一 turn 的 write_scope、reason_code、实际 profile 和治理输入版本摘要，覆盖原 BUG-0029 场景；原历史 reason_code 未留存，不能伪造成直接观测。N/A：本轮仅规划，不变更 API、DB、UI、部署、安全策略或客户端生成物，不新增 usage_events，不复制原始 Prompt、凭证或完整治理文件。

## Sprint 关闭记录

2026-10-17 16:43:00（Asia/Shanghai）：13/13 Change 已归档、252/252 任务完成，8 个范围 Issue 已关闭；Sprint 归档就绪、陈旧扫描、目录与环境忽略策略通过。完整验收与 AI Usage 回退说明见 `acceptance-report.md`。发布说明保持草稿，对外发布另走发布链路。

## Sprint 经验复盘回链

2026-10-17：复盘已沉淀至 [Sprint-008 经验复盘](../../../docs/knowledge-base/retrospectives/sprint-008-retrospective.md)。行动项 S8-A001 至 S8-A005 为建议，未自动创建 Issue/Change。
