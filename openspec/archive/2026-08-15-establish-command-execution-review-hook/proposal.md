## 背景

MoonBox 已有命令输出中的「下一步」和「待用户决策/处理」契约，也有 Workflow Sync、AI Usage 和证据化根因分析治理；但每次命令执行结束后，AI 还没有固定反馈“本次执行链路是否顺畅、是否暴露流程问题、是否有规范优化点”。这会导致小型流程摩擦只停留在当次上下文里，难以沉淀为可复用治理经验。

## 变更内容

- 新增命令执行复盘 Hook：workflow 命令完成后输出链路状态、问题证据和规范优化建议。
- 默认保持轻量：没有发现问题时只输出“无明显优化点”，不得为了复盘而制造长篇报告。
- 明确 follow-up 边界：发现治理优化或缺陷时只给 capture/spec-opt 建议，不自动创建 REQ/BUG/Change，除非用户明确授权。
- 更新 Agent 上下文预算规则、Workflow Sync 技能和校验脚本，确保该 Hook 成为命令输出契约的一部分。
- 不修改业务 `src/`、API、DB schema、Web UI 或生产部署拓扑。

## 能力范围

### 新增能力

- `command-execution-review-hook`: workflow 命令结束后的轻量链路复盘、问题证据和规范优化建议输出契约。

### 修改能力

- `agent-workflow-tooling`: 增加命令执行复盘 Hook 要求。

## 影响范围

- `rules/agent-context-budget.md`：新增 Hook 的通用输出契约。
- `.agents/skills/workflow-sync/SKILL.md`：补充 workflow 命令完成后复盘 Hook 口径。
- `scripts/validate-agent-context-budget.py`：新增中央契约校验，避免 Hook 规则被移除。
- `AGENTS.md`、`docs/08-command-execution-order.md`、`docs/README.md`：同步命令输出和流程治理说明。
- `openspec/changes/establish-command-execution-review-hook/` 与 `iterations/change/sprint-003/`：记录本次治理 Change。
- `docs/spec-logs/`：写入治理迭代日志和索引。
