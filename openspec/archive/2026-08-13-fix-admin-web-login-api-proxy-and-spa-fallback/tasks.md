---
created_at: 2026-08-09 23:24:11
updated_at: 2026-08-09 23:24:11
---

# 任务

## 1. Web nginx 与 Docker 配置

- [x] 1.1 新增 Web nginx 配置，提供 `/api/` 反向代理到 `backend:8000`。
- [x] 1.2 为 Web nginx 增加 SPA fallback，确保 `/admin` 直达和刷新返回 `index.html`。
- [x] 1.3 更新 Web Dockerfile，构建镜像时使用项目 nginx 配置。
- [x] 1.4 调整 Docker Compose Web 服务环境变量说明，Docker 默认不依赖运行期 `VITE_API_BASE_URL`。
- [x] 1.5 调整 `scripts/docker-up.sh`，移除 Docker 默认路径中对 `VITE_API_BASE_URL` 的强制生成和端口一致性校验。

## 2. 文档与规格同步

- [x] 2.1 更新 `docs/02-deployment.md`，说明 Docker Web 同源 `/api` 反代和 SPA fallback。
- [x] 2.2 更新 `.env.example`、`src/backend/.env.example` 或相关示例中的 API base URL 语义说明，如适用。
- [x] 2.3 更新 OpenSpec delta spec，覆盖 Docker Web API 代理、SPA fallback 和 `VITE_API_BASE_URL` 降级。

## 3. 回归验证

- [x] 3.1 构建并启动 Docker 本地环境。
- [x] 3.2 验证 `POST http://localhost:18102/api/v1/admin/auth/login` 使用 `admin / Admin123!` 返回 200。
- [x] 3.3 验证 `POST http://localhost:18101/api/v1/admin/auth/login` 仍返回 200。
- [x] 3.4 验证 `GET http://localhost:18102/admin` 返回 SPA 入口。
- [x] 3.5 使用浏览器验证管理后台登录成功，不再展示“登录失败，请稍后重试。”。
- [x] 3.6 运行相关测试或校验：Docker Compose config、后端认证测试、Web 构建或等价验证。

## 4. 知识沉淀

- [x] 4.1 修复完成后评估是否需要沉淀 `docs/knowledge-base/incidents/` 或部署 best-practice；若不适用，在归档说明中记录原因。
