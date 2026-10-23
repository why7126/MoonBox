---
title: 治理执行量化与授权优化闭环
created_at: 2026-10-20 18:32:12
updated_at: 2026-10-20 18:35:45
---

# 治理执行量化与授权优化闭环

## 迭代目标
将命令执行复盘扩展为可测量、分级授权、可验证效果的治理闭环。关联 Change `optimize-governance-feedback-loop`、Sprint `sprint-011`，来源为用户明确治理授权。

## 变更摘要与更新文件
- `scripts/governance_feedback.py`：运行生命周期、暂态用量导入、候选去重/冷却、预算和递归门禁、验证封存、净收益评估及保留清理。
- `scripts/ai_usage.py` 与 `scripts/extract-ai-usage.py`：脱敏用量接入，采集失败和缺少PyYAML的非阻断降级。
- `rules/governance-feedback-policy.json`、`docs/standards/governance-feedback-loop.md`：授权范围、量化口径与执行细则。
- AGENTS、上下文预算、目录规则、Workflow Sync/spec-opt技能、文档和命令索引：中央契约短引用。
- `scripts/validate-agent-context-budget.py`、`scripts/benchmark-governance-feedback.py` 与聚焦单测：契约门禁、采集性能实测和正反例。

## 影响范围
product_data_collection_observability: applicable

affected_layers: [agent_workflow_governance]

API、DB、Web、管理端、客户端、Orval、Docker Compose、对象存储：N/A，仅治理工具与本地脱敏台账。无业务src实现、数据库迁移或客户端生成。授权不扩展产品权限和发布权限。

## 验证结果
42项聚焦回归、8/8自动验收、归档预演和最终readiness均通过；证据见当前Change `trace.md` 和 `evidence/acceptance/`。合成收益样本只验证计算口径，真实长期收益仍待同组后续调用；本轮Token不能完整归因时保留不可用。

## 问题证据与解决
上一轮默认Python缺少PyYAML导致Hook导入异常。本轮复用已有项目环境，并新增标准Hook缺依赖时紧凑降级；负向回归证明主命令不因可选采集器失败而失败。没有通过降低验收门禁处理问题。

## 后续建议
已授权范围内按中央闭环继续；收集真实完整样本，质量门禁不变，达到证据要求后判断净收益。没有创建额外业务Issue或自动归档。

## 跨项目落地提示
建立每次命令调用的脱敏量化台账，记录耗时、Token、版本、质量与优化自身成本；在明确治理授权、Change、Sprint和验证门禁内实施优化，以可比样本和净收益验证效果，保留未知值、防递归、去重和回退边界。

本轮量化：20次CLI实测start中位数140.708ms、finish/review中位数132.373ms；验收15.094秒；启用后实施验证区间797.930秒，启用前成本未知、Token不可归因。
