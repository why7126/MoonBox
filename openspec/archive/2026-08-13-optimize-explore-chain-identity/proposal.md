## 背景

MoonBox 已在 REQ/BUG 管理规则中要求后续 `/opsx-*` 命令保留完整 Issue 链路身份，但通用 `/explore` 与 `/opsx-explore` 的输出契约仍偏笼统。Agent 在探索已存在 Change 后，容易把下一步写成 `/opsx-apply <change-id>`，导致 REQ/BUG 来源链路丢失，后续 Workflow Sync、Sprint scope 和 Issue trace 追溯需要额外解析。

本次治理优化明确：探索命令在输出下一步 `/opsx-*` 命令时，只要上下文可识别该 Change 来源于 REQ 或 BUG，就必须使用完整 `REQ-xxxx-slug` 或 `BUG-xxxx-slug`；只有无 REQ/BUG 来源的纯治理 Change 才使用 `<change-id>`。

## 变更内容

- 更新 `/explore` Skill，增加下一步 `/opsx-*` 参数解析顺序和输出示例。
- 更新 `/opsx-explore` Skill，增加 Change 来源识别与 REQ/BUG 链路身份保留要求。
- 更新命令顺序文档，补充 explore 场景下的正确与错误示例。
- 更新 `scripts/validate-agent-context-budget.py`，校验 `/explore` 与 `/opsx-explore` 是否包含链路身份契约。
- 将本纯治理 Change 纳入当前 Sprint 范围。
- 写入治理迭代日志。

## 能力范围

### 修改能力

- `agent-workflow-tooling`: 强化探索命令输出下一步 `/opsx-*` 命令时的链路身份规范。

## 影响范围

- `.agents/skills/explore/SKILL.md`
- `.agents/skills/opsx-explore/SKILL.md`
- `docs/08-command-execution-order.md`
- `scripts/validate-agent-context-budget.py`
- `openspec/archive/2026-08-13-optimize-explore-chain-identity/`
- `iterations/archive/sprint-002/`
- `docs/spec-logs/`

不修改业务 `src/`、API、数据库、Web UI、客户端、部署拓扑或正式 `openspec/specs/`。
