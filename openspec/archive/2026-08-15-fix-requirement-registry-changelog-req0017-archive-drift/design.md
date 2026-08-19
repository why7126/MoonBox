## 根因

BUG-0012 的根因状态为 `confirmed`。`sprint-archive sprint-002` 已确认 `add-admin-space-management` archived，但关闭链路的 promote 与 stale scan 没有覆盖已归档 REQ 的目录级当前态索引刷新：

- `promote-issues-for-archive.py --sprint sprint-002` 返回无可迁移 Issue，因此未触发 REQ-0017 的 registry/CHANGELOG 刷新。
- `check-sprint-close-stale-scan.py --sprint sprint-002` 聚焦 Sprint 目录和已知 stale 文案，没有检查 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 的单条 REQ 路径/阶段一致性。
- 关闭链路中没有聚焦 `REQ-0017-admin-space-management` 的 `req.archive` Workflow Sync 输出。

## 修复方案

本 Change 采用最小治理修复：

1. 以 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` 和 `openspec/archive/2026-08-14-add-admin-space-management/` 为权威事实源。
2. 更新 `issues/requirements/_registry.yaml` 中 REQ-0017：
   - `status: done`
   - `lifecycle_stage: archive`
   - `path: issues/requirements/archive/REQ-0017-admin-space-management/`
   - `related_changes` 包含 `add-admin-space-management`
3. 更新 `issues/requirements/CHANGELOG.md` 中 REQ-0017：
   - 当前状态 `done`
   - 阶段 `archive`
   - 关联 Sprint `sprint-002`
   - 关联 Change `add-admin-space-management`
   - 下一步 `无`
   - 事实源 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md`
4. 不修改 `src/`，不修改 API、DB、UI、部署和客户端生成物。
5. 不把 `iterations/archive/sprint-002` 中可能存在的旧路径或旧状态残留纳入本 BUG 修复范围。

## 测试与验收

- 运行聚焦 `rg` 校验，确认 REQ-0017 在 registry、CHANGELOG 和单条 trace 中一致。
- 运行 `python scripts/validate-root-cause-evidence.py --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift`，确认根因证据门禁仍通过。
- 运行 OpenSpec 校验，确认 Change artifacts 格式有效。
- 修复完成后由 Workflow Sync 回填 BUG 与 Sprint 当前态。

## 风险

- 风险较低，修复只涉及治理索引文档。
- 若人工误把 sprint-002 归档四件套历史残留纳入本 Change，会扩大范围并偏离用户已选择的 A 方案；tasks 中显式加入范围门禁避免扩散。
