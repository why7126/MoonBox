---
change_id: fix-frontend-user-menu-change-password
status: applied
created_at: 2026-08-11 17:37:04
updated_at: 2026-08-12 13:43:11
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
---

# Tasks

- [x] 1. 前端交互修复
  - [x] 1.1 抽取或复用后台修改密码弹窗与密码输入显示/隐藏组件。
  - [x] 1.2 在前台需求中心维护修改密码弹窗打开状态。
  - [x] 1.3 给前台用户菜单“修改密码”绑定点击行为，关闭菜单并打开弹窗。
  - [x] 1.4 确认空间切换浮层、主题切换、进入后台和退出登录交互不受影响。

- [x] 2. 会话与错误处理
  - [x] 2.1 前台提交成功后调用既有 `/api/v1/admin/auth/change-password`。
  - [x] 2.2 成功后清理 `moonbox.admin.session` 与 `moonbox.frontend.session`，跳转 `/login`。
  - [x] 2.3 接口失败时保持弹窗打开，展示错误提示且不清理会话。
  - [x] 2.4 新密码确认不一致时阻止提交，不发起 API 请求。

- [x] 3. 回归测试
  - [x] 3.1 在 `requirement-center.test.tsx` 覆盖前台菜单点击打开修改密码弹窗。
  - [x] 3.2 覆盖前台改密成功请求体、授权头、会话清理和 `/login` 跳转。
  - [x] 3.3 覆盖接口失败和确认密码不一致场景。
  - [x] 3.4 保持 `admin-auth.test.tsx` 或后台相关测试覆盖后台修改密码不回归。
  - [x] 3.5 运行 `pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run`。
  - [x] 3.6 运行 `pnpm --dir src/web build`。

- [x] 4. 文档与追溯
  - [x] 4.1 回填 BUG acceptance 验收结果与证据。
  - [x] 4.2 回填 Change trace、Sprint acceptance-report 和 release-note。
  - [x] 4.3 评估是否需要沉淀 `docs/knowledge-base/incidents/`；若无复用价值，在 trace 中说明不适用。

## 验收返修记录

### 2026-08-11 18:00:31 前台改密弹窗样式不可读

- 反馈：前台点击用户菜单“修改密码”后，弹窗文字和输入框对比度异常，几乎看不清楚，无法填写。
- 根因：前台复用后台 `ChangePasswordModal`，但后台弹窗样式依赖 `.admin-shell` 作用域内的 `--admin-*` 变量；前台页面只有 `.requirement-center` 的 `--rc-*` 变量。
- 调整：在 `.requirement-center .admin-modal-backdrop` 下桥接弹窗所需 `--admin-*` 变量到 `--rc-*` token，保持后台页面原主题不受影响。
- 测试：补充 `requirement-center.test.tsx` 样式桥接守护，防止前台复用后台弹窗时变量缺失。
- 视觉验收：1440px 打开前台修改密码弹窗并填写当前密码，computed style 显示输入文字 `rgb(231, 232, 243)`、背景 `rgb(14, 16, 35)`、边框 `rgba(234, 242, 255, 0.18)`，截图 `/tmp/moonbox-bug0004-change-password-readable-1440.png`。

### 2026-08-11 23:49:27 前台普通用户改密提示登录失效

- 反馈：前台普通用户只有 `moonbox.frontend.session`、没有 `moonbox.admin.session` 时，修改密码提示“登录已失效，请重新登录”。
- 根因：`ChangePasswordModal` 复用的 `changeAdminPassword()` 只读取 `moonbox.admin.session.access_token`，但前台登录成功后普通用户只保留 frontend session token。
- 调整：`changeAdminPassword()` 在没有 admin token 时回退读取 `moonbox.frontend.session.access_token`，继续调用既有 `/api/v1/admin/auth/change-password`。
- 测试：补充普通前台用户仅有 frontend token 的改密成功回归，验证请求携带 `Bearer front-token`，成功后清理前后台 session 并跳转 `/login`。

### 2026-08-12 00:00:17 前台普通用户改密提示需要后台管理员权限

- 反馈：前台普通用户携带 frontend session token 调用 `/api/v1/admin/auth/change-password` 时，后端返回“需要后台管理员权限。”。
- 根因：后端路由依赖 `require_admin_user`，仓储层 `change_own_password()` 也要求用户角色为“后台管理员”。
- 调整：`/change-password` 改用 `require_session_user`；`change_own_password()` 只要求当前用户存在且状态为“正常”，不再要求后台管理员角色。
- 权限边界：后台用户管理、后台个人资料等其它管理接口仍保持后台管理员权限要求。
- 测试：补充/扩展后端集成测试，覆盖前台普通用户改密成功、旧 session 失效、新密码可登录，并继续无法访问 `/api/v1/admin/users`。

### 2026-08-12 13:43:11 旧接口错误与当前字段错误同时展示

- 反馈：修改密码弹窗中，上一次接口错误会在用户修改输入后继续保留，导致与当前字段校验错误同时显示。
- 根因：弹窗提交级 `error` 状态只在提交前清空；三个密码输入框变化时只更新字段值，没有清理旧接口错误。
- 调整：新增统一字段更新函数，任一密码字段变化时清理旧提交级错误。
- 测试：补充前台回归，先触发“当前密码不正确”，再将确认密码改为不一致，验证仅显示“两次输入的新密码不一致。”，旧接口错误不再显示。
