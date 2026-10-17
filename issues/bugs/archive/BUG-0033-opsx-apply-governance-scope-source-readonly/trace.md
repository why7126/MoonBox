---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 误授治理写权限导致源码只读追溯记录
status: done
created_at: 2026-10-06 22:22:15
updated_at: 2026-10-12 23:44:08
owner: 产品团队
source: 用户反馈与只读代码定位
lifecycle_stage: archive
iteration: sprint-008
related_requirement:
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
related_change: fix-opsx-apply-governance-scope-source-readonly
openspec_changes:
  - change_id: fix-opsx-apply-governance-scope-source-readonly
    type: fix
    status: archived
lifecycle:
  captured: 2026-10-06 22:22:15
  generated: 2026-10-06 22:28:03
  completed: 2026-10-07 13:07:35
  reviewed: 2026-10-07 13:11:12
  approved: 2026-10-07 13:11:12
severity: high
---

# 产品内执行 opsx-apply 误授治理写权限导致源码只读追溯记录

## 当前摘要

用户报告产品内 `/opsx-apply` 对已纳入 Sprint 的 Change 误用治理写权限，导致源码只读。原失败对象为 BUG-0029；原 turn 实际使用 `moonbox-governance`，原 Change 的 bug_id/iteration 与策略要求的 bug/sprint 不匹配。Firefox 原会话与完整策略内存对照确认字段不兼容导致权限回退，根因现为 confirmed。原轮次服务端 reason_code 未持久化，后续修复验收须补齐脱敏决策留痕。

## 重复/相似检查

BUG-0026 同属产品内 Chat 执行权限问题，但针对 `/opsx-archive` 归档写入和未知状态。用户确认本问题独立新建并关联 BUG-0026。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-12 23:44:08 | /opsx-archive | Change `fix-opsx-apply-governance-scope-source-readonly` 已归档，状态同步完成。 |
| 2026-10-12 23:40:30 | /opsx-accept | Change `fix-opsx-apply-governance-scope-source-readonly` 自动验收结论已同步，按证据清单判断归档就绪。 |
| 2026-10-07 17:30:23 | /opsx-apply | Change `fix-opsx-apply-governance-scope-source-readonly` apply 完成，待 archive。 |
| 2026-10-07 16:55:05 | /opsx-apply | Change `fix-opsx-apply-governance-scope-source-readonly` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-07 16:47:37 | /opsx-apply | Change `fix-opsx-apply-governance-scope-source-readonly` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-07 13:11:12 | /bug-review | approved | 根因与回归范围评审通过，确认修复；修复验收未执行，下一步纳入 Sprint。 |
| 2026-10-07 13:07:35 | /bug-complete | pending_review | 已完成文档补齐。 |
| 2026-10-07 13:06:00 | /bug-complete 浏览器与策略补证 | enriching | E21–E22：当前原会话的完整策略正反对照确认字段不兼容导致治理写权限回退；历史 reason_code 未留存。 |
| 2026-10-07 12:25:30 | /bug-complete 权限补证 | enriching | E17–E20：原执行器 profile 直接确认为 moonbox-governance；新增 AC-011 权限决策留痕与 reason_code 复核，根因仍 probable。 |
| 2026-10-06 22:48:47 | /bug-complete 自动取证 | enriching | E13–E16：原 turn、Issue 快照和当时 Change 字段已取得；决策/profile 未记录或未检得，根因仍 probable。 |
| 2026-10-06 22:43:26 | /bug-complete 对象补证 | enriching | E12：用户确认原失败对象为 BUG-0029；根因保持 probable，完成时间不变。 |
| 2026-10-06 22:38:46 | /bug-complete 进一步补证 | enriching | 新增 E8–E11：实际治理文件 4 个内存对照通过，根因提升为 probable，未确认原失败 turn，未执行完成态同步。 |
| 2026-10-06 22:32:47 | /bug-complete 草稿保存 | enriching | 根因未确认，保存补证清单与验收草稿；不执行完成态同步，保留 lifecycle.completed 原值。 |
| 2026-10-06 22:28:03 | /bug-generate | draft | 已生成 bug.md，完成合成验证，运行态根因待补证。 |
| 2026-10-06 22:22:15 | bug.capture | captured | 依据用户反馈记录独立缺陷；严重度暂定 high，运行态原因待核查。 |

## 补证与阶段门禁

根因状态为 confirmed，证据见 root-cause.md；已完成 bug.complete 工作流同步，当前评审已通过，状态为 approved。验收草稿为 pending，修复后的产品行为验收尚未执行。原轮次 reason_code 未持久化，已纳入 AC-011；capture 和其他对象未修改。
- 阶段迁移：plan → review（/bug-review --approve）
- 2026-10-12 23:44:08 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-opsx-apply-governance-scope-source-readonly
