## 背景

`rules/document-governance.md` 已定义 Change trace 的 `execution.schema_version=1` 用于记录执行事实，但 `/req-opsx` 生成 Change trace 时没有把该 frontmatter 作为固定模板。部分新建 Change 因缺少 schema v1 初始块，后续 Workflow Sync 需要补写或推断执行元数据，容易造成同类同步失败。

## 变更内容

- 在 `/req-opsx` 技能中固化新建 Change `trace.md` 的 `execution` frontmatter schema v1 模板。
- 明确 `/req-opsx` 创建阶段只写 `schema_version: 1`、`started_at: null`、`completed_at: null`、`last_event: req.opsx`，不伪造实施启动或完成时间。
- 扩展上下文预算校验脚本，检查 `/req-opsx` 技能必须保留 `execution.schema_version: 1` 与 `last_event: req.opsx` 契约，防止模板回退。
- 修复 Workflow Sync 执行事实写入逻辑，使 `started_at: null` 的 schema v1 初始模板在 `opsx.start` 时能被真实启动时间替换。
- 同步 AGENTS、上下文预算规则、OpenSpec Change 和治理日志。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `agent-workflow-tooling`: `/req-opsx` 生成 OpenSpec Change trace 时，必须带 schema v1 execution frontmatter 初始块。

## 影响范围

- 技能：`.agents/skills/req-opsx/SKILL.md`。
- 脚本：`scripts/validate-agent-context-budget.py`、`scripts/workflow_sync/execution.py`。
- 测试：`tests/unit/test_workflow_execution.py`。
- 规则入口：`AGENTS.md`、`rules/agent-context-budget.md`。
- 文档：本 Change 与治理日志。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理命令模板、校验脚本和文档。
