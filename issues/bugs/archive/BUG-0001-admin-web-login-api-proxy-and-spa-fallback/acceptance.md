---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
acceptance_status: passed
created_at: 2026-08-09 23:12:33
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 Docker Web 登录 API 代理正确

在 Docker Compose 本地环境中，请求 `http://localhost:18102/api/v1/admin/auth/login` 使用 `admin / Admin123!` 登录时，必须由 Web nginx 转发到后端服务并返回 200。

## AC-002 管理后台登录页面可完成登录

在浏览器访问 Docker Web 管理后台登录页，输入 `admin / Admin123!` 后，应成功进入管理后台，不得展示“登录失败，请稍后重试。”。

## AC-003 SPA 路由直达与刷新可用

直接访问或刷新 `http://localhost:18102/admin` 时，Web nginx 必须返回 SPA 入口页面，前端路由应展示管理后台登录页或已登录管理后台。

## AC-004 Docker 默认不依赖 VITE_API_BASE_URL

Docker 默认部署路径下，Web 登录能力不得依赖运行期 `VITE_API_BASE_URL`。`VITE_API_BASE_URL` 应仅作为本地 Vite dev 或前后端分域部署的可选配置。

## AC-005 部署脚本与文档语义一致

Docker 启动脚本和部署文档必须同步说明：

- Docker Web 默认采用同源 `/api` + nginx 反代。
- `VITE_API_BASE_URL` 不是 Docker 静态 Web 容器运行期必需配置。
- 若使用前后端分域部署，必须在构建期或运行时配置机制中明确 API base URL 生效方式。

## 回归验证建议

- 运行 Docker Compose 构建并启动 backend、web、minio。
- 使用 HTTP 请求验证 Web 同源 `/api/v1/admin/auth/login` 返回 200。
- 使用浏览器验证 `/admin` 直达、刷新和登录成功。
- 验证后端直连登录仍返回 200。
- 检查 nginx 配置中存在 `/api/` 反向代理和 SPA fallback。


## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-admin-web-login-api-proxy-and-spa-fallback
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

