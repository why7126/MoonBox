---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
created_at: 2026-08-09 23:12:33
updated_at: 2026-08-09 23:12:33
category: deployment/config
---

# 根因分析

## 直接原因

Docker Web 镜像使用 nginx 默认静态站配置，仅将 `/usr/share/nginx/html` 作为静态资源目录，没有配置 `/api/` 反向代理到后端服务，也没有配置 SPA fallback。

因此：

- 浏览器从 Web 服务发出的 `/api/v1/admin/auth/login` 被 nginx 当作静态文件路径处理，返回 404。
- 浏览器直接访问 `/admin` 时，nginx 尝试查找 `/usr/share/nginx/html/admin`，返回 404。

## 根本原因

部署链路中没有统一明确 Docker Web 的 API 访问策略：

- 前端代码支持通过 `VITE_API_BASE_URL` 拼接后端地址，但该变量属于 Vite 构建期变量。
- `docker-compose.yml` 将 `VITE_API_BASE_URL` 写入 Web 容器运行期环境变量，容易让维护者误以为运行期配置会改变已构建的静态 JS bundle。
- 本地 Vite dev 通过 `vite.config.ts` 配置了 `/api` proxy，但 Docker nginx 没有提供等价能力，导致 dev 与 Docker 行为不一致。
- `scripts/docker-up.sh` 对 `VITE_API_BASE_URL` 做端口一致性校验，进一步强化了 Docker 默认依赖浏览器侧 API base URL 的误解。

## 触发条件

- 使用 Docker Compose 启动 Web 静态服务。
- 前端登录请求使用同源相对路径 `/api/v1/admin/auth/login`。
- Web nginx 未配置 `/api/` 代理和 SPA fallback。
- 用户直接访问或刷新 `/admin`，或在管理后台登录页提交登录。

## 已验证事实

- 后端健康检查 `http://localhost:18101/health` 返回 200。
- 后端登录接口 `http://localhost:18101/api/v1/admin/auth/login` 使用 `admin / Admin123!` 返回 200。
- Web 同源登录路径 `http://localhost:18102/api/v1/admin/auth/login` 返回 404。
- Web 直达路径 `http://localhost:18102/admin` 返回 404。
- 容器内 nginx 默认配置只有 `location /` 静态目录配置，没有 `/api/`、`try_files` 或 `proxy_pass`。

## 分类

- 缺陷类型：部署配置缺陷
- 影响层级：Web Docker 入口、nginx 静态托管、管理后台 API 访问链路
- 非根因：管理员账号、密码哈希、后端认证接口、数据库种子数据
