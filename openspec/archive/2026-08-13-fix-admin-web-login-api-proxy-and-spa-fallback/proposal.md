---
created_at: 2026-08-09 23:24:11
updated_at: 2026-08-09 23:24:11
---

# 修复 Docker Web 管理后台登录 API 代理与 SPA fallback

## 背景

`BUG-0001-admin-web-login-api-proxy-and-spa-fallback` 已确认：Docker Web 管理后台使用 `admin / Admin123!` 登录时，前端同源请求 `/api/v1/admin/auth/login` 被 nginx 当作静态文件路径处理并返回 404；直接访问 `/admin` 也返回 404。

后端认证接口直连 `http://localhost:18101/api/v1/admin/auth/login` 可正常返回 200，说明根因不在账号密码、后端认证或数据库种子，而在 Web Docker/nginx 入口配置。

## 修复依据

- BUG：`BUG-0001-admin-web-login-api-proxy-and-spa-fallback`
- Sprint：`sprint-002`
- 影响：Docker Web 管理后台登录主流程不可用，`/admin` 直达与刷新不可用。

## 目标

- Web nginx 在 Docker 默认路径中代理 `/api/` 到后端 `backend:8000`。
- Web nginx 对 `/admin` 等 SPA 前端路由提供 fallback 到 `index.html`。
- Docker 默认部署不再依赖运行期 `VITE_API_BASE_URL` 才能完成 Web 管理后台登录。
- 启动脚本、Compose 配置和部署文档同步说明 `VITE_API_BASE_URL` 仅作为本地 Vite dev 或分域部署可选配置。
- 补充回归验证，覆盖 Web 同源 API、后端直连 API、`/admin` 直达和登录主流程。

## 非目标

- 不修改后端认证语义、账号密码策略、会话模型或数据库 schema。
- 不新增管理后台业务页面。
- 不改变 `/api/v1/admin/auth/login` 的请求或响应契约。
- 不引入运行时前端配置服务。

## 回滚计划

若 nginx 代理或 fallback 引入异常：

1. 回滚 `src/web/nginx.conf` 和 `src/web/Dockerfile` 中的 nginx 配置接入。
2. 回滚 `docker-compose.yml` 与 `scripts/docker-up.sh` 中对 `VITE_API_BASE_URL` 语义的调整。
3. 重新构建 Web 镜像，验证静态首页仍可访问。
4. 保留后端认证接口直连验证作为回退诊断入口。
