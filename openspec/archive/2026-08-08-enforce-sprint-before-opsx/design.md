---
purpose: OpenSpec Change Design
content: 评审后先 Sprint 再 opsx 的命令顺序设计
created_at: 2026-08-08 20:38:15
updated_at: 2026-08-08 20:38:15
owner: MoonBox 产品团队
---

# 评审后先 Sprint 再 opsx 的命令顺序设计

## 设计决策

### D1：review 只通向 Sprint

`/req-review --approve` 和 `/bug-review --approve` 只代表评审通过，下一步必须是 Sprint 规划。这样 Sprint scope 成为 OpenSpec Change 创建前的正式承载边界。

### D2：opsx 转换要求 in_sprint

`/req-opsx` / `/bug-opsx` 不再把 `approved` 作为可继续状态。遇到 `approved` 时应停止，并输出对应 `/sprint-propose` 命令。

### D3：sprint-propose 负责接续 opsx

`/sprint-propose` 成功后，Workflow Sync 将 Issue 同步为 `in_sprint`，此时下一步才输出 `/req-opsx <REQ-full-id>` 或 `/bug-opsx <BUG-full-id>`。

## 验证策略

- 运行 `python scripts/validate-agent-context-budget.py`，确认 skill 不再回退到旧顺序。
- 运行 OpenSpec 语言校验和目录结构校验。
- 运行 `openspec validate enforce-sprint-before-opsx`。
- 运行 Workflow Sync、Sprint scope 校验和 AI Usage hook。
