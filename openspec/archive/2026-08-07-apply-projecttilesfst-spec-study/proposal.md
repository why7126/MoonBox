---
purpose: OpenSpec Change Proposal
content: 应用 ProjectTilesFST spec-study 学习候选 A-D 到 MoonBox 治理资产
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# apply-projecttilesfst-spec-study

## 背景

MoonBox 已从 ProjectTilesFST 学习到 `spec-opt`、`spec-study`、Sprint 自动编号、学习报告目录和上下文预算治理的配套实践。用户已确认应用候选 A、B、C、D。

## 目标

- 补齐 `/sprint-propose` 的 Sprint ID 自动编号规则。
- 将 `/spec-study` 与 Sprint 自动编号沉淀为 OpenSpec delta spec。
- 增强 `rules/agent-context-budget.md` 的已读摘要复用细则。
- 扩充 `docs/spec-logs/README.md` 的目录边界。

## 范围

本 Change 只修改治理资产、规则文档、Agent 技能和 OpenSpec 变更文档，不修改 `src/` 业务运行时代码。

## 非目标

- 不同步 ProjectTilesFST 的瓷砖业务、小程序发布、TileSpec、媒体处理或业务 smoke 脚本。
- 不恢复 `.cursor/`、`.codex/`、`.kiro/`、`.opencode/`、`.claude/` 等多 Agent 目录。
- 不直接修改 `openspec/specs/` 正式规格；正式规格仅通过归档合并生效。
