---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: done
review_result: approved
reviewed_at: 2026-09-14 11:48:38
reviewer: 产品团队
severity: medium
created_at: 2026-09-14 11:48:38
updated_at: 2026-09-14 13:12:02
---

# 缺陷评审

## 评审结论

批准修复。

## 评审清单

| 项目 | 结论 | 说明 |
|---|---|---|
| 可复现或根因充分 | 通过 | `root-cause.md` 为 confirmed，证据链 5 条；受控运行证明 `req.complete` 聚焦事件仍派生 `draft`。 |
| 严重等级合理 | 通过 | medium；影响需求治理状态投影和需求中心漂移判断，未见数据丢失、权限越界或核心业务不可用证据。 |
| 回归验收明确 | 通过 | `acceptance.md` 已列 7 项 AC，覆盖 `draft/enriching -> pending_review`、registry / CHANGELOG 同步、幂等和同域 BUG 流程评估。 |
| hotfix 路径 | 不需要 | 该缺陷影响治理一致性与工作流体验，适合常规 Sprint 修复；暂无 P0/P1 热修证据。 |

## 风险与注意事项

- 后续修复必须先纳入 Sprint，再创建 OpenSpec Change；不得从 approved 直接进入 `/bug-opsx`。
- 修复时需同时评估 `bug.complete -> pending_review` 是否存在同类缺口，避免只修 REQ 链路。
- 验收时需确认需求中心当前态卡片不再误报数据漂移。

## 下一步

`/sprint-propose --bug BUG-0020-req-complete-status-projection-drift`
