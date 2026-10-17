---
title: 自动验收预检与证据覆盖治理迭代记录
created_at: 2026-10-12 23:09:23
updated_at: 2026-10-12 23:09:23
---

# 自动验收预检与证据覆盖治理迭代记录

## 迭代目标

依据 BUG-0029 自动验收复盘，区分环境或证据阻塞与功能失败，并使逐 AC 证据及视觉覆盖可直接审阅。

## 变更摘要

- 验收器在命令执行前核对环境、授权产品数据源、证据文件和视觉矩阵；缺口生成阻塞诊断。
- 视觉计划显式映射阶段×视口组合及证据文件，完整运行和就绪检查核对覆盖与哈希。
- 报告逐 AC 列出检查来源、证据类型、入口和缺口；标准、技能及入口规则同步。

## 影响范围与更新文件

治理脚本 `scripts/opsx_acceptance.py`、单测 `tests/unit/test_opsx_acceptance.py`、标准 `docs/standards/opsx-acceptance.md`、技能 `.agents/skills/opsx-accept/SKILL.md`、`AGENTS.md`、`rules/agent-context-budget.md`、`docs/README.md`、OpenSpec Change 与 sprint-009 规划。

API、DB、Web 业务实现、客户端、管理端、Orval、Docker Compose 均无运行态变更；产品数据采集与链路观测不适用，因为本轮仅处理治理证据元数据。

## 验证结果

定向测试 18 项通过；OpenSpec、当前 Change 中文优先、文档标题、目录结构、上下文预算校验通过。视觉截图内容仍需人工目视签认，文件和矩阵校验不替代产品观察。

## 后续建议

新建视觉验收计划时填写完整矩阵与浏览器预检；既有未归档视觉计划在下一次验收前补齐映射。保留 sprint-009 原有容量预警，不在本轮调整容量。
