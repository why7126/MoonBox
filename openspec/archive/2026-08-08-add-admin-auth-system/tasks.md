# Tasks

## 1. 后端认证与会话

- [x] 1.1 设计并实现后台认证 API：登录、退出、当前管理员摘要。
- [x] 1.2 实现密码哈希校验，禁止明文密码存储、日志输出和测试夹具泄露。
- [x] 1.3 实现 access token 签发、过期校验和 token 标识。
- [x] 1.4 实现服务端会话记录，支持创建、查询、最后使用时间更新、撤销和过期判断。
- [x] 1.5 实现账号冻结、删除、重置密码或权限状态变化后的后台会话失效策略。

## 2. 超级管理员初始化

- [x] 2.1 实现环境变量首次幂等创建唯一系统内置超级管理员。
- [x] 2.2 生产环境拒绝空密码、示例密码和弱密码。
- [x] 2.3 确保初始化过程不输出明文密码或可复用凭证。

## 3. 后台 API 鉴权替换

- [x] 3.1 替换 `/api/v1/admin/**` 的 `x-admin-role: admin` 占位鉴权。
- [x] 3.2 后端从 access token 与服务端会话解析当前操作者。
- [x] 3.3 未认证返回 401，已认证但无后台权限返回 403。
- [x] 3.4 禁止信任前端传入的 `user_id`、`role`、`is_admin` 或等价身份字段。

## 4. 管理后台前端

- [x] 4.1 实现后台登录页，包含用户名、密码、登录按钮、loading/disabled 状态和受控错误反馈。
- [x] 4.2 实现后台登录态存储与清理策略，避免将凭证写入 URL、日志、错误上报、埋点或截图。
- [x] 4.3 实现后台路由守卫，未登录或登录态失效时进入后台登录页或等价登录入口。
- [x] 4.4 实现退出登录入口和退出后的本地状态清理。
- [x] 4.5 处理后台 API 401/403 响应，避免空白页、死循环跳转或不可恢复状态。

## 5. 文档与契约

- [x] 5.1 同步 `docs/03-api-index.md`、OpenAPI 契约和错误码说明。
- [x] 5.2 同步 `docs/04-database-design.md` 中的服务端会话记录和超级管理员初始化约束。
- [x] 5.3 同步 `docs/02-deployment.md`、`.env.example` 和 `src/backend/.env.example` 的后台认证环境变量。
- [x] 5.4 同步 `docs/standards/authentication.md` 的当前认证策略、公开端点、前端登录态和权限模型。

## 6. 测试与验收

- [x] 6.1 后端测试覆盖登录成功、登录失败、token 缺失、token 过期、会话撤销、退出后复用 token、无后台权限访问和生产弱密码初始化拒绝。
- [x] 6.2 后端测试覆盖 `x-admin-role: admin` 不再绕过 `/api/v1/admin/**` 正式鉴权。
- [x] 6.3 前端测试覆盖未登录访问后台路由、登录成功进入后台、401 后回到登录入口和退出登录清理登录态。
- [x] 6.4 运行 OpenSpec 校验、相关后端 pytest、前端 Vitest/Testing Library 和必要构建验证。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-08 22:35:00 | 密码框中显示/隐藏图标未与输入框垂直居中。 | 收紧 `.admin-login-password` 选择器，避免被登录面板通用 `span` 样式影响；为显隐按钮增加 `transform: translateY(-50%)`，确保按钮中心线与 40px 密码输入框中心线对齐。 | `pnpm --dir src/web test` 26 passed；`pnpm --dir src/web build` passed；`openspec validate add-admin-auth-system --strict` passed；`git diff --check` passed；1440x900 Playwright 视觉验收通过，密码输入框与显隐按钮中心线差值 `0px`，截图 `/tmp/moonbox-admin-login-1440.png`。 |
| 2026-08-08 20:48:00 | 管理后台正式入口使用 `#admin-users` 不够清晰，登录页 UI/UE 需要密码显示/隐藏、按钮状态和错误反馈优化；用户确认正式入口只做 `/admin`。 | 前端支持 `/admin` 正式入口并兼容旧 `#admin-users`；首页 CTA 进入 `/admin`；登录页增加密码显示/隐藏按钮、输入框 focus/error 状态、稳定的主按钮 disabled/loading 样式和更清晰的说明文案；补充前端测试覆盖正式入口、旧入口兼容、首页 CTA 和密码显隐。 | `pnpm --dir src/web test` 24 passed；`pnpm --dir src/web build` passed；`openspec validate add-admin-auth-system --strict` passed；`git diff --check` passed。 |
| 2026-08-08 10:38:00 | 重置密码后使用临时密码登录显示“用户名或密码错误”，无法判断是密码错误、账号状态不可用还是无后台权限。 | 登录页改为展示后端返回的受控错误详情；临时密码弹窗增加“仅状态为正常的后台管理员账号可登录后台”的说明；补充前端测试覆盖登录失败详情和临时密码使用前提提示。 | `pnpm --dir src/web test` 22 passed；`pnpm --dir src/web build` passed；`openspec validate add-admin-auth-system --strict` passed；`git diff --check` passed。 |
| 2026-08-08 10:29:47 | 后台登录仍报 `NetworkError when attempting to fetch resource.`，后端日志显示 `OPTIONS /api/v1/admin/auth/login` 返回 405，浏览器 CORS 预检失败。 | 后端读取 `BACKEND_CORS_ORIGINS` 并挂载 FastAPI `CORSMiddleware`，允许 Web 管理后台 Origin 对后台认证接口发起预检与真实请求；补充 CORS 预检集成测试，并同步部署文档说明。 | `uv run pytest tests/integration/api/test_admin_users.py tests/unit/test_database_config.py` 13 passed；`pnpm --dir src/web test` 11 passed；`pnpm --dir src/web build` passed；`docker compose build backend` passed；`docker compose up -d backend web` passed；backend healthy；容器内 `/api/v1/admin/auth/login` OPTIONS 200 且 `access-control-allow-origin=http://localhost:5173`；`openspec validate add-admin-auth-system --strict`、`validate-openspec-language.py`、`git diff --check` 均通过。 |
| 2026-08-08 10:13:58 | 后台登录页报 `NetworkError when attempting to fetch resource.`，排查发现 `moonbox-backend` 容器反复重启，先后暴露 `ModuleNotFoundError: No module named 'sqlalchemy'`、SQLite 数据库父目录缺失，以及 slim 镜像缺少 `curl` 导致健康检查不稳定。 | 后端 Dockerfile 改为按 `pyproject.toml` 安装项目完整依赖；SQLite 文件型连接串在创建 engine 前自动创建父目录；backend healthcheck 改为 Python 标准库请求 `/health`；本地 `.env` 将 `VITE_API_BASE_URL` 对齐到当前后端宿主端口；同步部署文档说明依赖事实源和端口覆盖约束。 | `docker compose build backend`、`docker compose up -d backend web`、backend healthy、容器内 `/health` 200、容器内 `/api/v1/admin/auth/login` 200、`uv run pytest tests/integration/api/test_admin_users.py tests/unit/test_database_config.py`、`pnpm --dir src/web test`、`pnpm --dir src/web build`、`docker compose config --quiet`、`openspec validate add-admin-auth-system --strict`、`git diff --check` 均通过；当前工具环境宿主机 `curl 127.0.0.1:8001` 不可达，但 Compose 端口映射与容器内 API 已验证。 |
| 2026-08-08 00:25:00 | 从后台登录页点击登录无响应，进入不了后台管理页。根因倾向为前端登录请求使用相对路径 `/api/v1/admin/auth/login`，在 `localhost:5173` 开发环境下请求落到 Web dev server。 | 前端登录/退出请求改为使用 `VITE_API_BASE_URL` 拼接后端 API 地址，并为 Vite dev server 增加 `/api` 到 `localhost:8000` 的开发代理兜底；补充测试断言登录/退出请求 URL。 | `pnpm --dir src/web test`、`pnpm --dir src/web build`、`openspec validate add-admin-auth-system --strict`、`git diff --check -- <touched-docs>` 均通过。 |
