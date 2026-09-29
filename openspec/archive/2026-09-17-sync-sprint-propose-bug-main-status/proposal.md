## 背景

`/sprint-propose --bug <BUG-full-id>` 成功纳入 Sprint 后，Workflow Sync 已能把聚焦 BUG 的 `trace.md`、`_registry.yaml` 和 `issues/bugs/CHANGELOG.md` 同步到 `in_sprint`。但默认子文档同步分支没有覆盖 `sprint.propose` 聚焦 Issue 场景，导致已存在 `bug.md` Frontmatter `status` 时仍可能停留在 `approved`，后续需要人工聚焦修正。

本变更让 `sprint.propose` 在聚焦 REQ/BUG 时沿用主文档同步能力，确保 `requirement.md` / `bug.md` 的主状态镜像与 trace 保持一致。

## 变更内容

- Workflow Sync 在 `sprint.propose` 且传入 `--req` 或 `--bug` 时，默认同步聚焦 Issue 子文档。
- 聚焦 BUG 纳入 Sprint 后，已存在的 `bug.md` Frontmatter `status` 自动更新为 `in_sprint`。
- 保持同步范围只覆盖聚焦 Issue，不扩大到无关 REQ/BUG 子文档。
- 补充单元测试锁定 `sprint.propose --bug` 对 `bug.md` 主状态的自动同步路径。
- 写入治理日志和 Change trace，记录本次纯治理脚本优化。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `harness-runtime`: Workflow Sync 的 Issue 子文档状态投影覆盖 `sprint.propose` 聚焦 REQ/BUG 场景。

## 影响范围

- 脚本：`scripts/workflow_sync/engine.py`。
- 测试：`tests/unit/test_workflow_sync_engine.py`。
- 文档：本 Change、治理日志和 spec-logs 索引。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理脚本与治理文档。
