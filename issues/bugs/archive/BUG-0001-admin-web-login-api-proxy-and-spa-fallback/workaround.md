---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
created_at: 2026-08-09 23:12:33
updated_at: 2026-08-09 23:12:33
---

# 临时规避方案

## 可用规避

在正式修复前，可使用以下方式规避：

1. 使用后端 API 直连验证账号密码：`http://localhost:18101/api/v1/admin/auth/login`。
2. 使用本地 Vite dev 服务运行 Web；`vite.config.ts` 已配置 `/api` proxy 到 `http://localhost:8000`。
3. 临时手工修改运行中 Web 容器 nginx 配置，添加 `/api/` 代理和 SPA fallback 后 reload nginx。

## 不推荐规避

- 不建议仅修改 `docker-compose.yml` 中 Web 服务的 `VITE_API_BASE_URL` 运行期环境变量；已构建的 Vite 静态 bundle 不会因此改变。
- 不建议让用户改用不同管理员密码；该问题与账号密码无关。
- 不建议在前端代码中硬编码 `http://localhost:18101`；这会削弱分环境部署能力。

## 规避风险

- 手工修改容器内 nginx 配置不可持久化，重建容器后会丢失。
- Vite dev 规避只覆盖本地开发，不覆盖 Docker 演示、验收和生产静态部署。
- 直连后端 API 只能验证认证能力，不能恢复管理后台 UI 主流程。
