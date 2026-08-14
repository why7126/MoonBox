---
purpose: 治理迭代日志
content: 优化 spec-study 日志优先学习顺序
created_at: 2026-08-09 08:27:52
updated_at: 2026-08-09 08:33:08
owner: MoonBox 产品团队
---

# 优化 spec-study 日志优先学习顺序

## 迭代目标

当 `/spec-study` 学习对象存在 `docs/spec-logs/CHANGELOG.md` 时，优先从日志索引理解治理演进，再读取相关单次日志，随后横向校验真实治理资产，最后按需读取代码、脚本或配置片段补证。

## 变更摘要

- 更新 `/spec-study` Phase 1 学习顺序，固化“日志索引 -> 单次日志 -> 真实治理资产 -> 必要补证”的方法。
- 更新上下文预算规则，明确日志只作为入口地图和历史背景，不能替代当前资产事实源。
- 更新 `docs/spec-logs/README.md` 和 `CHANGELOG.md`，说明 `CHANGELOG.md` 在跨项目学习中的入口价值。
- 创建 active OpenSpec Change `optimize-spec-study-log-first-learning` 并纳入 `sprint-002`。

## 影响范围

- 影响治理 Skill：`.agents/skills/spec-study/SKILL.md`。
- 影响规则：`rules/agent-context-budget.md`。
- 影响治理日志：`docs/spec-logs/README.md`、`docs/spec-logs/CHANGELOG.md`、本文件。
- 影响 OpenSpec：`openspec/changes/optimize-spec-study-log-first-learning/`。
- 不影响 `src/` 业务代码。

## 更新文件

- `.agents/skills/spec-study/SKILL.md`
- `rules/agent-context-budget.md`
- `docs/spec-logs/README.md`
- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260809082752-governance-spec-study-log-first-learning.md`
- `openspec/changes/optimize-spec-study-log-first-learning/`
- `iterations/change/sprint-002/`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-sprint-scope.py sprint-002 --item optimize-spec-study-log-first-learning`：通过。
- `openspec validate optimize-spec-study-log-first-learning`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-spec-study-log-first-learning --sprint auto`：通过，更新 2 处，错误 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-spec-study-log-first-learning --sprint sprint-002 --json`：通过，`usage_mode: actual`，warning 0。

## 影响矩阵

| 项 | 影响 |
|---|---|
| API | 不适用 |
| DB | 不适用 |
| Web | 不适用 |
| 客户端 | 不适用 |
| 管理端 | 不适用 |
| Orval | 不适用 |
| Docker Compose | 不适用 |

## 后续建议

后续执行真实 `/spec-study` 跨项目学习时，观察日志优先是否降低上下文消耗，并在候选学习内容中显式标注日志与真实资产是否存在漂移。
