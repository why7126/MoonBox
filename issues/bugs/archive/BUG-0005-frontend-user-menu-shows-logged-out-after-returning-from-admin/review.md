---
bug_id: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
review_result: approved
created_at: 2026-08-11 18:40:00
updated_at: 2026-08-11 18:40:00
reviewer: user
---

# 缺陷评审

## 评审结论

确认修复。该缺陷会导致前台用户菜单在从后台返回前台时短暂或持续显示“未登录”，属于登录态展示与鉴权状态不同步问题。

## 评审清单

- [x] 可复现或根因充分
- [x] 严重等级合理
- [x] 回归验收明确
- [x] 是否需 hotfix 路径

## 严重等级

维持 `medium`。问题不直接造成数据损坏，也不必然阻断需求中心主流程；但会破坏用户对登录态、账号状态和权限入口的判断，应进入常规修复流程。

## Hotfix 判断

暂不走 hotfix。建议纳入最近 Sprint，通过常规 OpenSpec fix 变更修复并补充前端回归测试。

## 后续动作

评审通过后必须先执行 `/sprint-propose --bug BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin` 纳入 Sprint；纳入 Sprint 后再执行 `/bug-opsx BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin`。
