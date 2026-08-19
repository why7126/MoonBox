## 1. 修复目录级索引

- [x] 1.1 更新 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 的 `status`、`lifecycle_stage`、`path` 与 `related_changes`。
- [x] 1.2 更新 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的当前态、阶段、Sprint、Change、下一步与事实源路径。
- [x] 1.3 确认未修改 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` 的归档事实源状态。

## 2. 聚焦验证

- [x] 2.1 运行 `rg -n "REQ-0017-admin-space-management|add-admin-space-management" issues/requirements/_registry.yaml issues/requirements/CHANGELOG.md issues/requirements/archive/REQ-0017-admin-space-management/trace.md`。
- [x] 2.2 运行 `python scripts/validate-root-cause-evidence.py --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift`。
- [x] 2.3 检查本 Change 未修改 `src/`、API、DB、UI、部署或客户端生成物。

## 3. 工作流回填

- [x] 3.1 运行 Workflow Sync，将 BUG-0012 与 Change `fix-requirement-registry-changelog-req0017-archive-drift` 回填到 `sprint-003`。
- [x] 3.2 回填 BUG trace、BUG CHANGELOG 和 Sprint scope 的关联 Change 与下一步。
- [x] 3.3 如发现 Workflow Sync 对归档态索引一致性覆盖不足，仅输出后续 capture 建议，不在本 Change 中扩展脚本修复。
