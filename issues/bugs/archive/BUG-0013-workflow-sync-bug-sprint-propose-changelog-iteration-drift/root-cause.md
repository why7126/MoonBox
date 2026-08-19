---
bug_id: BUG-0013-workflow-sync-bug-sprint-propose-changelog-iteration-drift
root_cause_status: confirmed
created_at: 2026-08-15 11:31:53
updated_at: 2026-08-15 11:31:53
owner:
---

# 根因分析

## 根因状态

status: confirmed

## 现象

`sprint.propose --bug` 或等价 Workflow Sync 链路无法完整覆盖 BUG 当前态看板和 iteration 派生刷新。dry-run 报告中没有 `issues/bugs/CHANGELOG.md`，且代码路径显示 registry 与 trace 同步只覆盖部分字段。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | `python scripts/sync-workflow-status.py --event sprint.propose --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift --sprint sprint-003 --dry-run --output detail` | 报告覆盖 Sprint 文档、BUG trace、registry 和部分 REQ trace，但没有出现 `issues/bugs/CHANGELOG.md` | 证明 `sprint.propose --bug` 聚焦事件未调用 BUG 当前态看板刷新 |
| E2 | code_path | `scripts/workflow_sync/engine.py` | `patch_issue_changelog_index` 仅在 `req.*`、`bug.*`、`opsx.apply/modify/archive` 条件下调用，未包含 `sprint.propose` | 解释 E1 中 CHANGELOG 缺失的直接代码原因 |
| E3 | code_path | `scripts/workflow_sync/patch.py` `patch_registry_entry` | registry patch 只替换 `status` 字段，不更新 `iteration`、`lifecycle_stage` 或 `path` | 解释 BUG 纳入 Sprint 后 registry iteration / stage 派生刷新不完整 |
| E4 | code_path | `scripts/workflow_sync/patch.py` `patch_issue_trace` | trace patch 同步 frontmatter `status` 和 yaml block `status`，未同步 frontmatter / yaml lifecycle 的 `iteration` 或 stage | 解释 BUG 纳入 Sprint 后 trace iteration / lifecycle 派生刷新不完整 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| `issues/bugs/CHANGELOG.md` 缺失导致无法更新 | 当前仓库存在 `issues/bugs/CHANGELOG.md`，且 `bug.capture` / `bug.generate` 已能刷新 BUG-0013 当前态行 |
| Workflow Sync 完全不处理 BUG | dry-run 报告显示 BUG trace 和 registry 被纳入检查，问题集中在 `sprint.propose` 事件覆盖和字段覆盖不完整 |
| 只是 BUG-0012 单条历史数据异常 | 代码条件缺少 `sprint.propose`，registry/trace patch 字段覆盖不足，是通用路径问题 |

## 已确认根因

Workflow Sync 的 BUG Sprint 纳入派生刷新存在两类实现缺口：

1. `patch_issue_changelog_index` 的调用条件未覆盖 `sprint.propose`，导致 BUG 纳入 Sprint 时不会刷新 `issues/bugs/CHANGELOG.md` 当前态行。
2. `patch_registry_entry` 与 `patch_issue_trace` 只同步 status / OpenSpec change 状态，不同步 Sprint 纳入所需的 `iteration`、`lifecycle_stage`、`path` 或 lifecycle stage 字段，导致 BUG sprint.propose 后 iteration / stage 派生刷新不完整。

## 修复方向

- 在 `sprint.propose` 且聚焦 `--bug` / `--req` 时调用当前态看板 patch。
- 扩展 registry patch，使其能按聚焦 Issue 同步 `status`、`iteration`、`lifecycle_stage` 和阶段目录 `path`。
- 扩展 trace patch，使其在 Sprint 纳入事件中同步 frontmatter 与 yaml lifecycle 的 `iteration` / stage。
- 增加 focused dry-run 或单元测试，断言 `sprint.propose --bug` 报告覆盖 `issues/bugs/CHANGELOG.md`、trace 和 registry。

## 验证闭环

- 修复前证据：E1 dry-run 报告没有 `issues/bugs/CHANGELOG.md`。
- 修复后应运行：

```bash
python scripts/sync-workflow-status.py --event sprint.propose --bug <BUG-full-id> --sprint <sprint-id> --dry-run --output detail
```

并确认报告中包含：

- `issues/bugs/CHANGELOG.md`
- 目标 BUG `trace.md`
- `issues/bugs/_registry.yaml`
- Sprint 四件套相关派生文件
