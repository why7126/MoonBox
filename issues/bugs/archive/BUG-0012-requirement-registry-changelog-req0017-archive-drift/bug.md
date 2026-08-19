---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
title: REQ-0017 需求索引仍指向 review 路径但真实目录已归档
severity: medium
status: done
owner:
discovered_at: 2026-08-15 10:32:44
environment: governance
related_requirement: REQ-0017-admin-space-management
related_change:
created_at: 2026-08-15 10:43:41
updated_at: 2026-08-15 11:49:22
---

# 现象

`REQ-0017-admin-space-management` 已完成归档闭环，真实目录位于 `issues/requirements/archive/REQ-0017-admin-space-management/`，但需求目录级索引仍保留开发阶段路径和状态：

- `issues/requirements/_registry.yaml` 中该 REQ 的 `lifecycle_stage` 仍为 `review`，`path` 仍指向 `issues/requirements/review/REQ-0017-admin-space-management/`。
- `issues/requirements/CHANGELOG.md` 中该 REQ 仍显示 `in_sprint` / `review`，下一步仍为 `/opsx-apply REQ-0017-admin-space-management`，事实源仍指向 `issues/requirements/review/REQ-0017-admin-space-management/trace.md`。

# 复现步骤

1. 查看 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`，确认该 REQ 的 `status`、`lifecycle_stage` 与关联 Change 状态。
2. 查看 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 的 `status`、`lifecycle_stage`、`path` 和 `related_changes`。
3. 查看 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的当前状态、阶段、关联 Change、下一步和事实源路径。
4. 对比真实目录 `issues/requirements/archive/REQ-0017-admin-space-management/` 与两个目录级索引中的路径。

# 期望结果

- `issues/requirements/_registry.yaml` 应展示 `REQ-0017-admin-space-management` 已归档后的真实状态和路径：`status: done`、`lifecycle_stage: archive`、`path: issues/requirements/archive/REQ-0017-admin-space-management/`，并保留关联 Change `add-admin-space-management`。
- `issues/requirements/CHANGELOG.md` 应展示 `REQ-0017-admin-space-management` 的当前状态为 `done`、阶段为 `archive`、下一步为“无”，事实源指向 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`。
- 两个目录级索引应与单条 REQ `trace.md`、真实文件系统路径和 OpenSpec archive 状态一致。

# 实际结果

- `issues/requirements/_registry.yaml` 对 `REQ-0017-admin-space-management` 仍保留 `review/` 阶段路径。
- `issues/requirements/CHANGELOG.md` 对 `REQ-0017-admin-space-management` 仍保留开发中状态、`/opsx-apply` 下一步和 `review/` 事实源路径。
- 真实目录已在 `archive/`，单条 REQ `trace.md` 已显示 `status: done`、`lifecycle_stage: archive`，关联 Change `add-admin-space-management` 已 `archived`。

# 影响范围

- 影响域：需求/缺陷治理资产与 Workflow Sync 派生索引。
- 影响文件：`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md`。
- 影响对象：`REQ-0017-admin-space-management`。
- 影响用户：查看需求当前态、执行后续治理命令或做归档巡检的产品/工程协作成员。
- 不影响运行时代码、API、数据库、Web UI、部署或客户端生成物。

# 严重等级说明

严重等级评估为 `medium`。该问题不阻断线上功能，也不会直接造成运行时错误；但会让需求当前态索引与事实源不一致，导致人工查阅、下一步命令判断、治理巡检和后续同步动作存在误导风险。用户已明确该问题为非阻塞治理漂移，因此按中等严重度记录。

# 初步定位证据

- `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` 显示 `status: done`、`lifecycle_stage: archive`，并记录 Change `add-admin-space-management` 已 `archived`。
- `openspec/archive/2026-08-14-add-admin-space-management/` 已存在，说明关联 OpenSpec Change 已归档。
- `issues/requirements/_registry.yaml` 中该 REQ 的 `path` 仍为 `issues/requirements/review/REQ-0017-admin-space-management/`。
- `issues/requirements/CHANGELOG.md` 中该 REQ 的事实源仍为 `issues/requirements/review/REQ-0017-admin-space-management/trace.md`，下一步仍为 `/opsx-apply REQ-0017-admin-space-management`。

# 修复范围选择

本 BUG 按用户选择 A 收敛范围：仅覆盖 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的状态、阶段、路径、关联 Change 和下一步漂移修复。

本轮探索中发现的 `iterations/archive/sprint-002` 旧路径或旧状态残留不纳入本 BUG 正式修复范围；如后续需要治理，应另行 capture 或在独立修复链路中处理。
