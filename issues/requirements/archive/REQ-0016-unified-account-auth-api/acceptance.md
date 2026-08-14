---
requirement_id: REQ-0016-unified-account-auth-api
acceptance_status: passed
created_at: 2026-08-12 10:04:53
updated_at: 2026-08-14 16:29:34
---

# 验收清单

## 功能 AC

- [ ] AC-001 统一登录接口：`POST /api/v1/auth/login` 可完成账号密码登录，返回 access token、过期时间、token 类型和当前用户摘要。
- [ ] AC-002 登录态边界：待激活用户首次登录后按既有策略激活，冻结、删除或账号不可用用户无法获得有效会话。
- [ ] AC-003 旧登录路径删除：`POST /api/v1/admin/auth/login` 不再作为可用接口暴露，前端、测试、文档和 OpenAPI 不再引用旧路径。
- [ ] AC-004 统一退出接口：`POST /api/v1/auth/logout` 可撤销当前服务端会话，旧 token 再访问受保护接口返回 401。
- [ ] AC-005 当前用户读取：`GET /api/v1/auth/me` 面向所有已登录用户返回当前用户摘要，不要求后台管理员角色。
- [ ] AC-006 个人资料更新：`PATCH /api/v1/auth/me` 允许所有登录用户修改自己的昵称和头像 URL，且不得通过请求体指定目标用户、角色、状态、权限或密码。
- [ ] AC-007 昵称规则：昵称最长 128 个字符，保存时去除首尾空白，清空昵称后用户菜单回退展示用户名。
- [ ] AC-008 头像 URL 规则：保存到用户资料的头像 URL 必须是后端返回或系统可访问的持久 URL，不得保存 `blob:`、本地临时路径或对象存储内部敏感路径。
- [ ] AC-009 修改密码：`POST /api/v1/auth/change-password` 面向所有登录用户可用，校验当前密码、新密码和确认新密码。
- [ ] AC-010 改密会话撤销：修改密码成功后撤销该用户所有服务端会话，前端清理统一 session 并回到 `/login`。
- [ ] AC-011 头像上传：`POST /api/v1/auth/avatar` 或等价统一路径面向所有登录用户可用，支持 JPG、PNG、WebP，单文件不超过 2MB。
- [ ] AC-012 头像读取：头像读取使用受保护后端代理路径，前端不得直连 MinIO 私有对象或暴露临时凭据。
- [ ] AC-013 单一 session：前端使用统一 `moonbox.session` 或等价存储，不再运行时依赖 `moonbox.frontend.session` 与 `moonbox.admin.session` 双存储。
- [ ] AC-014 路由守卫：前台需求中心基于统一 session 判断登录态；管理后台基于统一 session 的用户摘要显示入口，但最终以后端 `/api/v1/admin/**` 授权为准。
- [ ] AC-015 后台授权：普通前台用户可登录、改资料、改密码、上传头像，但调用 `/api/v1/admin/**` 管理接口必须返回 403 或等价权限不足响应。
- [ ] AC-016 契约同步：`docs/03-api-index.md`、`docs/standards/authentication.md`、OpenAPI、Orval 客户端、后端集成测试和前端测试均完成 `/api/v1/auth/*` 迁移。
- [ ] AC-017 破坏性迁移证据：验收记录必须包含旧 `/api/v1/admin/auth/*` 不再注册或不再被引用的检索/测试证据。
- [ ] AC-018 敏感信息保护：认证、改密、头像上传和资料更新流程不得在日志、错误响应、前端缓存、测试 fixture 或文档示例中保存明文密码、access token、会话 ID 明文、密码哈希、对象存储密钥或 `.env` 内容。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-media-upload-chain.md` — 预防 Sprint 002/003 复发类缺陷

- [ ] AC-XCUT-001 头像上传组件必须具备 `idle -> uploading -> done/failed` 状态机；上传中禁用重复选择和重复提交，失败后允许重试。
- [ ] AC-XCUT-002 头像上传成功后必须在同一会话立即回显到当前个人资料入口和用户菜单，不依赖刷新页面；保存到资料中的对象引用不得泄露临时凭据或敏感上下文。
- [ ] AC-XCUT-003 Docker 本地 `:3000` 边界必须能完成头像文件上传、受保护读取和前后台回显验收；容器网络、浏览器访问和反向代理路径保持一致。

## 非目标 AC

- [ ] AC-OUT-001 本需求不新增注册、忘记密码、OAuth、SSO、MFA、refresh token、多端互踢或设备管理。
- [ ] AC-OUT-002 本需求不重做登录页、前台用户菜单、后台用户菜单或个人资料弹窗视觉。
- [ ] AC-OUT-003 本需求不改变 `/api/v1/admin/users/*` 用户管理资源接口的后台管理员授权要求。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: update-unified-account-auth-api
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

