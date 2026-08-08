---
purpose: OpenSpec Change Proposal
content: 应用 ProjectTilesFST 命令执行顺序治理经验
created_at: 2026-08-07 23:20:00
updated_at: 2026-08-07 23:20:00
owner: MoonBox 产品团队
---

# Proposal

## 背景

MoonBox 已引入 REQ/BUG、Sprint、OpenSpec、发布、镜像和产品手册等命令族，但“下一步命令”和“严格串行步骤”的统一口径分散在各技能内。ProjectTilesFST 对命令执行顺序、Sprint scope 机器事实源、Workflow Sync、Issue promote 和 AI Usage hook 有更清晰的顺序治理经验。

## 目标

- 增加 MoonBox 命令执行顺序速查文档。
- 在关键技能中补充统一 Command Order，明确从 REQ/BUG 到 Sprint、OpenSpec、apply、modify、archive、release 的推荐顺序。
- 强化下一步命令参数规则：REQ 来源继续使用 `REQ-*`，BUG 来源继续使用 `BUG-*`，纯治理 Change 才使用 `<change-id>`。
- 明确会写同一事实源的步骤必须串行执行，尤其是 Sprint scope、Workflow Sync、Issue promote 和 AI Usage。

## 非目标

- 不复制 ProjectTilesFST 业务专属 miniapp、瓷砖业务或设备验收流程。
- 不修改业务 `src/`。
- 不改变 API、DB、部署拓扑或发布制品。
