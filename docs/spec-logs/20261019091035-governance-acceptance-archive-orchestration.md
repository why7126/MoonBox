---
title: 自动验收与归档编排治理优化
created_at: 2026-10-19 09:10:35
updated_at: 2026-10-19 09:12:05
---

# 自动验收与归档编排治理优化

## 迭代目标

将近期五条链路复盘所得十项优化纳入 `optimize-acceptance-archive-orchestration` 与 sprint-010，分三批实施。保留真实性、同轮证据和正式归档授权门禁。

## 变更摘要与影响范围

第一批完成逐 AC 队列、依赖调度、局部阻塞、待采集状态、环境样本及浏览器能力契约。第二批完成输入章节与依赖指纹、历史计划兼容、命令去重、逐项原子检查点、计数与脱敏活动指标。第三批完成状态规则去歧义、临时副本归档预演和 wrapper 收尾去重。

## 更新文件

- scripts/opsx_acceptance.py：队列、检查点、指纹、去重、状态与指标。
- scripts/archive-recovery-guard.py：只读正式仓库的临时副本预演入口。
- scripts/benchmark-acceptance-orchestration.py：相同隔离场景对比已提交基线与当前实现。
- scripts/validate-agent-context-budget.py、tests/unit/test_acceptance_orchestration.py：契约反例与脚本回归。
- .agents/skills/opsx-accept/SKILL.md、.agents/skills/opsx-archive/SKILL.md、.agents/skills/workflow-sync/SKILL.md：连续执行、状态和收尾一致性。
- AGENTS.md、rules/agent-context-budget.md、rules/document-governance.md、docs/08-command-execution-order.md、docs/README.md、docs/standards/opsx-acceptance.md：统一事实源和执行入口。
- 当前 Change 产物、证据与 sprint-010 四件套。

## 验证结果

50项聚焦回归通过；上下文预算、OpenSpec 中文与结构、目录、标题、Sprint scope 和产品数据观测校验通过。当前治理验收7/7 passed，readiness ready，规格临时合并预演通过；正式归档未执行。

同组隔离场景中，局部缺证由 0 通过/3 阻塞变为 2 通过/1 阻塞。重复命令由 3 次变为 1 次，全部3项通过；计时仅记录夹具数据，不代表真实产品总耗时。原始聚合结果随当前 Change 保存在 evidence/comparison.json。

## 边界与后续建议

API/DB/Web/客户端/管理端/Orval/Docker Compose 均不变；权限不扩大；不改业务 src 或正式规格。product_data_collection_observability 为 applicable，affected_layers 为 agent_workflow，validation 覆盖脱敏聚合与同轮证据；不新增产品数据表和日志采集。

真实产品浏览器采集与 Agent 全链路行为未在本轮重新运行；本轮证明治理脚本、技能静态契约和合成场景。旧版 plan 指纹保持兼容，新计划显式启用 orchestration_version。目录仅存在原有 SQLite 迁移提示；测试存在既有依赖弃用提示。用户授权转存的同步冲突元数据保留原始字节，其他既有工作区变更未改。

后续可在实际未归档 REQ/BUG 中观察端到端采集行为与阶段耗时，不从合成结果承诺提速比例。正式归档仍需单独授权；未创建额外 follow-up Issue/Change。
