---
bug_id: BUG-0019-requirement-center-issue-title-overridden
title: 需求中心阶段业务标题来源与文档中文标题校验追溯记录
status: done
created_at: '2026-09-14 10:25:53'
updated_at: 2026-09-29 14:18:37
related_requirement: null
related_bug: null
owner: 产品团队
source: explore
lifecycle_stage: archive
iteration: sprint-007
openspec_changes:
- change_id: fix-requirement-center-stage-business-titles
  type: fix
  status: archived
lifecycle:
  captured: '2026-09-14 10:25:53'
  generated: 2026-09-14 11:02:20
  completed: '2026-09-15 22:56:33'
  reviewed: '2026-09-15 22:58:59'
  approved: '2026-09-15 22:58:59'
related_change: fix-requirement-center-stage-business-titles
severity: medium
---

# 需求中心阶段业务标题来源与文档中文标题校验追溯记录

## 来源与范围

用户授权 /bug-capture；承接前序 /explore 的两个样本与代码路径验证。范围为 REQ/BUG 卡片主标题，不把回归样本视为本 BUG 的父需求或因果关联 BUG。已评审批准，未纳入 Sprint、未创建修复 Change。

## 证据入口

- review.md：批准结论与实施边界。

- bug.md：缺陷主文档。
- root-cause.md：confirmed 根因、六条证据与当前归档样本函数复核。
- workaround.md：按 ID 核对的临时规避及限制。
- acceptance.md：十三项修复自验已完成，用户验收待确认；证据见关联Change verification.md。

- capture.md：复现步骤、期望/实际、源码证据与建议验收。
- issues/bugs/_registry.yaml、issues/requirements/_registry.yaml：正确业务标题。
- src/backend/app/governance/change_index.py：中文标题回退与唯一 Change 选择。
- src/web/src/pages/catalog/RequirementCenterPage.tsx：主标题覆盖表达式。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-29 14:18:37 | /opsx-archive | Change `fix-requirement-center-stage-business-titles` 已归档，状态同步完成。 |
| 2026-09-15 23:34:06 | /opsx-apply | Change `fix-requirement-center-stage-business-titles` apply 完成，待 archive。 |
| 2026-09-15 23:33:58 | /opsx-apply | Change `fix-requirement-center-stage-business-titles` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-15 23:07:06 | /opsx-apply | Change `fix-requirement-center-stage-business-titles` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-15 22:56:33 | /bug-complete | BUG-0019-requirement-center-issue-title-overridden 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 11:02:20 | /bug-generate | BUG-0019-requirement-center-issue-title-overridden 已生成 bug.md，状态同步为 draft。 |
| 2026-09-14 10:25:53 | /bug-capture | 创建单条采集记录，严重度 medium，承接两个已核实标题异常样本。 |
| 2026-09-14 11:02:20 | /bug-generate | 生成 bug.md，状态推进为 draft；保留两个异常样本、证据边界与九阶段标题一致性范围。 |
| 2026-09-14 11:05:00 | /bug-complete | 进入 enriching，补齐根因、规避和验收资料；待根因门禁通过后推进待评审。 |
| 2026-09-14 11:05:12 | /bug-complete | 根因门禁通过：confirmed，6 条证据；资料完善完成，推进 pending_review，修复验收仍待执行。 |
| 2026-09-15 22:56:10 | /bug-complete | 依据用户新规则重写阶段来源与全体文档中文标题生成校验要求；旧统一 Issue 标题方案失效，进入 enriching 复核。 |
| 2026-09-15 22:56:33 | /bug-complete | 修订后根因门禁通过，6 条证据；恢复 pending_review，13 项验收待执行。 |
| 2026-09-15 22:58:59 | /bug-review --approve | 用户批准最新阶段标题与全生成文档中文标题范围，保持 medium，等待纳入 Sprint。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-09-29 14:18:37 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive BUG-0019-requirement-center-issue-title-overridden
