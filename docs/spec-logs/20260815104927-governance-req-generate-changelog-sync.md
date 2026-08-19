---
purpose: req.generate CHANGELOG 派生刷新覆盖治理日志
content: 记录 Workflow Sync 对 req.generate 刷新 issues/requirements/CHANGELOG.md 当前态行的治理优化
created_at: 2026-08-15 10:49:27
updated_at: 2026-08-15 10:49:27
owner: MoonBox 产品团队
---

# req.generate CHANGELOG 派生刷新覆盖治理日志

## 迭代目标

优化 `/req-generate` 完成后的派生刷新覆盖，确保 `python scripts/sync-workflow-status.py --event req.generate --req <REQ-full-id> --sprint auto` 能刷新 `issues/requirements/CHANGELOG.md` 对应 REQ 当前态行。

## 变更摘要

- 在 Workflow Sync patch 层新增 Issue 当前态看板行生成与替换函数。
- 在 req/bug 聚焦事件和 opsx 关联 Issue 事件中调用当前态看板 patch。
- 更新 `req-generate` Skill，要求报告覆盖 `issues/requirements/CHANGELOG.md`。
- 更新 `rules/requirement-management.md`，明确 `req.generate` 的 CHANGELOG 派生刷新门禁。

## 影响范围

- `scripts/workflow_sync/patch.py`
- `scripts/workflow_sync/engine.py`
- `.agents/skills/req-generate/SKILL.md`
- `rules/requirement-management.md`
- `openspec/changes/optimize-req-generate-changelog-sync/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/CHANGELOG.md`

## 更新文件

- `scripts/workflow_sync/patch.py`
- `scripts/workflow_sync/engine.py`
- `.agents/skills/req-generate/SKILL.md`
- `rules/requirement-management.md`
- `openspec/changes/optimize-req-generate-changelog-sync/{proposal,design,tasks,trace,acceptance}.md`
- `openspec/changes/optimize-req-generate-changelog-sync/specs/agent-workflow-tooling/spec.md`
- `docs/spec-logs/20260815104927-governance-req-generate-changelog-sync.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python scripts/sync-workflow-status.py --event req.generate --req REQ-0019-space-creation-join-application-flow --sprint auto --dry-run --output detail`：通过，报告将 `issues/requirements/CHANGELOG.md` 列为 Updated。
- `python -m py_compile scripts/workflow_sync/patch.py scripts/workflow_sync/engine.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-req-generate-changelog-sync`：通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item optimize-req-generate-changelog-sync`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-req-generate-changelog-sync --sprint auto`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-req-generate-changelog-sync --sprint sprint-003 --json`：通过。
- `git diff --check`：通过。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

无。仅修改治理脚本、规则、Skill、OpenSpec 文档和治理日志。

## 后续建议

无。
