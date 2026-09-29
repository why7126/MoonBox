---
bug_id: BUG-0017-compose-container-name-suffix-one
title: 容器名不应自动追加 -1 后缀
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:12:05
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
iteration: sprint-007
openspec_changes:
  - change_id: fix-compose-container-name-suffix-one
    type: fix
    status: archived
lifecycle:
  captured: '2026-09-14 09:05:04'
  generated: '2026-09-14 10:23:08'
  completed: '2026-09-14 23:55:58'
  reviewed: '2026-09-15 00:02:11'
  approved: '2026-09-15 00:02:11'
related_requirement: null
related_bug: null
related_change: fix-compose-container-name-suffix-one
captured_via: capture
classification_rationale: 用户描述“容器名不要加 -1”，属于现有 Docker/Compose 命名表现与期望不一致，按缺陷采集。
severity: medium
---

# BUG-0017-compose-container-name-suffix-one Trace

## 来源与范围

来源为用户本次 `/capture` 输入。该条记录 Docker/Compose 容器命名偏差，已评审通过并纳入 `sprint-007`；OpenSpec Change `fix-compose-container-name-suffix-one` 已创建、实施并归档。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:12:05 | /opsx-archive | Change `fix-compose-container-name-suffix-one` 已归档，状态同步完成。 |
| 2026-09-15 00:28:22 | /opsx-apply | Change `fix-compose-container-name-suffix-one` apply 完成，后续已完成归档。 |
| 2026-09-15 00:27:33 | /opsx-apply | Change `fix-compose-container-name-suffix-one` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-15 00:20:11 | /opsx-apply | Change `fix-compose-container-name-suffix-one` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 23:57:09 | /bug-complete | BUG-0017-compose-container-name-suffix-one 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 09:05:04 | /capture | 创建采集记录，初判 medium；用户反馈容器名后缀与期望不一致，按 BUG 采集。 |
| 2026-09-14 10:23:08 | /bug-generate | 生成 bug.md，状态推进为 draft；根因、规避方案与验收仍待 /bug-complete 补齐。 |
| 2026-09-14 23:55:58 | /bug-complete | 补齐 root-cause、workaround、acceptance；根因证据门禁通过后进入 pending_review。 |
| 2026-09-15 00:02:11 | /bug-review | 评审通过，确认按常规 Sprint 纳入修复；下一步先执行 /sprint-propose。 |
| 2026-09-15 00:10:27 | /sprint-propose | 纳入 sprint-007；后续已执行 /bug-opsx 创建修复 Change。 |
| 2026-09-15 00:18:00 | /bug-opsx | 创建 OpenSpec Change `fix-compose-container-name-suffix-one`；下一步执行 /opsx-apply。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-17 08:12:05 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-compose-container-name-suffix-one
