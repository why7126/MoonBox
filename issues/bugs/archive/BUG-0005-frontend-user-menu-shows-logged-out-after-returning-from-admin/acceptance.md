---
bug_id: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
acceptance_status: passed
created_at: 2026-08-11 18:32:00
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-BUG-0005-001 加载期间保持已登录用户展示

WHEN 用户已登录并从后台返回前台需求中心
AND 需求中心上下文接口仍在加载
THEN 前台用户菜单栏不得显示“未登录”
AND SHOULD 使用本地前台 session 或后台 session 中的已知用户名作为稳定兜底展示

## AC-BUG-0005-002 上下文加载成功后展示接口用户

WHEN 需求中心上下文接口返回当前用户信息
THEN 用户菜单栏应展示接口返回的当前用户名称、头像和后台访问权限
AND 不应因为本地兜底 session 覆盖接口中的真实权限

## AC-BUG-0005-003 鉴权失败时清理半登录状态

WHEN 需求中心上下文接口返回 `401` 或 `403`
THEN 系统应清理前台 session 与后台 session
AND 应跳转到 `/login` 或展示一致的登录失效处理
AND 不应继续停留在显示“未登录”的半登录前台页面

## AC-BUG-0005-004 回归测试覆盖

WHEN 运行前端测试
THEN 应覆盖从后台返回前台时上下文接口 pending 的用户菜单展示
AND 应覆盖上下文接口 `401/403` 时 session 清理与登录跳转
AND 既有前台登录、进入后台、退出登录和修改密码流程不得回归

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-frontend-user-menu-session-state
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

