---
title: 验收稳定批次与增量复验治理记录
created_at: 2026-10-20 18:09:32
updated_at: 2026-10-20 18:09:32
---

# 验收稳定批次与增量复验治理记录

## 迭代目标
减少跨入口遗漏、输入变动导致的重复验收和无变化进度消息，保持现有门禁。

## 变更摘要与影响范围
中央标准新增完整入口矩阵、稳定批次、受影响依赖闭包和里程碑反馈。五个执行技能及入口短引用；静态校验防止关键条款和引用丢失。未修改验收器缓存算法，不宣称跨轮命令缓存或实际提速。

## 更新文件
- docs/standards/opsx-acceptance.md
- AGENTS.md、rules/agent-context-budget.md、docs/08-command-execution-order.md
- .agents/skills/ 下 opsx-apply、openspec-apply-change、opsx-modify、opsx-accept、opsx-archive 的 SKILL.md
- scripts/validate-agent-context-budget.py、scripts/test-stable-validation-contract.py
- openspec/changes/optimize-acceptance-stable-validation/、sprint-011 范围及派生材料
- 本日志与 docs/spec-logs/CHANGELOG.md

## 验证结果
上下文契约、当前 Change 中文与结构、中文标题校验通过；合成正反例 21 项通过（1 正例、11 条款删除、8 引用删除、1 事实源缺失）。目录校验通过，保留既有 SQLite legacy 路径 warning，不删除运行数据。
测试命令：python scripts/test-stable-validation-contract.py；python scripts/validate-agent-context-budget.py。
静态测试不等于真实 Agent 行为验收，不报告实际耗时改善比例。

## 产品与部署影响
API、DB、Web、客户端、管理端、Orval、Docker Compose 均 N/A：仅治理规范及静态校验，不修改业务实现或部署。本轮不需要产品模型调用、视觉采集或真实归档。
product_data_collection_observability: N/A；affected_layers: []；不新增采集或链路事件；validation：变更范围检查。

## 后续建议
后续实际任务按新契约记录执行次数与实测耗时，再评估跨轮缓存或构建缓存的独立实现；不自动新增 Issue，不放宽当前成功证据复用条件。

## 工作流收尾

已纳入 sprint-011 并完成 opsx.apply，同步无错误，Sprint 范围校验通过。用量自动发现不可归因（unavailable），不为用量重复验收。未归档、未提交。
