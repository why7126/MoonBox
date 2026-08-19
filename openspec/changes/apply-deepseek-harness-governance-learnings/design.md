---
change_id: apply-deepseek-harness-governance-learnings
status: proposed
created_at: 2026-08-19 12:10:48
updated_at: 2026-08-19 12:10:48
---

# 设计说明

## 学习转写策略

deepseek-harness 的治理优势来自三类机制：长期规则分层、脚本化校验和按影响面选验证。MoonBox 的治理事实源不同，因此本变更采用转写而非迁移：

- 文档层级落在 `rules/document-governance.md`，约束 `docs/`、`issues/`、`iterations/`、`openspec/` 的事实归属。
- 校验矩阵落在 `docs/08-command-execution-order.md`，作为命令执行和收尾检查的速查入口。
- REQ/BUG 文档质量落在 `rules/requirement-management.md` 与 `rules/bug-management.md`，继续以 `trace.md`、registry、CHANGELOG、Sprint 四件套和 Change 为事实源。
- 最小相关验证落在 `rules/testing.md`，指导命令按影响面选择验证，并说明未覆盖风险。

## 兼容性

本变更不改变业务状态机和 Workflow Sync 数据结构。`/spec-study` 产生的治理资产应用结果使用一份 `study` 报告承载，不再额外生成重复治理日志；`docs/spec-logs/CHANGELOG.md` 作为索引登记该报告。

## 风险

- 若规则只写原则、不列出验证入口，后续命令可能仍靠口头判断。通过校验矩阵降低该风险。
- 若 Issue/Change 质量规则与 Workflow Sync 自动派生范围混淆，可能导致手工编辑派生块。规则明确不得手工编辑 Workflow Sync marker 块。
- 当前工作区已有大量既有改动，本变更必须通过聚焦 diff 复核避免触碰 `src/`。
