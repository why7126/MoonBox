---
created_at: 2026-08-09 08:27:52
updated_at: 2026-08-09 08:27:52
---

# 优化 spec-study 日志优先学习顺序

## 背景

`/spec-study` 当前要求横向学习项目入口、规则、文档、Agent 目录、脚本和部署资产，但没有明确说明当学习对象存在 `docs/spec-logs/CHANGELOG.md` 时应如何利用治理日志索引。

对于已经有规范迭代日志的项目，直接从代码或目录结构开始学习容易消耗较多上下文，也可能先看到实现细节而遗漏治理变更的设计意图。`docs/spec-logs/CHANGELOG.md` 和单次 `study` / `governance` 日志更适合作为治理演进入口。

## 变更目标

- 明确 `/spec-study` 在学习对象存在 `docs/spec-logs/CHANGELOG.md` 时，优先采用“日志索引 -> 单次日志 -> 治理资产 -> 代码/脚本补证”的学习顺序。
- 保留 Learning Matrix 的横向校验要求，避免只读日志导致事实过期或漏检。
- 同步上下文预算规则和 spec-log 变更历史，形成可复用的治理学习方法。

## 影响范围

- 影响 `.agents/skills/spec-study/SKILL.md`。
- 影响 `rules/agent-context-budget.md`。
- 影响 `docs/spec-logs/README.md`、`docs/spec-logs/CHANGELOG.md` 和本次治理日志。
- 不影响 `src/` 业务代码、API、数据库、Web、客户端、管理端、Orval 或 Docker Compose。
