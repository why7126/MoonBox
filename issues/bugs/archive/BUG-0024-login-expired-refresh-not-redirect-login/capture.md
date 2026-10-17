---
bug_id: BUG-0024-login-expired-refresh-not-redirect-login
title: 登录失效时，页面刷新也没有重新定位到登录页
status: done
created_at: '2026-09-16 20:00:07'
updated_at: 2026-10-04 23:50:44
owner: user_f694abc671d548b48d9eb897f720ba4d
source: capture
lifecycle_stage: plan
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
severity: medium
---

# 登录失效时，页面刷新也没有重新定位到登录页

## 现象

登录失效时，页面刷新也没有重新定位到登录页。

## 补充说明

期望登录失效后刷新页面能够跳转到登录页。用户反馈实际刷新后仍未跳转；根因已在 root-cause.md 依据截图、Network 401 响应和代码路径确认为 Chat 工作台 401 处理未统一清理会话并跳转登录页。
