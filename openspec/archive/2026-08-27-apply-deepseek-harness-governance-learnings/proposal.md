---
change_id: apply-deepseek-harness-governance-learnings
type: update
status: proposed
created_at: 2026-08-19 12:10:48
updated_at: 2026-08-19 12:10:48
---

# 应用 deepseek-harness 治理学习成果

## 背景

`/spec-study` 已完成对 deepseek-harness 的只读学习。该仓库在文档层级、事实唯一归属、脚本化治理门禁、Issue/PR 文档质量和最小相关验证方面有可迁移价值。

MoonBox 已有 OpenSpec、REQ/BUG、Sprint、Workflow Sync 和中文优先治理体系。本变更将学习成果转写为 MoonBox 规则，不照搬外部目录、GitHub Project 自动化或双语文档三件套。

## 目标

- 补强长期文档的层级归属规则，要求同一事实只有一个长期事实源。
- 建立治理校验矩阵，明确规则、文档、脚本、Skill、OpenSpec 和 Sprint 变更的验证入口。
- 强化 REQ/BUG 与 Change 文档质量规则，避免状态、验收、负责人、证据和 Sprint/Change 追溯漂移。
- 补充最小相关验证策略，要求按影响面选择能证明风险的最小验证组合。
- 生成一份 `study` 学习报告，并在 spec-logs 索引中登记。

## 非目标

- 不修改业务 `src/` 代码、API、数据库 schema、Web、管理后台或客户端运行时实现。
- 不恢复 `.claude/`、`.codex/`、`.cursor/`、`.kiro/`、`.opencode/` 等目录。
- 不引入 deepseek-harness 的双语文档配对机制、GitHub Project 状态机或 TypeScript/Cordis 专项校验。
- 不修改 `openspec/specs/` 正式规格。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance: true
```
