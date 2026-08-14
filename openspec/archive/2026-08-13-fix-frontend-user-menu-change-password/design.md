---
change_id: fix-frontend-user-menu-change-password
status: applied
created_at: 2026-08-11 17:37:04
updated_at: 2026-08-12 13:43:11
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
---

# 技术设计

## 根因

前台需求中心用户菜单中的“修改密码”按钮只绑定了悬停关闭空间浮层逻辑，没有绑定点击处理函数。后台已经实现 `ChangePasswordModal` 和 `changeAdminPassword`，但该弹窗能力没有以可复用方式提供给前台页面。

## 修复方案

1. 抽取或复用后台修改密码弹窗和密码输入显示/隐藏组件，使前台需求中心可使用同一交互与校验口径。
2. 在前台需求中心新增修改密码弹窗状态。
3. 给前台用户菜单“修改密码”绑定点击处理：关闭用户菜单和空间浮层，打开修改密码弹窗。
4. 弹窗提交复用 `changeAdminPassword(currentPassword, newPassword, confirmPassword)`；该方法优先使用 `moonbox.admin.session.access_token`，没有 admin session 时回退使用 `moonbox.frontend.session.access_token`。
5. 成功后清理前台 session 与后台 admin session，并导航到 `/login`。
6. 失败时保留弹窗，展示接口错误或默认错误，不清理任何会话。
7. 后台用户管理页继续使用同一弹窗能力，保持成功后重新登录的既有行为。
8. 前台复用后台改密弹窗时，必须在 `.requirement-center` 作用域下桥接后台弹窗所需 `--admin-*` 变量到前台 `--rc-*` 设计 token，确保弹窗文字、输入框背景、边框、光标和主按钮在前台主题内可读可填写。
9. 提交级接口错误必须在用户继续编辑任一密码字段时清空，字段级错误优先反映当前输入状态，避免旧接口错误和当前字段校验错误叠加。

## 会话边界

| 场景 | 期望 |
|---|---|
| 前台改密成功 | 清理 `moonbox.admin.session` 与 `moonbox.frontend.session`，进入 `/login` |
| 前台改密失败 | 不清理任何会话，弹窗保持打开 |
| 新密码确认不一致 | 不发起 API 请求，不清理任何会话 |
| 后台改密成功 | 保持既有后台重新登录行为 |
| 前台普通用户改密 | 没有 `moonbox.admin.session` 时使用 `moonbox.frontend.session.access_token` 调用改密接口 |

## API 与权限

本 Change 不新增 API，不修改数据库。前台继续调用既有 `/api/v1/admin/auth/change-password`，并沿用当前后端密码强度、当前密码校验和会话失效规则。

`/api/v1/admin/auth/change-password` 是当前登录用户的自助改密接口，必须允许任意状态为“正常”的登录用户修改自己的密码；它不应要求后台管理员角色。后台用户管理、后台个人资料和其它管理接口继续使用后台管理员权限，不随本 Change 放开。

## 测试策略

- 前端测试覆盖前台用户菜单点击“修改密码”打开弹窗。
- 前端测试覆盖新密码确认不一致不发起请求。
- 前端测试覆盖前台提交成功调用 `/api/v1/admin/auth/change-password`，并清理前后台 session、跳转 `/login`。
- 前端测试覆盖普通前台用户仅有 `moonbox.frontend.session.access_token` 时，改密请求使用 frontend token，且不提示“登录已失效”。
- 后端集成测试覆盖前台普通用户 token 调用 `/api/v1/admin/auth/change-password` 成功，并确认该用户继续无法访问 `/api/v1/admin/users`。
- 前端测试覆盖接口失败时保留弹窗和会话。
- 前端测试覆盖接口失败后继续编辑任一密码字段会清理旧提交级错误，仅保留当前字段级错误。
- 后台修改密码测试保持通过，确认弹窗复用不破坏后台流程。
- 前端样式测试覆盖前台作用域下的后台弹窗 token 桥接。
- 1440px 关键交互验收覆盖前台打开修改密码弹窗后的输入框 computed style 与截图。

## 风险

- 如果直接复制后台弹窗而非抽取，可能造成前后台改密规则分叉。
- 如果 `changeAdminPassword` 只清理后台 session，前台 session 可能残留并绕过 `/requirements` 路由保护。
- 如果成功后先弹 toast 再跳转，可能出现短暂停留或旧状态闪烁；实现应以会话清理和路由跳转为主。
- 如果前台直接复用后台弹窗但缺少 `.admin-shell` 主题变量，可能出现文字、输入框或按钮对比度异常；实现必须在前台页面作用域补齐变量桥接。

## 文档同步

本 Change 不改变 API、数据库、部署或安全长期文档。若实现阶段改变共享组件边界或前台登录/会话策略，应在 Change trace 中说明是否需要同步长期文档；否则记录“不适用”原因。
