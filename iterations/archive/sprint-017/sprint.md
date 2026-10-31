---
note: workflow-sync — workflow-sync 自动同步 — 7/7 Change archived；0 applied；Sprint `completed`
title: 独立变更治理迭代规划
created_at: 2026-10-31 07:52:55
updated_at: 2026-10-31 16:03:16
---
# 独立变更治理迭代规划

## 1. Sprint 目标
修复独立提案状态初始化，规划归档工具独立版本路由，并补齐 Chat 执行中的提问、回答与原轮次续接能力。

### Sprint 目标编号列表

- BUG-0058-chat-history-status-replay-request-amplification
- BUG-0072-standalone-change-ready-dev-without-sprint
- BUG-0046-chat-midrun-question-response-unavailable
- BUG-0045-chat-acceptance-runtime-capability-gap
- fix-independent-change-initialization
- add-archive-tool-version-routing
- fix-sprint-close-title-classification

### BUG-0058-chat-history-status-replay-request-amplification 要点

BUG `BUG-0058-chat-history-status-replay-request-amplification`：聊天历史状态重建与重复读取导致加载迟缓。当前状态 done；archived `fix-chat-history-read-lifecycle`（2026-10-31 10:22:33）。

### BUG-0072-standalone-change-ready-dev-without-sprint 要点

BUG `BUG-0072-standalone-change-ready-dev-without-sprint`：独立 Change 未纳入迭代却提前显示待开发。当前状态 done；archived `fix-standalone-change-sprint-stage`（2026-10-31 10:53:17）。

### BUG-0046-chat-midrun-question-response-unavailable 要点

BUG `BUG-0046-chat-midrun-question-response-unavailable`：Chat 命令执行中提出问题但缺少可回答和续接入口。当前状态 done；archived `fix-chat-midrun-question-response`（2026-10-31 12:30:13）。

### BUG-0045-chat-acceptance-runtime-capability-gap 要点

BUG `BUG-0045-chat-acceptance-runtime-capability-gap`：Chat 命令执行环境缺少验收能力导致开发验收中断。当前状态 done；archived `fix-chat-acceptance-runtime-capability`（2026-10-31 15:49:19）。

### fix-independent-change-initialization 要点

Change `fix-independent-change-initialization`：fix independent change initialization。当前状态 archived；archived `fix-independent-change-initialization`（2026-10-31 23:59:59）。

### add-archive-tool-version-routing 要点

Change `add-archive-tool-version-routing`：add archive tool version routing。当前状态 archived；archived `add-archive-tool-version-routing`（2026-10-31 23:59:59）。

### fix-sprint-close-title-classification 要点

Change `fix-sprint-close-title-classification`：fix sprint close title classification。当前状态 archived；archived `fix-sprint-close-title-classification`（2026-10-31 23:59:59）。

## 2. Scope

| 类型 | 编号 | 标题 | 状态 | 估算 | 说明 |
|---|---|---|---|---:|---|
| BUG | BUG-0058-chat-history-status-replay-request-amplification | 聊天历史状态重建与重复读取导致加载迟缓 | done | — | archived `fix-chat-history-read-lifecycle`（2026-10-31 10:22:33） |
| BUG | BUG-0072-standalone-change-ready-dev-without-sprint | 独立 Change 未纳入迭代却提前显示待开发 | done | — | archived `fix-standalone-change-sprint-stage`（2026-10-31 10:53:17） |
| BUG | BUG-0046-chat-midrun-question-response-unavailable | Chat 命令执行中提出问题但缺少可回答和续接入口 | done | — | archived `fix-chat-midrun-question-response`（2026-10-31 12:30:13） |
| BUG | BUG-0045-chat-acceptance-runtime-capability-gap | Chat 命令执行环境缺少验收能力导致开发验收中断 | done | — | archived `fix-chat-acceptance-runtime-capability`（2026-10-31 15:49:19） |
| Change | fix-independent-change-initialization | fix independent change initialization | archived | — | archived `fix-independent-change-initialization`（2026-10-31 23:59:59） |
| Change | add-archive-tool-version-routing | add archive tool version routing | archived | — | archived `add-archive-tool-version-routing`（2026-10-31 23:59:59） |
| Change | fix-sprint-close-title-classification | fix sprint close title classification | archived | — | archived `fix-sprint-close-title-classification`（2026-10-31 23:59:59） |

### 包含需求

<!-- workflow-sync:scope-requirements:start -->
| 编号 | 名称 | 优先级 | 状态 | 说明 |
|---|---|---|---|---|
<!-- workflow-sync:scope-requirements:end -->

### 包含 BUG

<!-- workflow-sync:scope-bugs:start -->
| 编号 | 名称 | 严重度 | 状态 | 说明 |
|---|---|---|---|---|
| BUG-0058 | 聊天历史状态重建与重复读取导致加载迟缓 | high | done | archived `fix-chat-history-read-lifecycle`（2026-10-31 10:22:33） |
| BUG-0072 | 独立 Change 未纳入迭代却提前显示待开发 | medium | done | archived `fix-standalone-change-sprint-stage`（2026-10-31 10:53:17） |
| BUG-0046 | Chat 命令执行中提出问题但缺少可回答和续接入口 | high | done | archived `fix-chat-midrun-question-response`（2026-10-31 12:30:13） |
| BUG-0045 | Chat 命令执行环境缺少验收能力导致开发验收中断 | high | done | archived `fix-chat-acceptance-runtime-capability`（2026-10-31 15:49:19） |
<!-- workflow-sync:scope-bugs:end -->

### 包含 Change

<!-- workflow-sync:scope-changes:start -->
| Change ID | 关联需求 | 状态 | Sprint 目标 |
|---|---|---|---|
| `fix-independent-change-initialization` | — | archived | archived `fix-independent-change-initialization`（2026-10-31 23:59:59） |
| `fix-chat-history-read-lifecycle` | BUG-0058-chat-history-status-replay-request-amplification | archived | archived `fix-chat-history-read-lifecycle`（2026-10-31 10:22:33） |
| `fix-standalone-change-sprint-stage` | BUG-0072-standalone-change-ready-dev-without-sprint | archived | archived `fix-standalone-change-sprint-stage`（2026-10-31 10:53:17） |
| `add-archive-tool-version-routing` | — | archived | archived `add-archive-tool-version-routing`（2026-10-31 23:59:59） |
| `fix-chat-midrun-question-response` | BUG-0046-chat-midrun-question-response-unavailable | archived | archived `fix-chat-midrun-question-response`（2026-10-31 12:30:13） |
| `fix-chat-acceptance-runtime-capability` | BUG-0045-chat-acceptance-runtime-capability-gap | archived | archived `fix-chat-acceptance-runtime-capability`（2026-10-31 15:49:19） |
| `fix-sprint-close-title-classification` | — | archived | archived `fix-sprint-close-title-classification`（2026-10-31 23:59:59） |
<!-- workflow-sync:scope-changes:end -->

REQ：无 已纳入正式范围；BUG：`BUG-0058`、`BUG-0072`、`BUG-0046`、`BUG-0045` 已纳入正式范围，优先级高于新增体验能力；当前完成度与验收风险以 Scope 表状态、关联 Change 和 acceptance-report 为准。

Change：已回填 4 个范围项关联 Change，另有 3 个纯 Change；7 archived，0 applied，0 in_progress，0 proposed。所有已纳入范围项均已关联 Change；执行开发与归档时以 Scope 表逐项状态为准。

## 横切预防清单
承接 [Sprint-016 复盘](../../../docs/knowledge-base/retrospectives/sprint-016-retrospective.md)：S16-A004 追加后重算为27/30人天，保留3人天缓冲（10%，低于建议30%）；后续新增范围须重新评估，优先延后低优先级新增能力；S16-A001 保留完整/部分交付状态与历史证据；S16-A002 用量缺测不记零；S16-A003 聚焦摘要与当前范围校验。相关优化仍为建议，不扩大本次范围。
保留历史事实，真实产品观察与合成回归分别记录。

归档工具版本路由：逐文件 manifest、只读挂载、摘要一致性、显式配置错误阻断、原操作授权与恢复身份保持均纳入验收。实际子容器验证须登记临时环境并完成清理检查；UI 最佳实践标签不适用，本项不重建 Web 页面。

product_data_collection_observability: applicable；affected_layers: Agent Workflow、task_traces、task_trace_spans、部署与脱敏诊断。验证计划覆盖跨入口工具摘要、恢复与重放身份、错误脱敏、历史证据哈希和回滚冻结，实施后提供实际结果。usage_events 不新增页面行为；request_logs 沿用既有可信请求关联；数据库字段、保留周期与客户端请求封装不在本次计划变更范围，实施前复核兼容性。
## 依赖
初始化修复 → 指定提案补齐 → 验收。

```text
add-archive-tool-version-routing
├─ 核实工具入口闭包、原操作授权与版本绑定证据
├─ manifest 与部署受控配置 → Shell/Python/产品路由
├─ Worker 子容器只读挂载 → 跨入口真实验证
└─ 恢复/重放/回滚负例 → 文档与 opsx-accept 证据
```

规划风险：现有恢复记录能否充分绑定工具版本、脚本业务根推导闭包及 Docker 宿主映射仍待验证。不能证明原版本时阻断恢复；不得新增数据库字段或扩大真实部署范围来默认消解风险。

### Chat 执行中问答预防与依赖

BUG-0046-chat-midrun-question-response-unavailable 暂估8人天，覆盖协议双阶段接入2、接口与问题状态2、页面1、回归及真实产品验收2、文档与观测1。估算不是实际投入或交付承诺。已有历史证据作为设计输入，实现前复核当前执行器接口。

保持普通新命令互斥，专用答案回传原轮次；授权、幂等、终止竞争、重连与工作进程恢复均纳入12项验收。1440px/390px下逐状态检查问题卡片，动作建立selector和modal适用性矩阵；真实同轮回答续接与合成协议回归分开报告。admin-list/admin-form/admin-modal/media-upload最佳实践标签不适用，本项为Chat问题卡片。

```text
BUG-0046-chat-midrun-question-response-unavailable
├─ bug-opsx 明确协议能力、问题身份、存储与超时契约
├─ 执行器双阶段接入 → 专用回答接口 → 问题卡片
├─ 授权/幂等/终止竞争/重连恢复验证
└─ 授权隔离样本 → 同轮提问、回答、消费答案与续接证据
```

BUG-0045提供验收环境能力，环境未就绪时仅阻塞相关真实验收；REQ-0046承接整体运行结果提示，本项不重复交付。当前只规划，不创建Change、不执行修复或宣称验收通过。

product_data_collection_observability: applicable；affected_layers: Web、API、问答数据持久化、执行器、request_logs、Task Trace；validation: 沿用BUG acceptance.md AC-002/004/006/007/008/011/012，验证关联身份、权限、幂等与日志脱敏，不记录自由文本答案和凭证。对象存储N/A：无附件存储范围；本命令API/DB schema、部署、安全边界及客户端生成变更N/A：仅更新规划，实施时按最终设计同步。

## 发布计划
本次完成Sprint归档；生产发布与部署另行安排。

## 3. 工作量与容量

<!-- workflow-sync:sprint-capacity-section:start -->
| 指标 | 数值 | 说明 |
|---|---:|---|
| Sprint 容量 | 30 人天 | 来自 `sprint.yaml:capacity_person_days` |
| 估算人天 | 35.5 人天 | 汇总 `scope_estimates[].estimated_person_days` |
| Story Points | 36 SP | 汇总 `scope_estimates[].story_points` |
| 容量占用率 | 118.33% | `estimated_person_days / capacity_person_days` |
| Fix 缓冲 | 0 人天 | 剩余可用容量，低于 0 时按 0 展示 |
| Fix 缓冲率 | 0.00% | `fix_buffer_person_days / capacity_person_days` |
| 容量门禁 | soft-pass：超过 100%，但未超过 120%，需记录容量风险 | Workflow Sync 派生判断 |
<!-- workflow-sync:sprint-capacity-section:end -->
## 4. 里程碑

<!-- workflow-sync:sprint-milestones-section:start -->
| 节点 | 目标日期 | 完成口径 | 当前状态 |
|---|---|---|---|
| Sprint 启动 | 未知 | 四件套创建并纳入正式范围 | completed |
| 范围实现完成 | 未知 | `changes[]` 全部 apply 完成 | 7/7 已 apply 或 archive |
| 归档收口 | 未知 | `changes[]` 全部 archive，验收报告完成 sign-off | 7/7 已 archive，0 待归档 |
<!-- workflow-sync:sprint-milestones-section:end -->
## 5. 风险与缓冲

<!-- workflow-sync:sprint-risks-section:start -->
| 风险 | 等级 | 证据 | 处理建议 |
|---|---|---|---|
| 容量超出计划值 | medium | 容量占用 118.33% | 后续不宜继续追加范围，除非替换或拆分 |
| Fix 缓冲不足 | medium | fix_buffer_person_days=0 人天 | 保留返修优先级，避免新增非必要治理范围 |
<!-- workflow-sync:sprint-risks-section:end -->
## 6. 知识库承接

<!-- workflow-sync:sprint-knowledge-section:start -->
| 承接项 | 触发条件 | 建议事实源 | 当前状态 |
|---|---|---|---|
| Sprint 复盘 | Sprint close 或集中归档前 | `docs/knowledge-base/retrospectives/sprint-017-retrospective.md` | 7/7 Change archived |
| 最佳实践 | 验收中出现可复用规则、脚本或 UI/API/DB 经验 | `docs/knowledge-base/best-practices/` | 由 `/sprint-exps` 基于证据生成或更新 |
| 事故与缺陷经验 | BUG 根因、返修或发布风险具备复用价值 | `docs/knowledge-base/incidents/` | 由 `/sprint-exps` 或后续治理命令按证据沉淀 |
<!-- workflow-sync:sprint-knowledge-section:end -->


## 经验复盘入口

[迭代复盘与行动项](../../../docs/knowledge-base/retrospectives/sprint-017-retrospective.md)：保留用量缺测边界、零缓冲经验及下一轮承接项。
