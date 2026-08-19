---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
acceptance_status: passed
created_at: 2026-08-15 10:46:46
updated_at: 2026-08-15 11:49:47
---

# 验收标准

## AC-BUG-0012-001 registry 状态与路径一致

WHEN 查看 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management`
THEN 该条目的 `status` MUST 为 `done`
AND `lifecycle_stage` MUST 为 `archive`
AND `path` MUST 为 `issues/requirements/archive/REQ-0017-admin-space-management/`
AND `related_changes` MUST 包含 `add-admin-space-management`。

## AC-BUG-0012-002 当前态看板行一致

WHEN 查看 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management`
THEN 当前状态 MUST 为 `done`
AND 阶段 MUST 为 `archive`
AND 关联 Sprint MUST 为 `sprint-002`
AND 关联 Change MUST 为 `add-admin-space-management`
AND 下一步 MUST 为“无”
AND 事实源 MUST 为 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`。

## AC-BUG-0012-003 单条事实源不被回退

WHEN 修复两个目录级索引
THEN `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` MUST 继续保持 `status: done`、`lifecycle_stage: archive`
AND `openspec_changes` 中 `add-admin-space-management` MUST 继续保持 `status: archived`。

## AC-BUG-0012-004 修复范围不扩散

WHEN 执行本 BUG 修复
THEN 不得修改 `src/`
AND 不得修改 `openspec/`
AND 不得把 `iterations/archive/sprint-002` 中旧路径或旧状态残留纳入本 BUG 的修复范围。

## AC-BUG-0012-005 聚焦验证通过

WHEN 修复完成
THEN MUST 运行聚焦校验，确认 `REQ-0017-admin-space-management` 在 `_registry.yaml`、`CHANGELOG.md`、单条 `trace.md` 和真实目录之间一致
AND MUST 运行 `python scripts/validate-root-cause-evidence.py --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift` 或记录因根因状态仍为 `probable` 导致暂不可通过评审门禁的原因。

## 建议验证命令

```bash
rg -n "REQ-0017-admin-space-management|add-admin-space-management" issues/requirements/_registry.yaml issues/requirements/CHANGELOG.md issues/requirements/archive/REQ-0017-admin-space-management/trace.md
python scripts/validate-root-cause-evidence.py --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift
```

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-15 11:49:47
accepted_by: workflow-sync
source_change: fix-requirement-registry-changelog-req0017-archive-drift
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

