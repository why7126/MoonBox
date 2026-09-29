## 背景

`/req-opsx` 已固化 Change trace `execution.schema_version=1` 模板，但 `/bug-opsx` 仍缺少对应的 schema v1 初始 frontmatter。BUG 链路创建 fix Change 时如果缺失 `execution` 初始块，后续 Workflow Sync 执行事实仍可能出现补写或同步失败。

## 变更内容

- 在 `/bug-opsx` 技能中固化新建 Change `trace.md` 的 `execution` frontmatter schema v1 模板。
- 明确 `/bug-opsx` 创建阶段只写 `schema_version: 1`、`started_at: null`、`completed_at: null`、`last_event: bug.opsx`，不伪造实施启动或完成时间。
- 扩展上下文预算校验脚本，检查 `/bug-opsx` 技能必须保留 `execution.schema_version: 1` 与 `last_event: bug.opsx` 契约，防止模板回退。
- 同步 AGENTS、上下文预算规则、OpenSpec Change 和治理日志。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `agent-workflow-tooling`: `/bug-opsx` 生成 OpenSpec fix Change trace 时，必须带 schema v1 execution frontmatter 初始块。

## 影响范围

- 技能：`.agents/skills/bug-opsx/SKILL.md`。
- 校验：`scripts/validate-agent-context-budget.py`。
- 规则入口：`AGENTS.md`、`rules/agent-context-budget.md`。
- 文档：本 Change 与治理日志。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理命令模板、校验脚本和文档。
