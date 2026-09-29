## 1. OpenSpec And Sprint Scope

- [x] 1.1 创建 `enhance-workflow-sync-current-status-block` Change，补齐 proposal、design、delta spec、tasks 与 trace。
- [x] 1.2 将纯治理 Change 纳入 `sprint-006` scope，并通过 Workflow Sync / Sprint scope 校验。

## 2. Workflow Sync Script

- [x] 2.1 增强 `scripts/workflow_sync/patch.py`，同步 `## 当前状态` fenced `yaml` 中的 `next`。
- [x] 2.2 增强同一代码块中的 `openspec_changes`，兼容 scalar 条目升级和状态同步。
- [x] 2.3 限定同步范围为 `## 当前状态` 章节内首个 fenced `yaml`，避免改写其他语义块。

## 3. Tests And Validation

- [x] 3.1 增加聚焦单元测试覆盖 `openspec_changes` 与 `next` 同步。
- [x] 3.2 运行聚焦 pytest 和脚本编译检查。
- [x] 3.3 运行治理校验：上下文预算、OpenSpec 语言、目录结构、目标 Change validate、Sprint scope、Workflow Sync dry-run/check。

## 4. Governance Log

- [x] 4.1 写入 `docs/spec-logs/20260914152241-governance-workflow-sync-current-status-block.md`。
- [x] 4.2 更新 `docs/spec-logs/CHANGELOG.md` 索引。
- [x] 4.3 最终执行 Workflow Sync 与 AI Usage Hook，并输出执行链路复盘。
