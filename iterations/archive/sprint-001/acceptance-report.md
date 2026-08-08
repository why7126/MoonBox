---
note: workflow-sync — 17/17 Change 已 archive；0 applied；待人工 sign-off
sprint_id: sprint-001
status: passed
created_at: 2026-07-30 08:51:51
updated_at: 2026-08-08 23:33:28
---

# Sprint-001 验收报告

## 验收范围

| 类型 | 编号 | Change | 当前状态 | 验收结论 |
|---|---|---|---|---|
| REQ | REQ-0001-homepage | add-homepage-brand-visual | done，已归档（`add-homepage-brand-visual` archived 2026-07-30 22:21:30） | 验收通过 |
| REQ | REQ-0002-login-page | add-login-page | done，已归档（`add-login-page` archived 2026-08-07 18:03:38） | 验收通过 |
| REQ | REQ-0003-database-compatibility | add-database-compatibility | done，已归档（`add-database-compatibility` archived 2026-07-30 09:36:18） | 验收通过 |
| REQ | REQ-0004-admin-user-management | add-admin-user-management | done，已归档（`add-admin-user-management` archived 2026-08-08 19:20:56） | 验收通过 |
| REQ | REQ-0005-admin-auth-system | add-admin-auth-system | done，已归档（`add-admin-auth-system` archived 2026-08-08 22:35:00） | 验收通过 |
| REQ | REQ-0006-admin-crud-list-template | add-admin-crud-list-template | done，已归档（`add-admin-crud-list-template` archived 2026-08-08 21:52:47） | 验收通过 |
| REQ | REQ-0007-admin-user-first-login-activation | update-admin-user-first-login-activation | done，已归档（`update-admin-user-first-login-activation` archived 2026-08-08 22:22:42） | 验收通过 |

## 功能验收

- [x] 首页左上角展示 `/brand/moonbox/moonbox-nav-logo.png` 导航专用 Logo。
- [x] 首页首屏右侧展示 `image.png`，主体清晰可辨。
- [x] 首页展示 `AI 原生软件工厂` 与 `打开宝盒，拥有一家软件公司`。
- [x] 首页展示 `Agent 工作流`、`产品知识库`、`交付 Harness`。
- [x] `开启 MoonBox` 与 `打开第一个项目` 均进入既有登录页入口。
- [x] 登录页显示时，首页主体内容不再作为当前主交互界面展示。
- [x] 直接访问带 `#login` 的地址时，应显示登录页。
- [x] 登录页左上角显示“返回首页”入口，点击后恢复首页视图并清除登录页状态。
- [x] 登录表单包含用户名、密码、记住我和登录按钮。
- [x] 用户名与密码均为必填；为空提交时应阻止提交并出现提示。
- [x] 当前原型提交不发起真实鉴权请求，不生成 Token，不改变真实会话状态。
- [x] 开发环境默认可使用 SQLite 启动后端服务，并完成基础连接、初始化和 CRUD 验证。
- [x] 生产环境必须显式配置 MySQL；配置缺失、连接失败或误用 SQLite 时启动失败。
- [x] ORM、Repository、schema 与迁移完成 SQLite/MySQL 差异审计。
- [x] MySQL 关键路径覆盖连接、迁移、基础 CRUD、约束校验和事务行为。
- [x] 数据库设计、部署文档、数据库规则和兼容性记录完成同步。
- [ ] 用户管理列表、创建、编辑、冻结、解冻、逻辑删除、重置密码、头像上传和超级管理员保护验收通过。
- [ ] 后台登录页提供超级管理员用户名密码登录入口。
- [ ] 登录成功后签发 access token，并创建服务端会话记录。
- [ ] 退出登录后当前会话失效，旧 token 访问 `/api/v1/admin/**` 返回 401。
- [ ] `/api/v1/admin/**` 替换 `x-admin-role: admin` 占位鉴权，未认证返回 401，无权限返回 403。
- [ ] 环境变量首次幂等创建唯一超级管理员，生产环境禁止空密码、示例密码或弱密码。
- [x] 后台 CRUD 列表页模板覆盖页头、主操作、筛选栏、表格、分页、确认弹窗、表单弹窗、toast、加载和空状态。
- [x] 用户管理页完成模板化适配或等价验证，核心能力、视觉密度、筛选、表格、分页、弹窗和 toast 无可感知回退。
- [x] 后续后台 CRUD 列表页优先通过模板和通用组件创建，避免复制用户管理页大段 JSX/CSS。
- [ ] 新建后台管理员保持“待激活”，使用有效临时密码首次登录成功后自动转为“正常”。
- [ ] 待激活用户被冻结后不可登录，解冻后仍恢复为“待激活”。
- [ ] 正常用户被冻结后不可登录，解冻后恢复为“正常”。
- [ ] 前台用户不得通过待激活首次登录流程进入管理后台，已删除用户不得通过解冻或首次登录恢复。

## UI 验收

- [x] 深色主题、金色强调和近直角按钮符合 MoonBox UI 规则。
- [x] 桌面端首屏维持左文案右产品视觉结构。
- [x] 移动端 Logo、标题、CTA 和产品视觉不溢出、不遮挡。
- [x] 首页不出现登录页表单、返回首页入口、忘记密码或申请体验。
- [x] 登录页背景复用首页产品视觉，并通过深色遮罩保证表单区域清晰可读。
- [x] 登录卡片顶部显示 MoonBox 产品 Logo。
- [x] 登录页不展示忘记密码、申请体验、注册、第三方登录、邮箱验证码或手机号验证码入口。
- [x] 移动端登录卡片、输入框、按钮和返回入口不得横向溢出，关键文案不得互相遮挡。
- [x] 后台 CRUD 列表页分页 DOM 与用户管理页基准一致。
- [x] 后台 CRUD 列表页成功和失败反馈使用 fixed toast，不造成 layout shift。
- [x] 后台 CRUD 列表页状态变更使用设计系统确认弹窗，且不得调用 `window.confirm`。
- [x] 后台 CRUD 列表页新增、编辑或确认弹窗通过 computed width 和低视口 body scroll 验收。
- [ ] 冻结/解冻确认弹窗展示恢复目标状态，状态变更使用设计系统确认弹窗且不得调用 `window.confirm`。

## 测试记录

- `pnpm --dir src/web test`：通过，2 个测试文件、5 个测试用例。
- `pnpm --dir src/web build`：通过，完成 TypeScript 与 Vite 生产构建。
- `curl -I http://127.0.0.1:5173/`：200 OK。
- `curl -I http://127.0.0.1:5173/brand/moonbox/Logo1-20260728001940.png`：200 OK。
- `curl -I http://127.0.0.1:5173/brand/moonbox/image.png`：200 OK。
- Playwright Chromium Headless Shell v1200：已安装并完成本地首页检查；桌面、笔记本、平板与移动端均无横向/纵向溢出，返修后底部留白约为桌面 81px、笔记本 65px、移动端 44px。
- Web 标签页图标：Playwright 验证 `title=MoonBox`，favicon 指向 `/brand/moonbox/moonbox-favicon-64.png` 且资源返回 200。
- 首页左上角 Logo：附件图已裁剪为 `/brand/moonbox/moonbox-nav-logo.png` 导航专用资产；Playwright 验证资源返回 200，自然尺寸 `1502x438`，渲染尺寸 `192x56`。
- `add-login-page` 已完成 `/opsx-apply`；登录页截图以原型 PNG + 构建产物 + 自动化行为覆盖作为等价视觉验收记录。
- `PYTHONPATH=src/backend pytest`：通过，8 个测试通过，1 个 MySQL live 测试因本地未设置 `RUN_MYSQL_TESTS=1` 跳过。
- `docker compose config --quiet`：通过。
- `openspec validate add-database-compatibility --strict`：通过。
- `.github/workflows/test.yml` 已配置 MySQL 8.4 service，CI 中设置 `RUN_MYSQL_TESTS=1` 后执行 MySQL 初始化兼容测试。
- `pnpm --dir src/web test`：通过，覆盖管理后台登录/退出请求使用 `VITE_API_BASE_URL` 拼接后端 API 地址。
- `pnpm --dir src/web build`：通过，完成返修后 TypeScript 与 Vite 生产构建。
- `openspec validate add-admin-auth-system --strict`：通过。
- `git diff --check -- openspec/archive/2026-08-08-add-admin-auth-system/design.md openspec/archive/2026-08-08-add-admin-auth-system/tasks.md openspec/archive/2026-08-08-add-admin-auth-system/trace.md docs/02-deployment.md`：通过。
- `pnpm --dir src/web test`：通过，覆盖用户管理列表从 `/api/v1/admin/users` 读取真实分页数据、筛选参数、分页条数、创建保存、头像上传回显和状态操作 toast。
- `pnpm --dir src/web build`：通过，完成用户管理真实数据源返修后的 TypeScript 与 Vite 生产构建。
- `uv run pytest tests/integration/api/test_admin_users.py`：通过，9 个用户管理 API 集成测试通过，覆盖列表、创建、筛选、编辑、状态操作、头像上传读取、CORS 和鉴权边界。
- `uv run pytest tests/integration/api/test_admin_users.py`：通过，10 个用户管理 API 集成测试通过，新增覆盖创建用户返回的一次性临时密码可登录、重置后旧密码失效且新临时密码可登录。
- `pnpm --dir src/web test`：通过，覆盖创建用户成功后仅展示一次后端返回的临时密码。
- `pnpm --dir src/web build`：通过，完成创建用户响应契约调整后的 TypeScript 与 Vite 生产构建。
- `pnpm --dir src/web test`：通过，20 个用例覆盖创建用户/重置密码后打开临时密码弹窗、复制按钮成功反馈、关闭后清空前端临时密码状态且不持久化。
- `pnpm --dir src/web build`：通过，完成临时密码弹窗与复制交互后的 TypeScript 与 Vite 生产构建。
- `pnpm --dir src/web test`：通过，20 个用例覆盖临时密码弹窗关闭按钮文案调整为“关闭”及关闭后清空状态。
- `pnpm --dir src/web build`：通过，完成临时密码弹窗文案调整后的 TypeScript 与 Vite 生产构建。
- `pnpm --dir src/web test`：通过，20 个用例覆盖弹窗 footer 操作按钮统一高度、最小宽度、padding 和圆角样式。
- `pnpm --dir src/web build`：通过，完成弹窗 footer 按钮尺寸收敛后的 TypeScript 与 Vite 生产构建。
- `pnpm --dir src/web test`：通过，21 个用例覆盖默认列表和“全部状态”隐藏已删除用户；该轮曾覆盖显式筛选“已删除”展示逻辑删除用户，后续验收已收敛为前端不提供该筛选项。
- `uv run pytest tests/integration/api/test_admin_users.py`：通过，11 个用户管理 API 集成测试通过，新增覆盖后端默认排除 `status=已删除`、显式筛选返回逻辑删除用户和 `total` 同规则计算。
- `pnpm --dir src/web test`：通过，21 个用例覆盖状态筛选项删除“已删除”，页面默认继续隐藏逻辑删除用户。
- `pnpm --dir src/web build`：通过，完成状态筛选项收敛后的 TypeScript 与 Vite 生产构建。
- `pnpm --dir src/web test`：通过，24 个用例覆盖 `/admin` 正式入口、旧 `#admin-users` 兼容、首页 CTA 进入后台入口和后台登录页密码显示/隐藏。
- `pnpm --dir src/web build`：通过，完成管理后台入口与登录页 UI/UE 返修后的 TypeScript 与 Vite 生产构建。
- 1440x900 Playwright 视觉验收：通过，管理后台登录页密码输入框与显示/隐藏按钮中心线差值 `0px`，截图 `/tmp/moonbox-admin-login-1440.png`。
- `pnpm --dir src/web test`：通过，4 个测试文件、25 个用例，覆盖后台 CRUD 列表页模板槽位、用户管理列表、筛选、分页、状态操作、弹窗和 toast。
- `pnpm --dir src/web build`：通过，完成后台 CRUD 列表页模板化后的 TypeScript 与 Vite 生产构建。
- 1440x900 Playwright 视觉验收：通过，截图 `issues/requirements/archive/REQ-0006-admin-crud-list-template/prototype/web/final-1440.png`；新增弹窗 computed width `560px`，确认弹窗 computed width `460px`，toast 为 fixed，分页 DOM 与表格横向滚动验收通过。

## 风险与遗留

- `REQ-0002-login-page` 已通过 `add-login-page` 纳入 Sprint，真实认证接口、Token 和会话管理仍不属于本 Sprint 范围。
- `REQ-0003-database-compatibility` 已新增 MySQL 可复现验证方式；本地未启动 MySQL service 时 live 测试跳过，CI 中运行。真实历史数据迁移、高可用和容量规划仍不属于本 Sprint 范围。
- `REQ-0005-admin-auth-system` 已通过 `add-admin-auth-system` 完成实现、验收回填与 OpenSpec archive。
- `REQ-0006-admin-crud-list-template` 已通过 `add-admin-crud-list-template` 完成 apply、验收回填与 OpenSpec archive。
- `REQ-0007-admin-user-first-login-activation` 已通过 `update-admin-user-first-login-activation` 完成实现、验收回填与 OpenSpec archive。
