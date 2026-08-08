# 设计说明

## 背景

REQ-0005 要求为管理后台建立真实认证系统，并替换现有 `/api/v1/admin/**` 的 `x-admin-role: admin` 占位鉴权。该能力必须先于后续后台敏感能力长期扩展稳定下来，否则用户管理、密码重置和状态治理等操作缺少真实操作者身份。

## 目标

- 提供超级管理员账号密码登录。
- 使用 access token + 服务端会话记录形成可撤销、可过期、可校验的后台登录态。
- 支持退出登录和账号状态变化后的会话失效。
- 用正式认证依赖保护所有 `/api/v1/admin/**` 管理接口。
- 通过环境变量首次幂等初始化唯一系统内置超级管理员，并阻止生产弱密码。

## 非目标

- 不实现普通 Web 前台用户登录。
- 不实现 refresh token、长期自动续期、多端互踢、MFA、SSO、OAuth、邮箱/短信验证码或忘记密码。
- 不实现安装向导创建超级管理员。
- 不实现独立审计日志查询页面。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  admin: true
  database: true
  storage: false
  api: true
  security: true
capabilities:
  new:
    - web-admin-auth-system
  modified:
    - api-governance
    - database-compatibility
    - deployment-governance
```

## D1. 前端策略

采用 Design System / 管理后台原生实现策略，不做 CSS Port。`prototype/web/prototype.html` 只作为后台登录页结构草图，后续实现应复用当前管理后台 shell 的近直角、细线、克制金色强调和深浅主题规则。

后台登录页包含：

- MoonBox 管理后台品牌标识。
- 用户名输入。
- 密码输入。
- 登录按钮和 loading/disabled 状态。
- 受控错误反馈区域。

后台登录页不得展示注册、忘记密码、第三方登录、短信验证码、邮箱验证码或 SSO 入口。

管理后台正式入口使用 `/admin`。未登录访问 `/admin` 时展示管理后台登录页；登录成功后进入当前默认后台页面。旧入口 `#admin-users` 暂时保持兼容，避免验收期和本地书签失效。

管理后台前端调用后端 API 时必须使用配置化 API base URL。开发与 Docker 环境默认读取 `VITE_API_BASE_URL=http://localhost:8000`；本地 Vite dev server 可配置 `/api` proxy 作为未显式设置 base URL 时的开发兜底。登录请求不得固定打到 Web 前端服务 origin，避免 `localhost:5173` 下点击登录无响应或请求落到前端服务。

登录失败时，前端应展示后端返回的受控 `detail` 或 `message`。若账号不可用、无后台权限、凭证失效或认证失败，页面应给出对应可恢复反馈，不得全部折叠成“用户名或密码错误”。

登录页应提供密码显示/隐藏按钮、清晰的输入框 focus/error 状态、稳定的登录按钮 disabled/loading 状态。主按钮应作为页面唯一主操作，宽度和高度在 loading 时保持稳定。

创建用户或重置密码后展示临时密码时，前端必须说明该密码仅展示一次，并提示只有“后台管理员”且状态为“正常”的账号可使用临时密码登录管理后台。

## D2. 认证与会话模型

登录成功后，后端创建服务端会话记录并签发 access token。access token 只作为访问凭证，后端每次处理 `/api/v1/admin/**` 请求时都必须校验对应服务端会话：

```text
Authorization: Bearer <access_token>
  |
  v
校验 token 签名与过期时间
  |
  v
查找服务端会话记录
  |
  v
校验未撤销、未过期、账号状态可用、具备后台权限
```

服务端会话记录至少包含：

- 会话 ID。
- 用户 ID。
- token 标识或 token 哈希。
- 创建时间。
- 过期时间。
- 撤销时间。
- 最后使用时间。

退出登录必须撤销当前服务端会话。账号被冻结、删除、重置密码或发生影响权限的状态变化时，相关后台会话必须失效。

## D3. 超级管理员初始化

系统启动或初始化时，若不存在系统内置超级管理员，则读取环境变量创建唯一超级管理员。初始化必须幂等，重复启动不得创建第二个系统内置超级管理员。

生产环境必须拒绝空密码、示例密码或弱密码。弱密码判定至少覆盖：

- 空字符串。
- `change-me`、`change-me-on-first-run`、`admin`、`password` 等示例值。
- 长度不足项目安全阈值的密码。

初始密码不得写入日志、API 响应、前端页面或审计明文。

## D4. API 边界

公开端点仅包含后台登录、健康检查等明确白名单。所有 `/api/v1/admin/**` 管理接口默认需要认证。

后端必须移除 `x-admin-role: admin` 作为正式鉴权依据的行为。认证依赖应从 access token 与服务端会话记录解析当前操作者，并禁止信任前端传入的 `user_id`、`role`、`is_admin` 或等价身份字段。

错误语义：

- 401：未携带凭证、凭证无效、凭证过期、会话不存在、会话已撤销或登录态失效。
- 403：已认证但无后台权限、账号状态不允许访问后台或操作对象受保护。

## D5. Conflict Resolution

原型与验收优先级：

```text
HTML > context.md > acceptance.md > ui-design.md > openspec/specs
```

本 Change 没有 PNG 原型。`prototype.html` 仅表达后台登录页基础结构；`acceptance.md` 对真实认证、安全边界和 API 鉴权具有更高业务约束。实现时若 HTML 草图与安全验收冲突，以验收、安全规则和本设计为准。

## D6. 文档与测试

实现时必须同步：

- `docs/03-api-index.md`
- `docs/04-database-design.md`
- `docs/02-deployment.md`
- `docs/standards/authentication.md`
- `.env.example` / `src/backend/.env.example`
- OpenAPI / API 契约与客户端调用说明
- 前端 API base URL / 本地 Vite proxy 约定

测试至少覆盖：

- 后端登录成功、登录失败、token 缺失、token 过期、会话撤销、退出后复用 token、无后台权限访问和生产弱密码初始化拒绝。
- 前端未登录访问后台路由、登录成功进入后台、401 后回到登录入口、退出登录清理登录态。
- 前端 `/admin` 正式入口、旧 `#admin-users` 兼容入口和首页 CTA 进入后台入口。
- 前端登录/退出请求使用 `VITE_API_BASE_URL` 拼接后端地址，避免本地开发请求误打到 Web dev server。
- 前端展示后端受控登录失败详情，并在临时密码弹窗提示后台登录前提。
- 前端密码显示/隐藏按钮、登录按钮 disabled/loading 和错误反馈状态。
- `/api/v1/admin/**` 不再接受 `x-admin-role: admin` 作为正式鉴权绕过。
