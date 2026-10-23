---
bug_id: BUG-0063-compatible-requirement-successor-blocked
title: 同条文兼容追加被归档后继冲突门禁拒绝缺陷记录
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
---

# 同条文兼容追加被归档后继冲突门禁拒绝缺陷记录

## 现象与影响

sprint-012 的归档命令已能进入 Chat 并预填，但发送时提示“Change 1 项、验收 sign-off 1 项未闭环”。本缺陷仅记录其中的归档后继条文判定：BUG-0061 对 BUG-0060 三项条文保留原约束及原场景并追加场景，却被 archive_requirement_conflict 拒绝。影响深层归档就绪、产品发送准入及 Sprint 关闭，初定 high；不表示所有运行行为已证明无回归。

## 复现步骤

1. 使用包含已归档 fix-direct-command-completion-proof 与 fix-cross-entry-continuation-guard 的 sprint-012。
2. 只读运行 `python scripts/validate-sprint-archive-readiness.py --sprint sprint-012 --json`。
3. 观察前者 deep_blocked 为 true，错误列出后者在 governance-command-durable-recovery 下的三项同标题条文。
4. 对照两份归档增量规格与生效规格：直接命令动作级交付契约、直接命令最终签认与版本围栏、直接命令状态原因与跨入口验收。

## 期望与实际

期望：在完整后继链、唯一身份、交付及附件证据有效、当前输入稳定的前提下，支持可验证的兼容追加。破坏性修改、删除/重命名、证据断链、未知语法、篡改及并发变化继续阻断；不能只凭文本包含或同标题直接放行。

实际：`src/backend/app/governance/archive_recovery.py` 的后继链检查以 `scope & protected` 交集直接拒绝，不区分兼容追加与破坏性变更。

## 已有证据与判断边界

- 同会话浏览器只读观察：Chat 主对象为 sprint-012，输入框保留归档命令并显示上述最终门禁错误；未为探索执行归档。
- 2026-10-22 只读 CLI 预检：4/4 Change 已归档、62/62 任务完成；仅 BUG-0060 对应 Change 的深层证明报三项条文冲突。
- 两份 `openspec/archive/2026-10-21-fix-direct-command-completion-proof/specs/governance-command-durable-recovery/spec.md` 与 `openspec/archive/2026-10-21-fix-cross-entry-continuation-guard/specs/governance-command-durable-recovery/spec.md` 程序化比较：三项原文本完整保留；生效规格三项与后继版本一致。
- BUG-0061 的 verification.md 记录 14/14 验收及产品实际归档、CLI 对照；这是既有证据，不声称本次重新测试。
- 已确认阻断机制和条文兼容追加事实；修复后的完整安全性与运行回归待正式验证。

## 判重与关联

BUG-0060、BUG-0061、BUG-0062 均已 done/archive。BUG-0062 明确限定为同模块不同条文可承接，同条文修改仍拒绝。本次用户在只读对比后明确授权创建关联缺陷，独立处理同条文兼容追加，保留三项历史交付。单条记录：产品及 CLI 阻断属于同一证明机制。

## 建议验收范围

- 当前三项仅追加场景的现场在完整有效证据下通过，历史 manifest、journal、哈希及首次执行事实保持不变。
- 保留原约束和场景只是必要条件；新增场景矛盾或无法可靠判定时不得自动放行。
- 改写原约束、删除/重命名、重复标题、断链、身份歧义、证据篡改及并发变化继续拒绝。
- 产品、CLI、Sprint 预检与 Workflow Sync 判定一致，拒绝时给出具体原因。
- 不重复合并规格或重放模型；不降低人工 sign-off、权限及其他关闭门禁。

## 范围外事项

Sprint 人工签署缺失与五处旧 active Change 引用是独立关闭条件，不因本 BUG 修复自动完成。本次未纳入 sprint-012 正式范围，source_sprint 仅表示现场来源。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档后继证明、Sprint 预检、API 准入及诊断；validation: 当前只读条文比较和 CLI 复现，修复后验证正负例、并发围栏与四入口一致性。N/A：本次 capture 不改变 API、DB、UI、部署、安全或客户端生成；不新增事件采集，不持久化 Prompt、凭证或本机路径。实施影响在后续设计阶段复核。

## 附件

用户截图的错误文字已脱敏摘录；未复制本机临时图片或运行日志。可复核事实源见上述仓库路径。
