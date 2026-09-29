---
created_at: 2026-09-15 08:47:46
updated_at: 2026-09-15 09:01:13
---

# 提案：优化 opsx-modify 验收返修台账结构

## 背景

当前 `/opsx-modify` 已要求在 `tasks.md` 增加 `## 验收返修记录`，近期多个 Change 也按此落地。该做法便于归档前快速扫到返修事实，但会让 `tasks.md` 从任务清单扩展成完整执行台账，和原有 Change 文档职责不完全一致。

## 变更内容

- 将完整验收返修台账主位置调整为 `openspec/changes/<change-id>/acceptance-fixes.md`。
- `tasks.md` 只保留返修任务勾选、简短摘要和台账链接。
- `trace.md` 保留返修摘要、证据入口和验证结果，不复制完整台账。
- `/opsx-archive` 归档复核读取 `acceptance-fixes.md`，确保返修台账不会在归档前丢失。
- `rules/document-governance.md` 固化 Change 文档职责分层。

## 影响范围

- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/spec-logs/`
- 本 Change 文档与 `sprint-007` scope

本 Change 不修改业务 `src/`、API、DB、Web 实现、OpenAPI、Orval 生成物、Docker Compose 或部署配置。

## 验收标准

- `/opsx-modify` 文档更新规则明确区分 `tasks.md`、`acceptance-fixes.md`、`trace.md` 和 Issue/Sprint 投影。
- `/opsx-archive` 归档复核明确读取返修台账并阻断缺失或 stale 证据。
- `rules/document-governance.md` 说明 `acceptance-fixes.md` 的职责和归档同步边界。
- 治理日志写入 `docs/spec-logs/` 并更新索引。
- 相关治理校验和 OpenSpec 校验通过，或在输出中说明既有非本次阻塞。
