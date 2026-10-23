---
bug_id: BUG-0063-compatible-requirement-successor-blocked
title: 同条文兼容追加被归档后继冲突门禁拒绝
status: done
created_at: '2026-10-22 08:58:14'
updated_at: 2026-10-23 21:46:22
severity: high
environment: docker
owner: 产品团队
related_requirement: null
related_bug:
- BUG-0060-direct-command-completion-proof-drift
- BUG-0061-cross-entry-continuation-guard-convergence
- BUG-0062-archive-requirement-scope-conflict
source_sprint: sprint-012
discovered_at: '2026-10-22 08:58:14'
related_change: null
root_cause_status: confirmed
---

# 同条文兼容追加被归档后继冲突门禁拒绝

## 问题概述

sprint-012 的 SPRINT 会话跳转与命令预填正常，但最终归档准入把 BUG-0061 对 BUG-0060 三项条文的兼容追加判为冲突。已经归档的旧交付无法取得当前深层就绪结论，进而阻断 Sprint 关闭。本缺陷处理证明机制的兼容后继识别，不回退既有安全边界。

## 环境与前置条件

- 环境：本地 Docker 产品与同仓库 CLI；现场来源 sprint-012，不代表本 BUG 已正式纳入该迭代。
- fix-direct-command-completion-proof、fix-cross-entry-continuation-guard 均已归档，后继增量已合并至生效规格。
- 当前迭代四项 Change 已归档、62/62 任务完成。其他最终门禁仍独立生效。

## 复现步骤

1. 读取 sprint-012 的 sprint.yaml，确认包含上述两项 Change。
2. 运行 `python scripts/validate-sprint-archive-readiness.py --sprint sprint-012 --json`。
3. 查看 fix-direct-command-completion-proof 的 blocker 与 deep_blocked；错误码为 archive_requirement_conflict，关联后继为 fix-cross-entry-continuation-guard。
4. 对照两份归档增量规格和 `openspec/specs/governance-command-durable-recovery/spec.md`，确认三项原约束、原场景完整保留，只增加新场景。
5. 产品复现入口为需求中心 Sprint 归档图标 → Chat 命令预填 → 用户发送归档命令。既有浏览器观察显示同类 Change 门禁错误；本次生成未再次发送或执行归档。

## 期望与实际

| 项目 | 期望 | 实际 |
|---|---|---|
| 同条文兼容追加 | 完整、稳定且可验证的后继证据允许承接 | 标题交集直接判冲突 |
| 原交付保护 | 保留原约束、场景、历史证据及首次执行事实 | 原条文保留仍无法就绪 |
| 真实风险 | 破坏性修改、断链、篡改、身份歧义及并发变化拒绝 | 现有拒绝规则需继续保持 |
| 跨入口 | 产品、CLI、Sprint 预检与 Workflow Sync 使用一致证据结论 | 共享门禁一致拒绝当前合法追加现场 |

## 影响范围与严重等级

severity 为 high：阻断当前 Sprint 正常关闭，并影响有同条文兼容后继的已归档交付核验。当前已确认现场为 BUG-0060 → BUG-0061；未外推为所有归档对象受影响。没有数据丢失或全部产品不可用证据，因此不定为 critical/blocker。

## 已确认机制与证据

`src/backend/app/governance/archive_recovery.py` 后继链遍历计算 `scope & protected`；交集非空时直接记录冲突并跳过该边，最终抛出 archive_requirement_conflict。该分支未区分同条文的兼容追加和破坏性修改。

| 受影响条文 | 后继新增场景 | 对比结果 |
|---|---|---|
| 直接命令动作级交付契约 | 仅进度事件不能完成 | 原约束与场景完整保留 |
| 直接命令最终签认与版本围栏 | 后继完成与新执行竞争 | 原约束与场景完整保留 |
| 直接命令状态原因与跨入口验收 | 当前交付已推进而旧执行未完成 | 原约束与场景完整保留 |

证据来源：

- `openspec/archive/2026-10-21-fix-direct-command-completion-proof/specs/governance-command-durable-recovery/spec.md`。
- `openspec/archive/2026-10-21-fix-cross-entry-continuation-guard/specs/governance-command-durable-recovery/spec.md`；三项生效条文与该版本一致。
- 2026-10-22 本次只读预检重现 blocked，具体仍为上述三项条文冲突。
- BUG-0061 归档 verification.md 记录 14/14 验收及产品实际归档、CLI 对照；属于既有交付证据，本轮未重跑运行回归。
- [采集记录](capture.md) 保存同会话产品观察及判重事实。

confirmed 指阻断代码路径、复现结果和当前条文追加事实。文本保留只是兼容证明的必要条件，不能自动证明新增场景无语义矛盾；后续设计需明确可机械验证的安全范围及不确定时拒绝策略。

## 修复目标与安全边界

1. 对有完整后继链、唯一归档身份、有效输入和验收证据的兼容追加给出可追溯判断。
2. 保留原约束及场景，校验新增场景；不以字符串包含、同标题或模型主观判断独立放行。
3. 改写、删除、重命名、重复标题、未知语法、矛盾追加、断链、篡改和并发输入变化继续阻断。
4. 不编辑原 manifest、journal、历史哈希或首次执行事实来消除冲突；不重放模型、不重复合并规格。
5. 统一产品、CLI、Sprint 预检及 Workflow Sync，失败时返回具体条文与原因。

## 关联与范围外

关联 BUG-0060-direct-command-completion-proof-drift、BUG-0061-cross-entry-continuation-guard-convergence、BUG-0062-archive-requirement-scope-conflict。BUG-0062 仅支持同模块不同条文承接，明确将同条文修改保持阻断；本次独立扩展兼容追加识别，不重开历史已完成交付。

人工 sign-off、五处旧 active Change 路径、最终权限及其他 Sprint 关闭检查不纳入本 BUG 的自动修复结果。当前无安全绕过方案，不建议 force 或重写历史证明。

## 数据采集与链路观测

product_data_collection_observability: applicable。
affected_layers: agent_workflow_governance、归档后继证明、API 准入诊断、Sprint 预检、Workflow Sync。
validation: 当前完成只读 CLI 复现及条文证据核对；后续按兼容正例、破坏性负例、证据完整性、并发及四入口一致性验证。
N/A：本轮仅生成缺陷文档，无 API、DB、UI、部署、安全策略或客户端生成变更；不新增事件、不持久化 Prompt、凭证或本机路径。实施阶段如改变响应或存储契约，另行同步对应文档、测试和客户端。

## 产品层面防复发要求

用户在 bug-complete 明确要求避免后续再次出现。本修复需提供通用、版本化兼容追加证明，覆盖多跳及跨 Sprint，不能按当前三个标题或对象 ID 特判。后继验收/归档预检提前检查受保护历史影响，产品提供按项可操作诊断且保留草稿；四入口统一判定，安全负例和部署验证纳入持续防回归门禁。具体可验收要求见 [验收标准](acceptance.md) AC-001—018；保留不确定时拒绝与最终签署门禁。

## 当前状态与下一步

已正式纳入 sprint-012，状态 in_sprint，关联 fix-compatible-requirement-successor 已 proposed，未实施修复。下一步 `/opsx-apply BUG-0063-compatible-requirement-successor-blocked`。

## 兼容证明门禁返修说明

取消后继写入前兼容证明硬性限制：产品预检、CLI 和归档执行不再要求独立兼容或规则替代证明；已完成后继仍核验正常验收、唯一身份、连续归档哈希链、交付增量、最终规格效果和并发变化。历史 journal、manifest 与证明保留，不自动归档或代替独立签署。

当前返修完整验收待执行，历史18/18不替代本轮结果。
