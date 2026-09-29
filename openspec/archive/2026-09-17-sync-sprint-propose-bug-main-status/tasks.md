## 1. OpenSpec And Sprint Scope

- [x] 1.1 创建 `sync-sprint-propose-bug-main-status` Change，补齐 proposal、design、tasks 与 trace。
- [x] 1.2 将纯治理 Change 纳入 Sprint scope，并通过 Workflow Sync / Sprint scope 校验。

## 2. Workflow Sync Script

- [x] 2.1 增强 `scripts/workflow_sync/engine.py`，让 `sprint.propose` 聚焦 REQ/BUG 时默认同步子文档。
- [x] 2.2 保持同步范围限定为当前 `--req` / `--bug` 聚焦 Issue。

## 3. Tests And Validation

- [x] 3.1 增加聚焦单元测试覆盖 `sprint.propose --bug` 同步 `bug.md` 主状态。
- [x] 3.2 运行聚焦 pytest 和脚本编译检查。
- [x] 3.3 运行治理校验：上下文预算、OpenSpec 语言、目录结构、目标 Change validate、Sprint scope、Workflow Sync dry-run/check。

## 4. Governance Log

- [x] 4.1 写入 `docs/spec-logs/20260915231447-governance-sprint-propose-bug-main-status.md`。
- [x] 4.2 更新 `docs/spec-logs/CHANGELOG.md` 索引。
- [x] 4.3 最终执行 Workflow Sync 与 AI Usage Hook，并输出执行链路复盘。
