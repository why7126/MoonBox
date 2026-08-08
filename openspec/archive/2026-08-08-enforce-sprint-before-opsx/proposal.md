---
purpose: OpenSpec Change Proposal
content: 强化评审后先 Sprint 再 opsx 的命令顺序
created_at: 2026-08-08 20:38:15
updated_at: 2026-08-08 20:38:15
owner: MoonBox 产品团队
---

# 强化评审后先 Sprint 再 opsx 的命令顺序

## 背景

当前命令顺序文档已表达“先评审、再纳入 Sprint、再创建 Change”，但 `req-review` / `bug-review` 的下一步仍可能推荐先 `/req-opsx` 或 `/bug-opsx`，且 `req-opsx` / `bug-opsx` 对 `approved` 状态仍存在直接继续的旧口径。

这会导致评审完成后绕过 Sprint scope，提前创建 OpenSpec Change，后续再靠 Workflow Sync 修补，顺序上不够稳定。

## 变更内容

- 将 `/req-review --approve` 后的下一步固定为 `/sprint-propose --req <REQ-full-id>`。
- 将 `/bug-review --approve` 后的下一步固定为 `/sprint-propose --bug <BUG-full-id>`。
- 将 `/req-opsx` / `/bug-opsx` 的入口门禁收紧为 `in_sprint` 或后续交付态；`approved` 状态必须先 Sprint。
- 更新长期规则、命令顺序文档和上下文预算校验脚本。

## 非目标

- 不修改业务代码。
- 不改变 Sprint 容量算法、OpenSpec CLI 行为或 Workflow Sync 事实源结构。
- 不修改正式 `openspec/specs/`；正式规格由归档命令合并。

## 影响范围

- 影响 `.agents/skills/req-review`、`.agents/skills/bug-review`、`.agents/skills/req-opsx`、`.agents/skills/bug-opsx`、`.agents/skills/sprint-propose`。
- 影响 `AGENTS.md`、`docs/08-command-execution-order.md`、REQ/BUG 管理规则和上下文预算校验脚本。
- API、DB、Web、客户端、管理端、Docker Compose 均无业务实现影响。
