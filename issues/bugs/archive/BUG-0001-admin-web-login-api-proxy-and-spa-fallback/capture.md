---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
status: done
created_at: 2026-08-09 23:04:45
updated_at: 2026-08-13 22:45:16
severity_hint: high
environment: docker
related_requirement:
related_bug:
---

# 现象

Docker Web 管理后台使用 `admin / Admin123!` 登录时，页面提示“登录失败，请稍后重试。”；同一账号密码直连后端登录接口可成功。

# 复现步骤

1. 使用 Docker Compose 启动 MoonBox 本地环境。
2. 在浏览器访问 Web 管理后台入口。
3. 使用用户名 `admin`、密码 `Admin123!` 提交登录。
4. 观察登录失败提示。
5. 对比直连后端 `POST http://localhost:18101/api/v1/admin/auth/login`，相同账号密码返回成功。

# 期望 vs 实际

期望：

- Docker Web 管理后台登录请求应稳定命中后端 API。
- `/admin` 直达或刷新应返回 SPA 入口并展示管理后台页面。
- Docker 默认路径不应依赖构建期 `VITE_API_BASE_URL` 才能登录。

实际：

- 运行中的 Web 静态包将登录请求发到同源相对路径 `/api/v1/admin/auth/login`。
- Web nginx 未配置 `/api` 反向代理，请求落到静态文件路径并返回 404。
- Web nginx 未配置 SPA fallback，直接访问 `/admin` 返回 404。
- 前端未读到后端 JSON 错误体，兜底显示“登录失败，请稍后重试。”。

# 附件

- 只读排查日志摘要：
  - 后端 `http://localhost:18101/health` 返回 200。
  - 后端 `admin / Admin123!` 登录接口返回 200。
  - Web 日志出现 `POST /api/v1/admin/auth/login HTTP/1.1" 404`，并尝试打开 `/usr/share/nginx/html/api/v1/admin/auth/login`。
  - Web 入口 `GET /admin` 返回 404，nginx 尝试打开 `/usr/share/nginx/html/admin`。

