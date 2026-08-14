---
change_id: fix-homepage-login-route
type: fix
status: applied
created_at: 2026-08-11 08:41:00
updated_at: 2026-08-11 12:14:08
source_bug: BUG-0003-homepage-start-moonbox-should-open-login-route
sprint: sprint-002
tasks:
  total: 14
  completed: 14
---

# Change Trace

## 基本信息

| 字段 | 值 |
|---|---|
| Change | fix-homepage-login-route |
| 类型 | fix |
| 状态 | applied |
| 来源 BUG | BUG-0003-homepage-start-moonbox-should-open-login-route |
| Sprint | sprint-002 |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-11 12:14:08 | opsx.modify | 验收返修前台用户菜单未显示头像；已让需求中心 BFF 返回 `current_user.avatar_url`，前台菜单用 admin token 读取受保护头像资源，空头像回退首字。 |
| 2026-08-11 12:00:08 | opsx.modify | 验收返修后台用户菜单仍显示两行；已移除后台触发区角色第二行，仅保留昵称/用户名一行，并补充回归断言。 |
| 2026-08-11 11:51:23 | opsx.modify | 验收返修昵称保存后未同步显示；已兼容个人资料修改当前登录用户和用户管理编辑当前用户列表项，用户管理 PUT 返回当前用户时同步后台菜单状态与 `moonbox.admin.session`。 |
| 2026-08-11 10:24:11 | opsx.modify | 验收返修用户菜单显示规则；已补齐前台 BFF、前台需求中心菜单和后台管理菜单回归测试，固定昵称优先、用户名兜底，前台第二行显示当前空间。 |
| 2026-08-11 10:08:06 | opsx.modify | 验收返修需求中心退出登录无效；已新增前台 session 清理并绑定需求中心退出动作，同时清理前台进入态和后台 admin session，调用后台 logout API 后跳转 `/login`。 |
| 2026-08-11 09:55:16 | opsx.modify | 验收返修 `admin/Admin123!` 登录兜底报错；已修复需求中心服务导入期治理根路径解析，优先使用 `MOONBOX_GOVERNANCE_ROOT`，避免容器浅路径下 `parents[4]` 越界导致后端启动失败和登录 API 502。 |
| 2026-08-11 09:41:57 | opsx.modify | 验收返修统一登录边界：`/login` 替代独立管理后台登录页并调用后台登录 API，`/admin` 未登录统一回 `/login`，并删除未使用的 `AdminLoginPage` 组件。 |
| 2026-08-11 09:25:49 | opsx.modify | 验收返修 `/requirements` 用户菜单仍显示「未登录」；已放宽前台 session 用户名兜底条件，覆盖后端空用户、空姓名和显式「未登录」匿名上下文。 |
| 2026-08-11 09:15:57 | opsx.modify | 验收返修需求中心用户菜单显示「未登录」且后台入口缺失；已恢复已有后台 admin session 时携带 Bearer token 识别 `can_access_admin`，仅有前台 session 时用前台用户名兜底。 |
| 2026-08-11 09:06:58 | opsx.modify | 验收返修 `/login` 提交后进入 `/requirements` 却显示后台管理登录页；已拆分前台原型 session 与后台管理员 session，`/requirements` 未登录回 `/login`，已登录进入前台需求中心。 |
| 2026-08-11 08:50:28 | opsx.apply | 完成 `/login` 独立路由修复、前台登录回归测试和构建验证；不需要沉淀 incidents。 |
| 2026-08-11 08:41:00 | bug.opsx | 从 BUG-0003 创建 OpenSpec 修复 Change。 |

## 验证记录

| 时间 | 类型 | 命令/证据 | 结果 |
|---|---|---|---|
| 2026-08-11 08:48:26 | test | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx --run` | pass，5 个测试文件、41 个测试通过 |
| 2026-08-11 08:49:39 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过 |
| 2026-08-11 09:06:13 | test | `pnpm --dir src/web test -- homepage.test.tsx requirement-center.test.tsx admin-auth.test.tsx --run` | pass，5 个测试文件、41 个测试通过 |
| 2026-08-11 09:06:58 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过 |
| 2026-08-11 09:15:27 | test | `pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run` | pass，5 个测试文件、42 个测试通过 |
| 2026-08-11 09:15:57 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过 |
| 2026-08-11 09:25:35 | test | `pnpm --dir src/web test -- requirement-center.test.tsx homepage.test.tsx admin-auth.test.tsx --run` | pass，5 个测试文件、44 个测试通过 |
| 2026-08-11 09:25:49 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-DU09bW5Q.js` |
| 2026-08-11 09:39:06 | test | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx requirement-center.test.tsx --run` | pass，5 个测试文件、44 个测试通过 |
| 2026-08-11 09:39:19 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-BbfR7sWy.js` |
| 2026-08-11 09:41:41 | test | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx requirement-center.test.tsx --run` | pass，5 个测试文件、44 个测试通过；源码已无 `AdminLoginPage` 引用 |
| 2026-08-11 09:41:57 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过 |
| 2026-08-11 09:53:48 | test | `uv run pytest tests/unit/test_requirement_center_paths.py tests/integration/api/test_requirement_center.py` | pass，7 个后端测试通过，覆盖容器浅路径优先使用 `MOONBOX_GOVERNANCE_ROOT` 与需求中心上下文回归 |
| 2026-08-11 09:55:06 | startup | `docker compose up -d --build backend`；`docker compose ps backend`；容器内 API 请求 | pass，backend healthy，web 容器可访问 `backend:8000/health`，容器内 `admin/Admin123!` 登录 API 返回 200 JSON |
| 2026-08-11 10:07:57 | test | `pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run` | pass，5 个测试文件、45 个测试通过，覆盖需求中心退出清理前台与后台 session、调用 logout API 并跳转 `/login` |
| 2026-08-11 10:08:06 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-tVK-RyGA.js` |
| 2026-08-11 10:23:52 | test | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx homepage.test.tsx --run` | pass，5 个测试文件、47 个测试通过，覆盖前台昵称/空间显示和后台昵称/用户名兜底 |
| 2026-08-11 10:22:56 | test | `python -m pytest tests/integration/api/test_requirement_center.py` | pass，6 个后端测试通过，覆盖需求中心用户 display name 昵称优先、用户名兜底 |
| 2026-08-11 10:24:11 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过 |
| 2026-08-11 11:51:13 | test | `pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run` | pass，5 个测试文件、48 个测试通过，覆盖用户管理编辑当前用户后同步后台菜单和 admin session |
| 2026-08-11 11:51:18 | test | `python -m pytest tests/integration/api/test_admin_users.py tests/integration/api/test_requirement_center.py` | pass，22 个后端集成测试通过，覆盖个人资料昵称保存、当前用户读取和需求中心昵称展示 |
| 2026-08-11 11:51:23 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-BcbQCiKD.js` |
| 2026-08-11 12:00:01 | test | `pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx admin-auth.test.tsx homepage.test.tsx --run` | pass，5 个测试文件、48 个测试通过，覆盖后台用户触发区不渲染角色第二行 |
| 2026-08-11 12:00:08 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-Stt6Uwgs.js` |
| 2026-08-11 12:13:08 | test | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx homepage.test.tsx --run` | pass，5 个测试文件、49 个测试通过，覆盖前台菜单用 admin token 加载头像与空头像首字回退，后台头像回归保持通过 |
| 2026-08-11 12:13:08 | test | `python -m pytest tests/integration/api/test_requirement_center.py tests/integration/api/test_admin_users.py` | pass，22 个后端集成测试通过，覆盖需求中心 BFF 当前用户 `avatar_url` 返回和后台头像读取回归 |
| 2026-08-11 12:14:08 | build | `pnpm --dir src/web build` | pass，TypeScript 与 Vite 生产构建通过，生成 `index-BeZaaoZ3.js` |

## 文档同步说明

- API：需求中心 BFF `GET /api/v1/requirement-center/context` 的 `current_user` 增加 `avatar_url` 字段；字段来自当前后台用户摘要，受保护头像资源仍通过既有后台 Bearer token 读取，不需要 Orval 客户端生成。
- DB：不适用，未修改数据结构。
- UI：已更新统一登录路由、前台进入态、`/requirements` 前台保护、`/admin` 未登录回 `/login`、需求中心用户菜单权限展示、退出登录跳转 `/login`、前后台用户菜单昵称/用户名兜底规则、后台菜单单行展示、昵称保存后当前会话同步、前台菜单头像展示和回归测试；未引入新的视觉模式。
- 部署：不适用，现有 SPA fallback 已支持 `/login`。
- 容器启动：已修复后端导入期路径兜底，Docker backend 可在 `/app/app/services/requirement_center.py` 浅路径下正常启动。
- 安全：不改变后端权限模型；统一登录页复用既有后台认证 API，不把前台 session 作为后台权限凭证；后台权限展示仅在已有后台 admin session 且后端返回 `can_access_admin` 时启用；退出登录会清除前台进入态与后台 admin session，并尽力调用后端 logout 吊销服务端会话。
- Knowledge Base incidents：不适用，本问题为小范围前台路由语义修复，无独立事故复盘价值。
