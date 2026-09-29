## 背景

Workflow Sync 已能同步 Issue `trace.md` Frontmatter 与正文 fenced `yaml` 中的主状态、迭代和 `openspec_changes[].status`，但部分 Issue 文档还在 `## 当前状态` 章节中维护面向人读的 fenced `yaml` 快照。当前脚本只更新该章节的 bullet 状态与阶段，导致 `openspec_changes` 和 `next` 容易残留旧值，后续需要人工扫尾。

本变更增强 Workflow Sync 对正文 `## 当前状态` 章节内首个 `yaml` 代码块的同步能力，让 Change 状态与下一步命令能从现有派生态自动回填。

## 变更内容

- Workflow Sync 在 patch Issue trace 时，若 `## 当前状态` 章节包含 fenced `yaml` 代码块，自动同步 `next`。
- 同一代码块内的 `openspec_changes` 支持把旧 scalar 条目升级为 `{change_id, status}` 结构，并同步目标 Change 状态。
- 只处理 `## 当前状态` 章节内首个 `yaml` 代码块，不扩大到 Readiness、验收、历史示例或其他语义块。
- 补充聚焦单元测试，覆盖旧 `next` 和旧 scalar `openspec_changes` 漂移修复。
- 补充治理日志和 OpenSpec trace，记录本次纯治理脚本增强。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `agent-workflow-tooling`: Workflow Sync 对 Issue trace 正文当前态块的派生同步范围增加 `openspec_changes` 与 `next`。

## 影响范围

- 脚本：`scripts/workflow_sync/patch.py`。
- 测试：`tests/unit/test_workflow_sync_patch.py`。
- 文档：本 Change、治理日志和 spec-logs 索引。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理脚本与文档。
