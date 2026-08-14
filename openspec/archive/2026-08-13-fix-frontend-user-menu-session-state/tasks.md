---
change_id: fix-frontend-user-menu-session-state
status: applied
created_at: 2026-08-11 18:55:00
updated_at: 2026-08-11 19:05:00
source_bug: BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin
---

# Tasks

- [x] 1. 前台用户展示兜底
  - [x] 1.1 在需求中心初始化用户展示时读取本地前台 session。
  - [x] 1.2 必要时从后台 admin session 派生已知用户名和头像兜底。
  - [x] 1.3 确保加载期间用户菜单不显示“未登录”。
  - [x] 1.4 确保接口成功返回后以接口用户和权限为准。

- [x] 2. 鉴权失败处理
  - [x] 2.1 在需求中心上下文接口返回 `401/403` 时清理 `moonbox.frontend.session`。
  - [x] 2.2 同时清理 `moonbox.admin.session`。
  - [x] 2.3 导航到 `/login` 或展示一致登录失效处理。
  - [x] 2.4 确认其他非鉴权错误不误清理合法会话。

- [x] 3. 回归测试
  - [x] 3.1 覆盖 context pending 期间用户菜单使用本地已知用户。
  - [x] 3.2 覆盖 context 成功后接口用户覆盖本地兜底。
  - [x] 3.3 覆盖 `401/403` 时两类 session 清理与 `/login` 跳转。
  - [x] 3.4 回归前台登录、进入后台、退出登录和前台修改密码流程。
  - [x] 3.5 运行 `pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run`。
  - [x] 3.6 运行 `pnpm --dir src/web build`。

- [x] 4. 文档与追溯
  - [x] 4.1 回填 BUG acceptance 验收结果与证据。
  - [x] 4.2 回填 Change trace、Sprint acceptance-report 和 release-note。
  - [x] 4.3 评估是否需要沉淀 `docs/knowledge-base/incidents/`；若无复用价值，在 trace 中说明不适用。
