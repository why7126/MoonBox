## 背景

`req-generate` Skill 已要求成功生成 `requirement.md` 后更新 `issues/requirements/CHANGELOG.md` 当前态行，但 Workflow Sync 的实现证据显示当前同步链路只 patch `trace.md`、Issue 子文档和 `_registry.yaml`，没有稳定 patch 当前态看板索引。

这会导致 `/req-generate` 完成后，REQ 真实文档进入 `draft`，但目录级 `CHANGELOG.md` 可能仍停留在 capture 阶段或旧状态。

## 变更内容

- 在 Workflow Sync patch 层新增 Issue 当前态看板行生成与替换能力。
- 在 `req.generate --req <REQ-full-id>` 聚焦事件中刷新 `issues/requirements/CHANGELOG.md` 对应 REQ 行。
- 同步支持 BUG 聚焦事件和 opsx 关联 Issue 事件，避免后续同类派生刷新缺口。
- 更新 `req-generate` Skill 与 `rules/requirement-management.md`，明确报告必须覆盖 `issues/requirements/CHANGELOG.md`。
- 不修改业务 `src/`、API、DB、Web UI、客户端或部署拓扑。

## 影响范围

- `scripts/workflow_sync/patch.py`
- `scripts/workflow_sync/engine.py`
- `.agents/skills/req-generate/SKILL.md`
- `rules/requirement-management.md`
- `openspec/changes/optimize-req-generate-changelog-sync/`
- `docs/spec-logs/`

## 回滚计划

如 CHANGELOG 派生行格式与人工维护规则出现冲突：

1. 回退 `patch_issue_changelog_index` 调用。
2. 保留 `req-generate` Skill 对 Workflow Sync 的要求。
3. 重新运行 `req.generate` dry-run、上下文预算、OpenSpec 语言和目录结构校验。
