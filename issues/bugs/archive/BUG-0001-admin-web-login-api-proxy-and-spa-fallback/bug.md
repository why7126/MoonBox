---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
title: Docker Web 管理后台登录 API 误路由且缺少 SPA fallback
severity: high
status: done
owner:
discovered_at: 2026-08-09 23:04:45
environment: docker
related_requirement:
related_change:
created_at: 2026-08-13 22:45:09
updated_at: 2026-08-13 22:45:09
---

# 现象

Docker Compose 本地环境中，Web 管理后台使用 `admin / Admin123!` 登录时，页面提示“登录失败，请稍后重试。”。相同账号密码直连后端 API 登录成功，说明认证数据与密码本身有效。

同时，直接访问或刷新 `/admin` 路径会返回 nginx 404，而不是回退到 SPA 入口页面。

# 复现步骤

1. 使用 Docker Compose 启动本地环境。
2. 访问 Web 服务入口 `http://localhost:18102`，进入管理后台登录页面。
3. 输入用户名 `admin`、密码 `Admin123!` 并提交登录。
4. 观察页面提示“登录失败，请稍后重试。”。
5. 直接请求 Web 同源 API 路径 `http://localhost:18102/api/v1/admin/auth/login`，返回 404。
6. 直接请求后端 API 路径 `http://localhost:18101/api/v1/admin/auth/login`，相同账号密码返回 200。
7. 直接访问 `http://localhost:18102/admin`，返回 404。

# 期望结果

- Docker Web 管理后台登录请求应稳定命中后端 API。
- Docker Web 环境下前端相对路径 `/api/...` 应由 nginx 反向代理到后端服务。
- `/admin` 直达、刷新或分享链接访问时应返回 SPA 入口并展示管理后台路由。
- Docker 默认部署不应依赖构建期 `VITE_API_BASE_URL` 才能完成登录。

# 实际结果

- Web 静态包中的管理后台登录请求使用相对路径 `/api/v1/admin/auth/login`。
- nginx 默认配置仅托管静态文件，没有 `/api/` 反向代理。
- 登录请求被 nginx 当作静态文件路径处理，返回 404。
- nginx 默认配置没有 SPA fallback，`/admin` 被当作静态文件路径处理并返回 404。
- 前端读取不到后端 JSON 错误体，最终展示兜底错误“登录失败，请稍后重试。”。

# 影响范围

- Docker Web 管理后台登录不可用。
- 所有通过 Web 同源相对路径访问的 `/api/v1/admin/**` 接口都会被误路由到 nginx 静态目录。
- `/admin` 直达、浏览器刷新、书签访问和外部链接访问均不可用。
- 由于前端兜底错误过于泛化，用户容易误判为账号密码错误或认证服务异常。

# 严重等级说明

严重等级为 `high`。该问题阻断 Docker 本地环境中的管理后台登录主流程，影响管理后台入口可用性；后端认证接口本身可用，因此不属于全系统不可用或数据破坏类 blocker。

# 修复方向

- 为 Web nginx 增加 `/api/` 反向代理，将请求转发到 Docker Compose 网络内的 `backend:8000`。
- 为 Web nginx 增加 SPA fallback，使 `/admin` 等前端路由回退到 `index.html`。
- 将 `VITE_API_BASE_URL` 从 Docker 默认必需配置降级为本地 Vite dev 或前后端分域部署的可选配置。
- 调整 Docker 启动脚本和部署文档，避免运行期环境变量被误认为会改变已构建的 Vite 静态 bundle。
