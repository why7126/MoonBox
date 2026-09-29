---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: done
created_at: '2026-09-14 11:33:24'
updated_at: 2026-09-14 13:11:57
related_requirement: REQ-0029-capture-multimodal-candidate-review
related_bug: null
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
iteration: sprint-006
openspec_changes:
  - change_id: fix-req-complete-status-projection-drift
    status: archived
lifecycle:
  captured: '2026-09-14 11:33:24'
  generated: 2026-09-14 11:38:40
  completed: 2026-09-14 11:42:05
  reviewed: 2026-09-14 11:48:38
  approved: 2026-09-14 11:48:38
related_change: fix-req-complete-status-projection-drift
severity: medium
---

# BUG-0020-req-complete-status-projection-drift Trace

## 来源与范围

用户通过 `/bug-capture` 反馈：`/req-complete` 后 REQ 状态投影可能残留 `draft` / `enriching` 数据漂移。样本为 REQ-0029，现象涉及 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 和需求中心当前态看板的一致性。

本次仅记录缺陷，不修改同步脚本、需求文档、前端或测试；根因、修复范围和验收细节待 `/bug-explore` 与后续缺陷完善确认。

## 证据入口

- capture.md：用户报告的 REQ-0029 状态漂移现象、期望与建议验收。
- bug.md：缺陷主文档。
- root-cause.md：confirmed 根因、证据链与修复方向。
- workaround.md：正式修复前的聚焦同步与人工核对规避。
- acceptance.md：7 项回归验收标准。
- `rules/requirement-management.md:91-94`：`/req-complete` 目标状态规范。
- `.agents/skills/req-complete/SKILL.md:88-95`：`enriching -> pending_review` 命令语义。
- `scripts/workflow_sync/engine.py:332-335`：当前事件目标表缺少 `req.complete`。
- `tests/unit/test_workflow_sync_engine.py:134-177`：现有 generate 覆盖样本，缺少 complete 同类覆盖。
- 受控运行：内存 REQ `trace_status='draft'` 执行 `SyncEngine().run(event='req.complete')` 后派生状态为 `draft`。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 13:11:57 | /opsx-archive | Change `fix-req-complete-status-projection-drift` 已归档，状态同步完成。 |
| 2026-09-14 12:16:41 | /opsx-apply | Change `fix-req-complete-status-projection-drift` apply 完成，待 archive。 |
| 2026-09-14 11:38:08 | /bug-generate | BUG-0020-req-complete-status-projection-drift 已生成 bug.md，状态同步为 draft。 |
| 2026-09-14 11:33:24 | /bug-capture | 创建单条采集记录，严重度 medium，关联样本 REQ-0029，待补证 req.complete 状态传播与回归覆盖缺口。 |
| 2026-09-14 11:42:05 | /bug-complete | 根因门禁通过：confirmed，5 条证据；补齐 root-cause、workaround、acceptance，状态推进 pending_review。 |
| 2026-09-14 11:48:38 | /bug-review | 评审通过，根因证据门禁已过，严重等级 medium，下一步纳入 Sprint。 |
| 2026-09-14 12:05:36 | /bug-opsx | 创建 OpenSpec Change `fix-req-complete-status-projection-drift`，并回填 sprint-006。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-14 13:11:57 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-req-complete-status-projection-drift
