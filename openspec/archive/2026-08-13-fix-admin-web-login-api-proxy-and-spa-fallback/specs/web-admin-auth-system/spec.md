# web-admin-auth-system Delta

## MODIFIED Requirements

### Requirement: 后台路由守卫

系统 MUST 在管理后台前端提供路由守卫，避免未登录或登录态失效的用户继续停留在受保护后台页面。

#### Scenario: Docker Web 管理后台登录请求命中后端

- **GIVEN** Docker Web 服务和后端 API 服务均已启动
- **WHEN** 管理员在 Web 管理后台提交正确用户名和密码
- **THEN** 登录请求 MUST 命中后端 `/api/v1/admin/auth/login`
- **AND** 使用有效管理员账号密码时 MUST 成功返回登录态
- **AND** 前端不得因 Web nginx 静态 404 展示“登录失败，请稍后重试。”

