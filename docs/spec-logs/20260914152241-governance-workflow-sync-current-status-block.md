---
purpose: Workflow Sync 当前状态代码块同步治理日志
content: 记录 Workflow Sync 同步 Issue trace 正文当前状态 yaml 代码块中 openspec_changes 与 next 的脚本增强
created_at: 2026-09-14 15:22:41
updated_at: 2026-09-14 15:22:41
owner: MoonBox 产品团队
---

# Workflow Sync 当前状态代码块同步治理日志

## 迭代目标

增强 Workflow Sync，让 Issue `trace.md` 正文 `## 当前状态` 章节内的 fenced `yaml` 快照自动同步 `openspec_changes` 与 `next`，减少后续手动扫尾和状态漂移。

## 变更摘要

- 新增当前状态 yaml 代码块同步逻辑，基于派生下一步命令写回 `next`。
- 同步 `openspec_changes` 中目标 Change 的状态，并兼容旧式 scalar 条目升级。
- 将同步范围限定在 `## 当前状态` 章节内首个 fenced `yaml`，避免影响 Readiness、验收或历史示例块。
- 增加聚焦单元测试覆盖旧 `next` 与旧 scalar `openspec_changes` 的同步。

## 影响范围

- Workflow Sync 治理脚本。
- Issue trace 文档派生同步。
- OpenSpec `agent-workflow-tooling` 治理规格。
- 治理日志与 spec-logs 索引。

## 更新文件

- `scripts/workflow_sync/patch.py`
- `tests/unit/test_workflow_sync_patch.py`
- `openspec/changes/enhance-workflow-sync-current-status-block/`
- `docs/spec-logs/20260914152241-governance-workflow-sync-current-status-block.md`
- `docs/spec-logs/CHANGELOG.md`
- `iterations/change/sprint-006/sprint.yaml`

## 验证结果

已运行：

- `python -m pytest tests/unit/test_workflow_sync_patch.py tests/unit/test_workflow_sync_engine.py`：通过，13 passed。
- `python -m py_compile scripts/workflow_sync/patch.py`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change enhance-workflow-sync-current-status-block`：通过。
- `python scripts/validate-directory-structure.py`：未通过；失败项为既有根目录 `.vite` 未登记，本次未修改该目录。
- `openspec validate enhance-workflow-sync-current-status-block --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-006 --item enhance-workflow-sync-current-status-block`：通过。
- `python scripts/sync-workflow-status.py --sprint auto`：通过，修复 `sprint.md` 派生漂移。
- `python scripts/sync-workflow-status.py --event opsx.start --change enhance-workflow-sync-current-status-block --sprint auto`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change enhance-workflow-sync-current-status-block --sprint auto`：通过，完成态同步 updated=3。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enhance-workflow-sync-current-status-block --sprint sprint-006 --json`：warning，`usage_mode: unavailable`，未发现可归因 command-run token_count 事件。

## API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose 影响

- API：不适用，未修改接口契约。
- DB：不适用，未修改 schema、迁移、索引或数据保留策略。
- Web / 管理端 / 客户端：不适用，未修改业务前端或客户端生成物。
- Orval：不适用，未修改 OpenAPI 或客户端生成配置。
- Docker Compose：不适用，未修改部署拓扑、环境变量或服务配置。

## 后续建议

后续可评估是否将更多人读快照字段纳入结构化派生清单，但必须先确认唯一事实源，避免把历史说明区误改为当前事实。
