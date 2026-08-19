---
purpose: OpenSpec Change Proposal
content: 为 opsx-modify 增加 REQ 子文档一致性扫尾检查
created_at: 2026-08-15 13:02:00
updated_at: 2026-08-15 13:02:00
owner: MoonBox 产品团队
---

# Proposal: add-opsx-modify-req-subdoc-sweep

## 背景

`/opsx-modify` 已要求验收返修同步 Change 文档和 linked Issue 文档，但 REQ 来源返修仍容易只更新主 PRD 或 acceptance，而遗漏业务流程、用户故事和 prototype HTML/context 等子文档。该遗漏会在 `/opsx-archive` 前形成口径漂移，使最终归档规格、REQ 文档和原型证据不一致。

## 变更内容

- 在 `/opsx-modify` 完成前增加 “REQ 子文档一致性扫尾检查”。
- 要求 REQ 来源返修按当前 REQ 目录实际存在的子文档逐项检查：`requirement.md`、业务流程、用户故事、`acceptance.md`、`trace.md`、`prototype/**`。
- 要求返修改变产品行为、UI/交互、验收口径、Mock/API 边界或原型意图时，同步相关 REQ 子文档；无需更新时必须记录理由。

## 非目标

- 不修改业务运行时代码。
- 不新增 REQ/BUG 生命周期状态。
- 不改变 `/opsx-archive` 的既有归档门禁，只提前在 `/opsx-modify` 阶段降低漂移风险。

## 影响

- 影响 `.agents/skills/opsx-modify/SKILL.md` 的执行契约。
- 影响 Agent 工作流治理规格与 Sprint scope。
- API、DB、Web、客户端生成、管理端、Docker Compose 均无运行时影响。
