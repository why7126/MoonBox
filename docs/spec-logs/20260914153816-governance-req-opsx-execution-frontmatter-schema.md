---
purpose: 治理迭代日志
content: 固化 req-opsx 生成 Change trace execution frontmatter schema v1
created_at: 2026-09-14 15:38:16
updated_at: 2026-09-15 08:32:35
owner: MoonBox 产品团队
---

# 固化 req-opsx execution frontmatter schema v1

## 迭代目标

将 `/req-opsx` 生成 OpenSpec Change trace 时的 `execution` frontmatter 固化为 schema v1，避免后续 Workflow Sync 因缺失执行元数据模板而反复补写或同步失败。

## 变更摘要

- `/req-opsx` 技能新增 Change trace `execution.schema_version: 1` 初始模板。
- 明确 `started_at` 与 `completed_at` 在创建阶段为 `null`，`last_event` 为 `req.opsx`。
- `scripts/validate-agent-context-budget.py` 增加 `/req-opsx` schema v1 required 片段检查。
- `scripts/workflow_sync/execution.py` 将 `None` 或空值执行时间按缺失处理，确保 `opsx.start` 能写入真实启动时间。
- `tests/unit/test_workflow_execution.py` 增加 schema v1 初始 `null` 模板的 start/apply 回归测试。
- 同步 `AGENTS.md`、`rules/agent-context-budget.md`、OpenSpec Change 文档和 Sprint scope。

## 影响范围

- Agent 命令模板：影响后续 `/req-opsx` 生成的 Change trace。
- 治理校验：影响上下文预算校验与 Workflow Sync 执行事实写入。
- OpenSpec/Sprint：新增纯治理 Change `solidify-req-opsx-execution-frontmatter-schema` 并纳入 `sprint-006`。

## 更新文件

- `.agents/skills/req-opsx/SKILL.md`
- `scripts/validate-agent-context-budget.py`
- `scripts/workflow_sync/execution.py`
- `tests/unit/test_workflow_execution.py`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `openspec/archive/2026-09-15-solidify-req-opsx-execution-frontmatter-schema/`
- `iterations/change/sprint-006/sprint.yaml`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- 脚本编译通过：`scripts/workflow_sync/execution.py`、`scripts/validate-agent-context-budget.py`。
- 聚焦单元测试通过：`tests/unit/test_workflow_execution.py`、`tests/unit/test_validate_agent_context_budget.py`，共 21 passed。
- 上下文预算、OpenSpec 中文、目录结构、目标 Change、Sprint scope 与 Workflow Sync 校验通过。
- 归档通过：`bash scripts/archive-change.sh solidify-req-opsx-execution-frontmatter-schema`。
- 归档证据通过：`python scripts/validate-archive-evidence.py --change solidify-req-opsx-execution-frontmatter-schema --archive-path openspec/archive/2026-09-15-solidify-req-opsx-execution-frontmatter-schema`。
- 状态同步通过：`python scripts/sync-workflow-status.py --event opsx.archive --change solidify-req-opsx-execution-frontmatter-schema --sprint auto`。
- Issue promote 通过：该 Change 为纯治理项，无可迁移 REQ/BUG。
- 全量 OpenSpec strict 通过：`openspec validate --all --strict`。
- AI Usage hook 返回 warning：`usage_mode: unavailable`、`command_run_count: 0`，原因是未发现可归因的 `token_count` 事件；不阻断本次治理变更。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用，未修改接口契约。
- DB：不适用，未修改 schema、迁移或持久化数据。
- Web/管理端/客户端/Orval：不适用，未修改前端或生成客户端。
- Docker Compose：不适用，未修改部署拓扑。

## 后续建议

可评估 `/bug-opsx` 是否需要同样固化 `last_event: bug.opsx` 的 execution schema v1 模板。
