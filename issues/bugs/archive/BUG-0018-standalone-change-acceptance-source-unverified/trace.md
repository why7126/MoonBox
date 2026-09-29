---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
status: done
created_at: '2026-09-14 09:16:42'
updated_at: 2026-09-17 08:12:45
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
iteration: sprint-006
openspec_changes:
  - change_id: fix-standalone-change-acceptance-source
    type: fix
    status: archived
lifecycle:
  captured: '2026-09-14 09:16:42'
  generated: '2026-09-14 10:20:38'
  completed: '2026-09-14 10:23:16'
  reviewed: '2026-09-14 11:03:16'
  approved: '2026-09-14 11:03:16'
related_requirement: REQ-0026-requirement-center-standalone-change-cards
related_bug: null
related_change: fix-standalone-change-acceptance-source
captured_via: capture
classification_rationale: 用户反馈的是已交付的需求中心独立 Change 卡片在验收中阶段展示“验收来源待核实：未找到交付验证记录”，而归档 Change 已存在验证记录与证据目录；属于既有能力与规格要求不一致，按缺陷采集。
severity: medium
---

# BUG-0018-standalone-change-acceptance-source-unverified Trace

## 来源与范围

来源为用户 `/capture` 输入、截图及后续 `/explore` 复核。该条记录需求中心独立 Change 卡片验收来源展示偏差；已评审通过并纳入 `sprint-006`，修复 Change 为 `fix-standalone-change-acceptance-source`。

## 关联证据

| 类型 | 路径 | 说明 |
|---|---|---|
| 用户截图 | `issues/bugs/archive/BUG-0018-standalone-change-acceptance-source-unverified/screenshots/user-evidence-acceptance-source-unverified.png` | 展示独立 Change 卡片出现“验收来源待核实：未找到交付验证记录”。 |
| 相关已归档能力 | `add-requirement-center-change-visibility` | 作为问题背景和规格证据，不作为本 BUG 的修复 Change。 |
| 相关归档 Change 验证 | `openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md` | 相关能力归档验证记录入口。 |
| 相关归档 Change 证据 | `openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/` | 相关能力证据目录入口。 |
| 后续复现 Change | `openspec/archive/2026-09-14-enhance-workflow-sync-current-status-block/trace.md` | trace 中存在 `## Validation Log` 验证记录，但卡片仍提示未找到交付验证记录；并入本 BUG 修复范围。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-17 08:12:45 | /opsx-archive | Change `fix-standalone-change-acceptance-source` 已归档，状态同步完成。 |
| 2026-09-15 00:16:20 | /opsx-apply | Change `fix-standalone-change-acceptance-source` apply 完成，待 archive。 |
| 2026-09-15 00:16:12 | /opsx-apply | Change `fix-standalone-change-acceptance-source` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-15 00:09:27 | /opsx-apply | Change `fix-standalone-change-acceptance-source` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 09:16:42 | /capture | 创建采集记录，初判 medium；用户反馈独立 Change 卡片误报未找到交付验证记录，按 BUG 采集。 |
| 2026-09-14 09:18:20 | /capture | 修正采集元数据：相关已归档 Change 仅作为背景证据，不作为本 BUG 的修复 Change；状态恢复为 captured。 |
| 2026-09-14 10:20:38 | /bug-generate | 生成 bug.md，状态推进为 draft；保留“验证摘要标题识别”作为待验证线索。 |
| 2026-09-14 10:23:16 | /bug-complete | 补齐 root-cause、workaround、acceptance；根因证据门禁通过，状态推进为 pending_review。 |
| 2026-09-14 11:03:16 | /bug-review --approve | 评审通过，确认修复；等待纳入 Sprint。 |
| 2026-09-14 15:40:08 | /bug-complete | 并入 `enhance-workflow-sync-current-status-block` 复现范围，补充 `Validation Log` 验收来源识别验收项；状态保持 approved。 |
| 2026-09-15 00:04:31 | /bug-opsx | 生成 `fix-standalone-change-acceptance-source`，回填 Sprint 与父需求追溯。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-17 08:12:45 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-standalone-change-acceptance-source
