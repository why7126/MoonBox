---
change_id: fix-homepage-login-route
status: applied
created_at: 2026-08-11 08:41:00
updated_at: 2026-08-11 12:14:08
source_bug: BUG-0003-homepage-start-moonbox-should-open-login-route
---

# Tasks

- [x] 1. 路由实现
  - [x] 1.1 在 `App` 中识别 `/login` 前台登录路由。
  - [x] 1.2 将现有前台登录视图作为 `/login` 主视图展示。
  - [x] 1.3 首页「开启 MoonBox」跳转到 `/login`，不再写入 `#login`。
  - [x] 1.4 首页「打开第一个项目」跳转到 `/login`，不再写入 `#login`。
  - [x] 1.5 登录页「返回首页」导航到 `/`。

- [x] 2. 回归边界
  - [x] 2.1 保持当前前台登录原型提交后进入 `/requirements`。
  - [x] 2.2 确认提交前台登录原型不调用后台登录 API。
  - [x] 2.3 确认 `/admin` 仍展示管理后台登录或后台页面，不被前台登录路由接管。
  - [x] 2.4 确认 `/requirements` 使用前台登录 session 保护，不再回落到管理后台登录页。

- [x] 3. 测试
  - [x] 3.1 更新 `homepage.test.tsx` 中 `#login` 断言为 `/login`。
  - [x] 3.2 增加直接访问 `/login` 的前台登录页测试。
  - [x] 3.3 增加 `/login` 返回首页和提交进入 `/requirements` 的回归测试。
  - [x] 3.4 运行 `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx --run`。
  - [x] 3.5 运行 `pnpm --dir src/web build`。

- [x] 4. 文档与追溯
  - [x] 4.1 回填 BUG acceptance 验收结果。
  - [x] 4.2 回填 Change trace、Sprint acceptance-report 和 release-note。
  - [x] 4.3 评估是否需要沉淀 `docs/knowledge-base/incidents/`；若无复用价值，在 trace 中说明不适用。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-11 09:06:58 | 从 `/login` 前台登录后跳转 `/requirements` 时显示后台管理登录页。 | 新增前台原型 session，`/requirements` 未登录时回到 `/login` 前台登录页，已登录时进入前台需求中心；需求中心加载不再携带后台管理员 token。 | `pnpm --dir src/web test -- homepage.test.tsx requirement-center.test.tsx admin-auth.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 09:15:57 | 进入 `/requirements` 后用户菜单显示「未登录」，已有后台权限也不显示「进入后台」。 | 前台 session 继续用于 `/requirements` 路由保护；若本地已有后台 admin session，需求中心上下文请求继续携带 Bearer token 识别 `can_access_admin`；仅有前台 session 时用前台用户名兜底，不显示「未登录」。 | `pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 09:25:49 | `/requirements` 用户菜单仍显示「未登录」。 | 放宽前台用户名兜底条件：只要存在有效 `moonbox.frontend.session.username`，且后端用户为空、姓名为空或姓名为「未登录」，用户菜单统一展示前台用户名。 | `pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 09:41:57 | 用户确认本质目标是用当前 `/login` 页面替代管理后台登录页，去掉独立管理后台登录页面功能。 | `/login` 统一调用后台登录 API，成功后同时建立后台 session 与前台进入态并进入 `/requirements`；`/admin` 未登录统一回 `/login`；删除未使用的 `AdminLoginPage` 组件。 | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx requirement-center.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 09:55:16 | 使用 `admin/Admin123!` 登录时报「登录失败，请稍后重试」。 | 修复 `requirement_center.py` 导入期治理根路径解析：优先使用 `MOONBOX_GOVERNANCE_ROOT`，浅层容器路径不再访问越界的 `parents[4]`，避免后端启动失败导致登录 API 502。 | `uv run pytest tests/unit/test_requirement_center_paths.py tests/integration/api/test_requirement_center.py`；`docker compose up -d --build backend`；backend healthy；容器内登录 API 返回 200 JSON |
| 2026-08-11 10:08:06 | 需求中心退出登录无效。 | 新增前台 session 清理函数，需求中心「退出登录」同时清理前台 session 与后台 admin session，调用后台 logout API 后跳转 `/login`。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 10:24:11 | 用户菜单栏显示规则需明确：前台显示用户昵称 + 当前空间，后台显示用户昵称；昵称为空时显示用户名。 | 固定现有显示规则：后端需求中心 display name 使用昵称优先、用户名兜底；前台菜单第一行显示 display name、第二行显示当前空间；后台菜单显示昵称优先、用户名兜底。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx homepage.test.tsx --run`；`python -m pytest tests/integration/api/test_requirement_center.py`；`pnpm --dir src/web build` |
| 2026-08-11 11:51:23 | 个人资料昵称保存后未同步显示为新昵称；需兼容个人资料修改当前登录用户与用户管理编辑列表项。 | 用户管理编辑当前登录用户时，用 PUT 返回用户同步后台菜单状态和 `moonbox.admin.session`；个人资料路径继续复用 `updateAdminProfile` 更新后端当前用户与 admin session，前台需求中心通过 Bearer context 读取最新昵称。 | `pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run`；`python -m pytest tests/integration/api/test_admin_users.py tests/integration/api/test_requirement_center.py`；`pnpm --dir src/web build` |
| 2026-08-11 12:00:08 | 后台用户菜单仍显示两行。 | 移除后台用户触发区角色第二行，仅保留用户昵称；昵称为空时继续显示用户名，并补充不渲染 `.admin-user-meta small` 的回归断言。 | `pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run`；`pnpm --dir src/web build` |
| 2026-08-11 12:14:08 | 前台用户菜单未显示用户头像；需求中心 BFF 应返回当前用户 `avatar_url`，前台菜单应复用带鉴权头像加载逻辑。 | 需求中心 BFF `current_user` 增加 `avatar_url`；前台需求中心菜单使用 admin token 读取受保护头像资源，头像为空或读取失败时回退首字。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx homepage.test.tsx --run`；`python -m pytest tests/integration/api/test_requirement_center.py tests/integration/api/test_admin_users.py`；`pnpm --dir src/web build` |
