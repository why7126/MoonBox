---
purpose: 自动验收证据与增量清单强化治理记录
created_at: 2026-10-12 19:53:00
updated_at: 2026-10-12 19:53:00
---

# 自动验收证据与增量清单强化

## 迭代目标与变更摘要

依据 BUG-0035 自动验收复盘，强化负向门禁计划预检、单项诊断与整体就绪隔离、逐 AC 证据及样本矩阵预检、报告结构校验和原子发布。完整运行可复用仍有效的历史单项证据；无效或失败的较新观察不由更旧通过记录覆盖。

## 影响范围与更新文件

更新 `scripts/opsx_acceptance.py`、`tests/unit/test_opsx_acceptance.py`、`docs/standards/opsx-acceptance.md`、`.agents/skills/opsx-accept/SKILL.md`、本索引及 `harden-automated-acceptance-evidence` Change，并纳入 `sprint-009`。

API、DB schema、Web、客户端生成、管理端、Orval、Docker Compose、部署及安全策略无变更。Agent Workflow 验收证据清单只保存脱敏状态与标记，不采集新的产品事件或原始消息。`product_data_collection_observability: applicable`；`affected_layers: [agent_workflow, chat_events]`；其他数据层 N/A，因为既有只读取证协议未变。

## 验证结果

聚焦测试 15 项通过；OpenSpec、语言、目录、上下文预算、Sprint scope 和 Workflow Sync 结果见 Change trace。验收清单的诊断隔离、负向门禁计划和报告拒绝发布均有聚焦回归。

## 后续建议

在下一个真实 Change 上观察诊断清单的复用率及报告预检失败率。
