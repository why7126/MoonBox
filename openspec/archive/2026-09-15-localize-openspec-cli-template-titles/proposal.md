## 背景

OpenSpec CLI 的 `instructions` 返回英文 template 标题，例如 `Why`、`What Changes`、`Capabilities` 和 `Impact`。MoonBox 已要求 OpenSpec 文档中文优先，但 `/req-opsx`、`/bug-opsx` 每次生成 Change 后仍容易把英文脚手架标题带入 proposal、design 或 tasks，造成重复手工修正。

## 变更内容

- 在 `/req-opsx` 与 `/bug-opsx` 技能中固化 OpenSpec CLI 模板标题中文化映射。
- 扩展上下文预算校验脚本，防止两个 opsx 技能删除该中文化契约。
- 同步 AGENTS、语言规则、上下文预算规则、OpenSpec Change 和治理日志。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `agent-workflow-tooling`: REQ/BUG 转 OpenSpec Change 时，生成文档必须把 CLI 英文模板标题转换为项目中文标题。

## 影响范围

- 技能：`.agents/skills/req-opsx/SKILL.md`、`.agents/skills/bug-opsx/SKILL.md`。
- 脚本：`scripts/validate-agent-context-budget.py`。
- 规则入口：`AGENTS.md`、`rules/language.md`、`rules/agent-context-budget.md`。
- 文档：本 Change 与治理日志。
- API/DB/Web/管理端/客户端/Orval/Docker Compose：不适用，本变更仅调整治理命令模板、校验脚本和文档规范。
