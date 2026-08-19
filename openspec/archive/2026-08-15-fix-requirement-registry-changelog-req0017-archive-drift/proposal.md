## 背景与动机

BUG-0012 记录了一个非阻塞但会误导后续治理判断的索引漂移：`REQ-0017-admin-space-management` 已归档，真实目录位于 `issues/requirements/archive/REQ-0017-admin-space-management/`，关联 Change `add-admin-space-management` 也已 archived，但 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 仍保留 review 路径、开发中状态和 `/opsx-apply` 下一步。

该漂移不影响运行时代码，但会影响人工查阅、后续命令判断、当前态看板和治理巡检。因此需要通过一个聚焦 fix Change 修正目录级索引，并补充验证，确保两个索引与单条 REQ trace、真实目录和 OpenSpec archive 一致。

## 变更内容

- 修正 `issues/requirements/_registry.yaml` 中 `REQ-0017-admin-space-management` 的状态、阶段、路径和关联 Change。
- 修正 `issues/requirements/CHANGELOG.md` 中 `REQ-0017-admin-space-management` 的当前态行、下一步和事实源路径。
- 保持单条 REQ `trace.md` 与 OpenSpec archive 事实源不被回退。
- 增加聚焦验证，确认本次修复不扩散到 `src/`、`openspec/` 正式规格以外的运行时代码，也不纳入 `iterations/archive/sprint-002` 历史残留。

## 能力影响

### 新增能力

无。

### 修改能力

- `agent-workflow-tooling`: 强化 Issue 当前态看板与 registry 的归档态一致性要求，明确历史漂移修复时必须以单条 Issue trace、真实目录和 OpenSpec archive 为权威事实源。

## 影响范围

- 治理文档：`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md`。
- 验证：聚焦 `rg` 校验与 `validate-root-cause-evidence.py`。
- 不影响：`src/`、API、DB、Web UI、部署、客户端生成物和生产数据。

## 回滚计划

如修复后发现索引仍不一致，以 `issues/requirements/archive/REQ-0017-admin-space-management/trace.md` 与 `openspec/archive/2026-08-14-add-admin-space-management/` 为权威事实源，回滚或重新生成目录级索引行；不得恢复 `review/` 路径或 `/opsx-apply REQ-0017-admin-space-management` 下一步。
