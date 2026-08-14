## 1. 后端统一 Auth API

- [x] 1.1 新增 `/api/v1/auth/*` 路由，覆盖登录、退出、当前用户、个人资料更新、修改密码、头像上传和受保护头像读取。
- [x] 1.2 移除 `/api/v1/admin/auth/*` 路由注册，不保留别名、重定向或隐藏兼容路径。
- [x] 1.3 确保登录返回 token 元数据、当前用户摘要和服务端派生的后台访问字段。
- [x] 1.4 确保 `GET /api/v1/auth/me` 与 `PATCH /api/v1/auth/me` 面向所有登录用户可用，且只作用于已认证用户本人。
- [x] 1.5 确保修改密码校验当前密码、新密码和确认密码，更新密码哈希，撤销该用户全部 session，且不返回可复用凭证。
- [x] 1.6 确保头像上传校验 JPG/PNG/WebP、2 MB 限制、存储写入、归属、持久 URL 和受保护读取代理。
- [x] 1.7 保留 `/api/v1/admin/**` 后端管理员资源鉴权。

## 2. Web Session 与 UI 接线

- [x] 2.1 用单一统一 session 存储替代 `moonbox.frontend.session` 和 `moonbox.admin.session` 运行时依赖。
- [x] 2.2 将登录、退出、当前用户、个人资料保存、头像上传/读取和修改密码调用迁移到 `/api/v1/auth/*`。
- [x] 2.3 更新前台和后台路由守卫使用统一 session，同时保留后端管理员鉴权作为最终权限边界。
- [x] 2.4 在退出登录、修改密码成功、401 认证失败、session 被撤销和账号不可用时清理统一 session。
- [x] 2.5 保持既有登录、用户菜单和个人资料弹窗视觉系统，不引入视觉重设计。

## 3. 契约、文档与生成客户端

- [x] 3.1 更新 OpenAPI 元数据，并按项目流程重新生成或更新客户端产物。
- [x] 3.2 更新 `docs/03-api-index.md` 和认证标准文档，明确 `/api/v1/auth/*` 是唯一正式认证与个人中心 API。
- [x] 3.3 移除或更新引用 `/api/v1/admin/auth/*` 的测试 fixture、脚本和示例。
- [x] 3.4 补充发布/验收说明，明确本次为破坏性迁移，旧 admin-auth 路径不可用。

## 4. 验证

- [x] 4.1 新增或更新后端 pytest 覆盖统一登录、退出撤销、当前用户、个人资料更新、修改密码撤销 session、头像上传/读取、旧路径移除和管理员鉴权保留。
- [x] 4.2 新增或更新前端 Vitest/Testing Library 覆盖统一 session、路由守卫、当前用户刷新、个人资料保存、头像上传状态机、修改密码后重新登录和 401 清理。
- [x] 4.3 记录静态证据，确认旧 `/api/v1/admin/auth/*`、`moonbox.frontend.session` 和 `moonbox.admin.session` 不再作为运行时依赖。
- [x] 4.4 验证 Docker local/default-port 头像上传、受保护读取和前后台当前用户回显；如本地 `:3000` 不可用，则记录已接受的外部治理 deferral。
- [x] 4.5 运行 `update-unified-account-auth-api` 的 OpenSpec 校验。

## 验收返修记录

| 时间 | 反馈 | 调整 | 结果 |
|---|---|---|---|
| 2026-08-12 13:13:07 | 用户管理列表和前台菜单头像已恢复，但前台个人资料弹窗、后台用户菜单、后台个人资料弹窗仍可能使用旧 session 头像快照；前台文字头像 fallback 为一字且样式不一致。 | 后台当前用户入口仅在 session 残留旧头像 URL 时通过 `/api/v1/auth/me` 刷新当前用户摘要；前台个人资料弹窗优先使用已恢复的当前上下文头像，前台 session fallback 忽略旧 admin 头像路径；前台文字头像统一为两字 fallback。 | 前台/后台菜单与个人资料弹窗均使用统一头像路径或一致两字 fallback；旧 session 快照不再覆盖已恢复头像。 |
| 2026-08-12 12:57:13 | 统一头像 API 迁移后，历史 `avatar_url` 仍指向 `/api/v1/admin/users/avatar/*`，导致已有头像回显失败。 | 在后端用户行读模型中将历史头像 URL 规范化为 `/api/v1/auth/avatar/*`；补充登录、`/auth/me`、后台用户列表响应测试；同步 Change 设计、delta spec、API 索引和文件上传规范。 | 旧头像 URL 可继续显示为新受保护读取路径；旧头像读取接口仍不恢复。 |
| 2026-08-12 12:50:00 | Docker `:3000` 可重复验收问题已由独立会话处理；本 Change 不再以该外部治理缺陷阻断 REQ-0016 主体实现收尾。 | 保留既有 Docker `:3000` 占用与默认端口 `18102` 登录失败尝试记录；任务 4.4 改为记录常规 Docker/default-port 尝试与外部治理 deferral，不伪造 Docker 闭环通过证据。 | 文档返修，无代码变更；REQ-0016 主体实现可进入 archive readiness 复核。 |
