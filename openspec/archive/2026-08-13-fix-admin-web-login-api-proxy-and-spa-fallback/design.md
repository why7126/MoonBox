---
created_at: 2026-08-09 23:24:11
updated_at: 2026-08-09 23:24:11
---

# 设计说明

## 根因

Docker Web 镜像当前使用 nginx 默认静态配置，只声明 `location /` 静态目录。前端管理后台登录请求使用相对路径 `/api/v1/admin/auth/login` 时，请求落在 Web 服务 origin `localhost:18102`，nginx 没有 `/api/` 反向代理，因此尝试读取 `/usr/share/nginx/html/api/v1/admin/auth/login` 并返回 404。

同时，nginx 没有 `try_files $uri $uri/ /index.html`，导致 `/admin` 直达或刷新时被当作静态路径处理并返回 404。

## 修复方案

### Web nginx 配置

新增 `src/web/nginx.conf`，在 Web 镜像中替换默认配置：

- `location /api/` 代理到 `http://backend:8000`。
- 保留 Host、X-Real-IP、X-Forwarded-* 头，便于后端日志和后续部署追踪。
- `location /` 使用 `try_files $uri $uri/ /index.html` 支持 SPA fallback。

### Docker 与 Vite API Base URL

Docker 默认路径采用同源 `/api` + nginx 反代，不再把 `VITE_API_BASE_URL` 作为 Web 容器运行期必需变量。

保留前端代码中对 `VITE_API_BASE_URL` 的可选支持，用于本地 Vite dev 或前后端分域部署；但 Docker 静态 Web 镜像不依赖运行期 `VITE_API_BASE_URL`。`scripts/docker-up.sh` 不再为 Docker 默认路径强制生成或校验 `VITE_API_BASE_URL` 与后端宿主机端口一致。

### 文档同步

更新 `docs/02-deployment.md`、`.env.example` 或相关示例说明：

- Docker Web 默认通过同源 `/api` 访问后端。
- `VITE_API_BASE_URL` 是构建期/开发期可选配置，不是静态 Web 容器运行期配置。
- 前后端分域部署时必须明确 API base URL 的生效机制。

## 测试策略

- Docker 构建与启动：`bash scripts/docker-up.sh self-storage-sqlite`。
- Web 同源 API：`POST http://localhost:18102/api/v1/admin/auth/login` 使用 `admin / Admin123!` 返回 200。
- 后端直连 API：`POST http://localhost:18101/api/v1/admin/auth/login` 返回 200。
- SPA fallback：`GET http://localhost:18102/admin` 返回 `index.html`。
- 浏览器回归：管理后台登录页输入 `admin / Admin123!` 后进入后台页面。
- 配置回归：确认 Docker Web 镜像 nginx 配置包含 `/api/` 代理和 `try_files` fallback。

## 风险

- 若 nginx proxy 路径处理不当，可能造成 `/api` 前缀丢失或重复。
- 若仍保留运行期 `VITE_API_BASE_URL` 强校验，会继续造成配置语义混乱。
- 若仅修复 `/api` 代理而漏掉 SPA fallback，`/admin` 刷新和直达仍会失败。

