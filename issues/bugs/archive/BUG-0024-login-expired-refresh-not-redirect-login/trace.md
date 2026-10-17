---
bug_id: BUG-0024-login-expired-refresh-not-redirect-login
title: 登录失效时，页面刷新也没有重新定位到登录页追溯记录
status: done
created_at: '2026-09-16 20:00:07'
updated_at: 2026-10-04 23:50:26
owner: user_f694abc671d548b48d9eb897f720ba4d
source: capture
lifecycle_stage: archive
captured_via: capture
capture_source:
  task_id: cb427af3-3122-4350-abca-3ad3abef8d28
  candidate_id: 3091f068-0367-45f3-80bb-70752fcba993
  revision: 33
  initial_type: bug
  final_type: bug
  adjusted_fields: []
  parents: []
classification_rationale: 用户反馈登录失效后刷新页面仍未跳转到登录页，属于登录态失效处理的疑似缺陷。暂按 medium 记录，具体页面、登录失效条件、复现路径和影响范围仍需补证确认。
iteration: sprint-008
openspec_changes:
  - change_id: fix-chat-auth-expired-redirect-login
    type: fix
    status: archived
lifecycle:
  captured: '2026-09-16 20:00:07'
  generated: 2026-09-29 20:03:13
  completed: 2026-09-30 17:04:51
  reviewed: 2026-09-30 17:11:01
  approved: 2026-09-30 17:11:01
related_requirement: null
related_bug: null
related_change: fix-chat-auth-expired-redirect-login
severity: medium
---

# 登录失效时，页面刷新也没有重新定位到登录页追溯记录

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-04 23:50:26 | /opsx-archive | Change `fix-chat-auth-expired-redirect-login` 已归档，状态同步完成。 |
| 2026-10-04 12:47:38 | /opsx-apply | Change `fix-chat-auth-expired-redirect-login` apply 完成，待 archive。 |
| 2026-10-04 12:46:51 | /opsx-apply | Change `fix-chat-auth-expired-redirect-login` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-04 11:27:52 | /opsx-apply | Change `fix-chat-auth-expired-redirect-login` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-04 11:24:01 | /bug-opsx | in_sprint | 创建 OpenSpec Change `fix-chat-auth-expired-redirect-login`；下一步执行 /opsx-apply。 |
| 2026-09-30 17:11:01 | /bug-review | approved | 根因门禁通过，medium，正常迭代修复；待纳入 Sprint，尚未修复验收。 |
| 2026-09-30 17:06:47 | /bug-complete | pending_review | BUG-0024-login-expired-refresh-not-redirect-login 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-30 17:04:51 | /bug-complete | pending_review | 根据用户补充截图与 Network 401 响应确认根因，补齐 root-cause、workaround、acceptance 与 trace，进入待评审。 |
| 2026-09-30 15:20:25 | /bug-complete 草稿补齐 | enriching | 保存根因假设、补证清单、临时方案及验收草稿；保留 lifecycle.completed 原值，未执行完成态同步。 |
| 2026-09-29 20:03:13 | /bug-generate | BUG-0024-login-expired-refresh-not-redirect-login 已生成 bug.md，状态同步为 draft。 |
| 2026-09-29 15:25:18 | trace.fix | captured | 根据用户授权将 BUG-0024-login-expired-refresh-not-redirect-login 事实源标题与现象改为登录失效刷新未跳转登录页 |
| 2026-09-16 20:00:07 | capture | captured | 需求中心创建并持久化 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-10-04 23:50:26 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-chat-auth-expired-redirect-login
