---
title: 产品治理命令能力矩阵复核
created_at: 2026-10-13 16:58:00
updated_at: 2026-10-14 09:00:00
---

# 产品治理命令能力矩阵复核

产品内 `RequirementCenterPage.tsx` 的 `productGovernanceCommandCapabilities` 是动作路由所用的命令能力矩阵，逐命令映射如下：

| 命令 | 当前能力 | 产品动作边界 |
|---|---|---|
| `req-generate`、`bug-generate` | `real_candidate_write` | 采集池动作请求 `/api/v1/chat/governance-preparations`，先准备真实候选；后续应用另验 |
| `req-complete`、`bug-complete`、`req-review`、`bug-review`、`sprint-propose`、`req-opsx`、`bug-opsx`、`opsx-apply`、`opsx-archive` | `real_object_session_write` | 打开绑定对象的产品 Chat 会话；具体事实源应用必须通过后端门禁与同轮 application 另验 |
| `req-explore`、`bug-explore` | `display_only` | 只读探索，不声明治理事实源应用 |
| 未列入矩阵的命令 | `codex_command_only` | 显示 Codex 命令提示，未知命令不会创建产品对象会话 |
| 显式 mock query 下的上述动作 | `demo_simulation` | 只在受控 demo 数据中模拟，不作为真实治理写入 |

2026-10-14 聚焦前端回归通过 3 项：显式 mock 才启用 demo、无 mock 时默认加载真实上下文、未知治理命令不创建对象会话。矩阵中的“真实对象会话写入”仅表示入口能力，不能替代每个命令的候选或 application 成功验收。复核入口为 `src/web/src/pages/catalog/RequirementCenterPage.tsx` 和 `src/web/src/requirement-center.test.tsx`。
