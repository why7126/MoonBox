---
bug_id: BUG-0018-standalone-change-acceptance-source-unverified
title: 独立 Change 卡片误报验收来源待核实
status: captured
created_at: '2026-09-14 09:16:42'
updated_at: 2026-09-14 09:18:20
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
iteration: null
openspec_changes: []
lifecycle:
  captured: '2026-09-14 09:16:42'
  generated: null
  completed: null
  reviewed: null
  approved: null
related_requirement: REQ-0026-requirement-center-standalone-change-cards
related_bug: null
related_change: null
captured_via: capture
classification_rationale: 用户反馈的是已交付的需求中心独立 Change 卡片在验收中阶段展示“验收来源待核实：未找到交付验证记录”，而归档 Change 已存在验证记录与证据目录；属于既有能力与规格要求不一致，按缺陷采集。
severity: medium
---

# BUG-0018-standalone-change-acceptance-source-unverified Trace

## 来源与范围

来源为用户本次 `/capture` 输入及截图。该条记录需求中心独立 Change 卡片验收来源展示偏差，根因未确认，未评审、未纳入 Sprint、未创建 OpenSpec Change。

## 关联证据

| 类型 | 路径 | 说明 |
|---|---|---|
| 用户截图 | `issues/bugs/plan/BUG-0018-standalone-change-acceptance-source-unverified/screenshots/user-evidence-acceptance-source-unverified.png` | 展示独立 Change 卡片出现“验收来源待核实：未找到交付验证记录”。 |
| 相关已归档能力 | `add-requirement-center-change-visibility` | 作为问题背景和规格证据，不作为本 BUG 的修复 Change。 |
| 相关归档 Change 验证 | `openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md` | 相关能力归档验证记录入口。 |
| 相关归档 Change 证据 | `openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/` | 相关能力证据目录入口。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 09:16:42 | /capture | 创建采集记录，初判 medium；用户反馈独立 Change 卡片误报未找到交付验证记录，按 BUG 采集。 |
| 2026-09-14 09:18:20 | /capture | 修正采集元数据：相关已归档 Change 仅作为背景证据，不作为本 BUG 的修复 Change；状态恢复为 captured。 |
