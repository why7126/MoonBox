## 背景

MoonBox 的 Agent 命令在需要用户反馈时，当前多以纯文字开放式追问为主。用户需要阅读较长上下文后再自行组织回复，容易导致决策负担高、反馈信息不稳定、命令动态收敛慢。

本次治理优化统一命令用户反馈交互规范：当命令需要用户选择、确认、补充范围、确认风险或处理阻塞时，优先使用“原生交互卡片 + 结构化选项 + 推荐项 + 可补充说明”的引导式提问；当客户端或工具层不支持原生交互卡片时，降级为文本结构化选项。每轮只聚焦少量关键决策，并根据用户答案动态收敛。

## 变更内容

- 在 `rules/agent-context-budget.md` 增加命令用户反馈交互契约。
- 更新 `explore`、`capture`、`req-*`、`bug-*`、`sprint-*`、`opsx-*`、`release-*`、`git-*` 命令 Skill，要求用户反馈优先采用原生交互卡片，无法支持时降级为文本决策卡。
- 更新 `AGENTS.md` 命令交互红线，作为全局入口约束。
- 更新 `scripts/validate-agent-context-budget.py`，校验目标命令 Skill 是否接入引导式反馈契约。
- 写入治理迭代日志，记录影响范围、验证和后续建议。
- 不修改业务 `src/`、API、数据库、Web UI、部署拓扑或正式 `openspec/specs/`。

## 能力范围

### 新增能力

- `guided-command-feedback`: 定义命令用户反馈的结构化选项、推荐项、可补充说明、少量关键决策、动态收敛和输出边界。

### 修改能力

- `agent-workflow-tooling`: 增强 Agent 命令输出契约与校验门禁。

## 影响范围

- `AGENTS.md`：新增命令交互红线。
- `rules/agent-context-budget.md`：新增统一反馈交互规范。
- `.agents/skills/**/SKILL.md`：目标命令族新增引导式反馈契约。
- `scripts/validate-agent-context-budget.py`：新增契约校验。
- `docs/spec-logs/`：新增治理迭代日志。
- `iterations/archive/sprint-002/`：纳入纯治理 Change 范围。
