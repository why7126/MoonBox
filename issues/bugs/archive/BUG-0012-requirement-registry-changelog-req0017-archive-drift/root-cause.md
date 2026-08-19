---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
created_at: 2026-08-15 10:46:46
updated_at: 2026-08-15 10:56:39
classification: governance
---

# 根因分析

## 根因状态

status: confirmed

## 现象

- `REQ-0017-admin-space-management` 的真实目录已位于 `issues/requirements/archive/REQ-0017-admin-space-management/`。
- 单条 REQ `trace.md` 已显示 `status: done`、`lifecycle_stage: archive`，关联 Change `add-admin-space-management` 已 `archived`。
- `issues/requirements/_registry.yaml` 仍把 `REQ-0017-admin-space-management` 记录为 `lifecycle_stage: review`，路径仍指向 `issues/requirements/review/REQ-0017-admin-space-management/`。
- `issues/requirements/CHANGELOG.md` 仍把 `REQ-0017-admin-space-management` 展示为 `in_sprint` / `review`，下一步仍是 `/opsx-apply REQ-0017-admin-space-management`，事实源仍指向 `review/` 路径。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | data_sample | `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` | frontmatter 显示 `status: done`、`lifecycle_stage: archive`，`openspec_changes` 中 `add-admin-space-management` 状态为 `archived`。 | 单条 REQ 事实源已进入归档闭环。 |
| E2 | data_sample | `issues/requirements/_registry.yaml` | `REQ-0017-admin-space-management` 的 `lifecycle_stage` 仍为 `review`，`path` 仍为 `issues/requirements/review/REQ-0017-admin-space-management/`。 | registry 与单条 REQ 事实源、真实目录不一致。 |
| E3 | data_sample | `issues/requirements/CHANGELOG.md` | `REQ-0017-admin-space-management` 仍展示 `in_sprint` / `review`，下一步为 `/opsx-apply ...`，事实源路径为 `review/.../trace.md`。 | 当前态看板与单条 REQ 事实源、真实目录不一致。 |
| E4 | data_sample | `openspec/archive/2026-08-14-add-admin-space-management/` | 关联 Change 归档目录存在。 | OpenSpec 归档侧已经闭环，不应继续提示 apply。 |
| E5 | reproduction | `/bug-explore BUG-0012-requirement-registry-changelog-req0017-archive-drift` | 对比 REQ trace、registry、CHANGELOG 和文件系统路径后，漂移可稳定复现。 | 问题不是单次读取误差，而是治理资产持久化状态不一致。 |
| E6 | runtime_log | Codex session summary `2026-08-14 16:29 sprint-archive sprint-002` | `/sprint-archive sprint-002` 执行中，`validate-sprint-archive-readiness.py --sprint sprint-002` 显示 `add-admin-space-management` 为 `archived`、`120/120` tasks、PASS；随后 `promote-issues-for-archive.py --sprint sprint-002` 返回 “No issues eligible for review → archive promotion”。 | 归档关闭链路确认 Change 已归档，但 Issue promotion 阶段没有处理任何 review→archive 迁移或对应 Issue 索引刷新。 |
| E7 | runtime_log | Codex session summary `2026-08-14 16:29 sprint-archive sprint-002` | `check-sprint-close-stale-scan.py --sprint sprint-002` 报告 `Sprint Path: iterations/change/sprint-002`、`Checked Files: 137`、`Blockers: 0`、`Warnings: 0`、PASS。 | 关闭前 stale scan 聚焦 Sprint 目录与已知 stale 文案，不覆盖 `issues/requirements/_registry.yaml` 和 `issues/requirements/CHANGELOG.md` 的 REQ-0017 当前态一致性。 |
| E8 | runtime_log | Codex session summary `2026-08-14 16:29 sprint-archive sprint-002` | `generate-sprint-fact-sheet.py --sprint sprint-002 --json` 的 scope 包含 `REQ-0017-admin-space-management`，且 readiness 已认定 `add-admin-space-management` archived，但后续四件套关闭和 Sprint 目录迁移前没有出现针对 `REQ-0017` 的 `req.archive` Workflow Sync 输出。 | Sprint archive 以 Change/Sprint readiness 通过为闭环依据，缺少聚焦 REQ-0017 的目录级索引同步步骤。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| REQ-0017 尚未归档，registry/CHANGELOG 的 `review` 状态是正确的 | E1、E4 显示 REQ trace 与 OpenSpec Change 均已归档。 |
| 真实目录仍在 `review/` | E1 的事实源路径位于 `archive/`，且 capture/explore 阶段已定位真实目录存在于 `issues/requirements/archive/REQ-0017-admin-space-management/`。 |
| 本 BUG 应覆盖 sprint-002 归档材料中的旧路径残留 | 用户在 `/bug-generate BUG-0012 A` 中选择 A，修复范围收敛为 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md`。 |

## 已确认根因

`sprint-archive sprint-002` 关闭链路在确认 `add-admin-space-management` 已 archived 后，执行了 Sprint 级 promote 与 stale scan，但这两个步骤没有覆盖已在 `archive/` 的 `REQ-0017-admin-space-management` 的目录级当前态索引刷新：

- `promote-issues-for-archive.py --sprint sprint-002` 返回无可迁移 Issue，因此没有触发 review→archive 迁移后的 registry/CHANGELOG 更新。
- `check-sprint-close-stale-scan.py --sprint sprint-002` 主要扫描 `iterations/change/sprint-002` 与已知 stale 文案，不检查 `issues/requirements/_registry.yaml` 和 `issues/requirements/CHANGELOG.md` 中每条 REQ 的路径/阶段是否与真实目录一致。
- 关闭链路中没有针对 `REQ-0017-admin-space-management` 的聚焦 `req.archive` Workflow Sync 输出。

因此，已确认根因是 Sprint 归档关闭链路只验证了 Change/Sprint readiness 和部分历史 stale 文案，没有在 Issue 已归档但目录级索引滞后的场景下强制刷新或校验 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md`，导致 REQ-0017 的派生索引保留 `review/` 路径和 `in_sprint` 下一步。

## 修复方向

- 将 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 更新为 `status: done`、`lifecycle_stage: archive`、`path: issues/requirements/archive/REQ-0017-admin-space-management/`，并补齐关联 Change `add-admin-space-management`。
- 将 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 更新为 `done` / `archive`，下一步为“无”，事实源路径指向 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`。
- 修复后运行聚焦校验，确认两个目录级索引与单条 REQ trace、真实目录和 OpenSpec archive 一致。
- 若后续能补到归档命令日志，再判断是否需要增强 Workflow Sync 或 archive promote 校验，避免同类漂移复发。

## 验证闭环

根因证据已覆盖真实目录、REQ trace、OpenSpec archive、requirements registry/CHANGELOG 漂移，以及 `sprint-archive sprint-002` 历史执行摘要。

后续修复完成后必须验证：

- `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 与真实 archive 目录一致。
- `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 当前态与 trace 一致。
- `python scripts/validate-root-cause-evidence.py --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift` 通过。
