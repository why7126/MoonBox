---
purpose: OpenSpec Change Proposal
content: 新增 docs/spec-logs 变更历史文档
created_at: 2026-08-08 20:53:52
updated_at: 2026-08-08 20:53:52
owner: MoonBox 产品团队
---

# 新增 docs/spec-logs 变更历史文档

## 背景

`docs/spec-logs/` 已用于存放 `/spec-study` 学习报告和 `/spec-opt` 治理迭代日志，但目录内缺少一份面向长期追踪的变更历史文档。随着规范、脚本、命令和目录边界持续迭代，仅依赖零散日志文件不利于快速了解治理资产的演进脉络。

## 变更内容

- 在 `docs/spec-logs/` 新增 `CHANGELOG.md`，用于记录每一次规范、脚本、命令、目录边界和校验规则更新日志。
- 更新 `docs/spec-logs/README.md`，明确 `CHANGELOG.md` 是目录级变更历史入口。
- 补充 OpenSpec delta，固化 `/spec-opt` 治理历史索引要求。
- 写入本次 `/spec-opt` 治理迭代日志。

## 非目标

- 不修改业务代码。
- 不修改 API、数据库、Web、客户端、管理后台或 Docker Compose 行为。
- 不替代单次 `YYYYMMDDhhmmss-governance-xxx.md` 治理日志；`CHANGELOG.md` 只做聚合索引和摘要。

## 影响范围

- 影响 `docs/spec-logs/` 目录文档结构。
- 影响 `agent-workflow-tooling` 的治理日志输出规格。
- API、DB、Web、客户端、管理端、Orval、Docker Compose 均无业务实现影响。
