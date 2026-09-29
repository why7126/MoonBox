---
created_at: 2026-09-15 09:49:03
updated_at: 2026-09-15 09:52:59
type: governance
topic: opsx-modify-repair-stage-flow
---

# opsx-modify 返修阶段流转治理

## 迭代目标

明确 `/opsx-modify` 的返修阶段流转：返修执行中用户可见阶段展示为研发中；返修完成、验证和 Workflow Sync 通过后回到验收中；保留 Change `applied` 事实，不用普通 `in_progress` 覆盖首次 apply 完成事实。

## 变更摘要

- 新建纯治理 Change `clarify-opsx-modify-repair-stage-flow` 并纳入 `sprint-007`。
- 更新 `/opsx-modify` Skill，补充返修执行中和返修完成后的阶段投影语义。
- 更新命令顺序、文档治理、上下文预算和 AGENTS 入口规则，避免后续命令把返修中展示态误写成 canonical 状态回退。
- 新增 OpenSpec delta spec，固化返修投影态与 applied 事实分层。

## 影响范围

- Skill：`.agents/skills/opsx-modify/SKILL.md`
- 入口与长期规则：`AGENTS.md`、`docs/08-command-execution-order.md`、`rules/document-governance.md`、`rules/agent-context-budget.md`
- OpenSpec：`openspec/changes/clarify-opsx-modify-repair-stage-flow/`
- Sprint：`iterations/change/sprint-007/sprint.yaml`
- 规范日志：`docs/spec-logs/CHANGELOG.md`

## API/DB/Web/客户端/部署影响

- API：不涉及；无接口路径、响应字段、OpenAPI 或 Orval 变化。
- DB：不涉及；无 schema、迁移或持久化数据变化。
- Web/管理端：不修改运行时代码；本次只定义治理阶段语义。
- 客户端生成：不涉及。
- Docker Compose/部署：不涉及。
- 安全：不涉及权限、认证、上传、对象存储或密钥边界变化。

## 验证结果

- `python scripts/sync-workflow-status.py --event opsx.start --change clarify-opsx-modify-repair-stage-flow --sprint auto`：通过，更新 3 个投影。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change clarify-opsx-modify-repair-stage-flow --residual-report`：通过，未发现非当前 Change 中文残留。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate clarify-opsx-modify-repair-stage-flow --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item clarify-opsx-modify-repair-stage-flow`：通过。
- `git diff --check -- <本次触达文件>`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change clarify-opsx-modify-repair-stage-flow --sprint auto`：通过，更新 3 个投影。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change clarify-opsx-modify-repair-stage-flow --sprint sprint-007 --json`：warning，`usage_mode: unavailable`、`command_run_count: 0`，不阻断父命令。
- `python scripts/validate-change-delivery-evidence.py --change clarify-opsx-modify-repair-stage-flow`：通过。
- 最终复核：上下文预算、当前 Change 中文、OpenSpec strict、目录结构、Sprint scope 和聚焦 diff whitespace 均通过。

## 后续建议

后续若要让需求中心运行时卡片在 `/opsx-modify` 执行过程中实时展示“研发中”，应在业务 Change 中为运行时读取补充专门的返修投影字段或事件，不应复用普通 `in_progress` 覆盖 `applied`。
