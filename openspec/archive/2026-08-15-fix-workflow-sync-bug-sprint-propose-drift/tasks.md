---
change_id: fix-workflow-sync-bug-sprint-propose-drift
status: applied
created_at: 2026-08-15 11:45:27
updated_at: 2026-08-15 12:00:52
---

# Tasks

- [x] 1. 扩展 `sprint.propose` 的 Issue 当前态看板刷新覆盖
  - [x] 1.1 在 `scripts/workflow_sync/engine.py` 中将 focused `sprint.propose` 纳入 `patch_issue_changelog_index` 调用条件
  - [x] 1.2 确认 `--bug` 与 `--req` 场景均能进入对应 CHANGELOG patch
- [x] 2. 扩展 registry 派生字段同步
  - [x] 2.1 让 registry patch 同步 `iteration`
  - [x] 2.2 让 registry patch 同步 `lifecycle_stage` 与真实阶段目录 `path`
  - [x] 2.3 让 bug/req opsx 回填 `related_change`
- [x] 3. 扩展 trace 派生字段同步
  - [x] 3.1 同步 frontmatter `iteration`
  - [x] 3.2 同步 fenced yaml `lifecycle.status`、`lifecycle.stage`、`lifecycle.iteration`
  - [x] 3.3 同步 `related_change` 与 `openspec_changes` 状态
- [x] 4. 增加回归验证
  - [x] 4.1 增加或更新 Workflow Sync focused 测试，覆盖 BUG `sprint.propose`
  - [x] 4.2 验证 `issues/bugs/CHANGELOG.md` 在 dry-run/detail 报告中出现
  - [x] 4.3 验证 trace、registry、CHANGELOG 与 Sprint scope 一致
- [x] 5. 文档与治理日志
  - [x] 5.1 按需同步 `rules/` 或 `.agents/skills/workflow-sync/SKILL.md`
  - [x] 5.2 若修改治理脚本，补充 `docs/spec-logs/YYYYMMDDhhmmss-governance-*.md` 与索引
- [x] 6. 最终验证
  - [x] 6.1 `python scripts/validate-root-cause-evidence.py --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift`
  - [x] 6.2 `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --dry-run --output detail`
  - [x] 6.3 `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift --sprint sprint-003 --check`
  - [x] 6.4 `python scripts/validate-directory-structure.py`
  - [x] 6.5 `python scripts/validate-openspec-language.py`
  - [x] 6.6 如修复有自动化测试，运行对应 focused 测试
  - [x] 6.7 评估是否需要沉淀 `docs/knowledge-base/incidents/`
