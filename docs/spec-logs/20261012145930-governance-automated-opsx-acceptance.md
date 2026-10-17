---
purpose: 自动验收治理迭代记录
created_at: 2026-10-12 14:59:30
updated_at: 2026-10-12 15:27:04
---

# 自动验收与证据归档治理迭代

## 目标与变更

将 apply 后的验收整理为独立阶段，自动运行逐 AC 检查、收集脱敏产品轮次证据、复用未过期结果，并在归档前检查就绪状态。动因是 BUG-0026 验收中多次环境中断、重复样本和手工证据整理造成的长耗时。

## 影响范围

- 新增 `/opsx-accept` 技能、`scripts/opsx_acceptance.py`、验收标准与聚焦测试。
- 现有 apply、modify、archive、Workflow Sync 衔接验收结果；有计划的 Change 使用新门禁，历史 Change 保持既有证据规则。
- Change 内保存计划与运行证据包；Issue 仅存结论与证据入口，Sprint 仅存聚合摘要。
- 已纳入 `sprint-008`。`sprint-009` 容量硬阻断，现有两条 active Sprint 不允许新建第三条。

主要更新文件：`.agents/skills/opsx-accept/SKILL.md`、`scripts/opsx_acceptance.py`、`scripts/workflow_sync/{constants,engine,issue_subdocuments,patch}.py`、`scripts/archive-change.sh`、`scripts/ai_usage.py`、`tests/unit/test_opsx_acceptance.py`、`docs/standards/opsx-acceptance.md`、`AGENTS.md`、`project.yaml`、`README.md`、`docs/08-command-execution-order.md`、相关 Skill 与目录/上下文/文档规则，以及本 Change 的提案、设计、规格、任务和追溯记录。

## 验证与边界

聚焦单测 27 passed；上下文预算、OpenSpec 中文和 strict、目录、Sprint scope、产品数据观测、交付证据门禁与 Workflow Sync 均通过。自动验收 3/3 passed、readiness ready；历史 BUG-0042 产品轮次只读适配器核对到 completed 与同轮命令序号 47/退出码 0。AI Usage 无可归因 token 事件，非阻断 warning。API、DB schema、Web、管理端、客户端生成、Orval、Docker Compose 和对象存储协议未改；产品 SQLite 只读查询轮次和命令事件，不写入产品库。已按观测标准声明 Agent Workflow 与 Chat event 适用，原始消息、prompt、事件 payload 不入仓。

## 后续建议

在真实新 Change 上观察预检耗时、AC 复用率和产品轮次取证完整度；MySQL 产品环境需等价授权只读适配器，不能以 SQLite 实现冒称覆盖。
