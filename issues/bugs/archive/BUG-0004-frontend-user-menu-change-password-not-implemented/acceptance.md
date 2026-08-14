---
bug_id: BUG-0004-frontend-user-menu-change-password-not-implemented
acceptance_status: passed
created_at: 2026-08-11 16:12:20
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 回归验收

### AC-001 前台菜单点击打开修改密码弹窗

WHEN 用户已登录前台并进入 `/requirements`
AND 用户打开左侧底部用户菜单
AND 点击“修改密码”
THEN 系统应关闭用户菜单
AND 打开标题为“修改密码”的弹窗
AND 弹窗应包含“当前密码”“新密码”“确认新密码”三个输入项。

### AC-002 前台修改密码提交调用既有接口

WHEN 用户在前台修改密码弹窗填写当前密码、新密码和确认新密码
AND 两次新密码一致
AND 点击“更新密码”
THEN 系统应调用 `/api/v1/admin/auth/change-password`
AND 请求体应包含 `current_password`、`new_password`、`confirm_password`
AND 请求应携带当前 admin token 的 Bearer 授权头。

### AC-003 前台修改密码成功后清理完整会话

WHEN 前台修改密码接口返回成功
THEN 系统应清理 `moonbox.admin.session`
AND 系统应清理 `moonbox.frontend.session`
AND 浏览器地址应跳转到 `/login`
AND 用户需要重新登录后才能回到前台需求中心。

### AC-004 前台修改密码失败保留弹窗与错误提示

WHEN 前台修改密码接口返回错误
THEN 修改密码弹窗应保持打开
AND 已填写内容不应被静默清空
AND 页面应展示接口返回的错误信息或默认失败提示
AND 不应清理当前会话。

### AC-005 密码确认不一致时不发起请求

WHEN 用户填写的新密码和确认新密码不一致
AND 点击“更新密码”
THEN 系统应展示“两次输入的新密码不一致”
AND 不应调用 `/api/v1/admin/auth/change-password`。

### AC-006 后台修改密码流程保持不回归

WHEN 用户进入后台用户管理页
AND 通过后台用户菜单点击“修改密码”
THEN 后台仍应打开修改密码弹窗
AND 成功后清理后台会话并回到登录页。

### AC-007 前台修改密码弹窗样式可读可填写

WHEN 用户在前台需求中心打开“修改密码”弹窗
THEN 弹窗标题、说明、字段标签、输入框内容、输入框边框、光标和按钮应清晰可见
AND 用户应能够正常聚焦并填写“当前密码”“新密码”“确认新密码”
AND 前台复用后台弹窗时不应因缺少 `.admin-shell` 主题变量导致颜色不可读。

### AC-008 前台普通用户使用 frontend session 修改密码

WHEN 前台普通用户已登录并只有 `moonbox.frontend.session.access_token`
AND 本地不存在 `moonbox.admin.session`
AND 用户在前台修改密码弹窗提交当前密码、新密码和确认新密码
THEN 系统应使用 frontend session token 调用 `/api/v1/admin/auth/change-password`
AND 请求授权头应为 `Bearer <frontend access_token>`
AND 不应展示“登录已失效，请重新登录”
AND 成功后应清理 `moonbox.frontend.session` 与 `moonbox.admin.session`
AND 浏览器地址应跳转到 `/login`。

### AC-009 后端自助改密不要求后台管理员角色

WHEN 前台普通用户携带有效 Bearer token 调用 `/api/v1/admin/auth/change-password`
THEN 后端应允许状态为“正常”的当前登录用户修改自己的密码
AND 不应返回“需要后台管理员权限。”
AND 成功后应撤销该用户既有会话
AND 该用户使用新密码可重新登录
AND 该用户仍不应访问 `/api/v1/admin/users` 等后台管理接口。

### AC-010 修改输入后清理旧提交错误

WHEN 修改密码接口曾返回“当前密码错误”等提交级错误
AND 用户继续修改任一密码输入项
THEN 系统应清理旧提交级错误
AND 若当前输入存在字段级错误，应只展示当前字段级错误
AND 不应同时展示旧接口错误与当前字段级错误。

## 测试建议

- 在 `src/web/src/requirement-center.test.tsx` 增加前台用户菜单“修改密码”点击、表单校验、接口请求、成功跳转和会话清理测试。
- 保留或补充后台 `src/web/src/admin-auth.test.tsx` 修改密码回归，避免组件抽取后破坏后台流程。
- 覆盖失败响应与新密码确认不一致场景，确保不会误清理会话。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-frontend-user-menu-change-password
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

