---
change_id: fix-admin-web-login-api-proxy-and-spa-fallback
status: applied
lifecycle_stage: change
created_at: 2026-08-09 23:24:11
updated_at: 2026-08-10 08:24:16
source_bug: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
sprint: sprint-002
---

# 追踪

```yaml
change_id: fix-admin-web-login-api-proxy-and-spa-fallback
status: applied
lifecycle_stage: change
source_bug: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
sprint: sprint-002
tasks_total: 15
tasks_completed: 15
```

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-09 23:24:11 | bug.opsx | 由 BUG-0001 创建 Docker Web 登录 API 代理与 SPA fallback 修复 Change。 |
| 2026-08-10 08:19:58 | opsx.apply | 已完成 Web nginx 同源 `/api` 反代、SPA fallback、Dockerfile、Compose、docker-up 脚本、部署文档与 env 示例调整；基础单元测试和 Web 构建通过。 |
| 2026-08-10 08:24:16 | opsx.apply | Docker Compose config 通过；Docker Web/Backend 镜像已构建并启动；Web 同源 `/api/v1/admin/auth/login`、后端直连登录和 `/admin` SPA fallback 均返回 200；浏览器提交 `admin` 登录成功，页面出现“用户管理”，未出现“登录失败，请稍后重试。”；相关后端、前端和 OpenSpec 校验通过。 |

## 验证记录

- `python -m pytest tests/unit/test_docker_up_script.py tests/unit/test_validate_env.py`：5 passed。
- `pnpm --dir src/web run build`：通过。
- `docker compose config --quiet`：通过。
- `docker compose up -d --build backend web`：Web 与 Backend 镜像构建并启动成功。
- `POST http://127.0.0.1:18102/api/v1/admin/auth/login`：200。
- `POST http://127.0.0.1:18101/api/v1/admin/auth/login`：200。
- `GET http://127.0.0.1:18102/admin`：200。
- 浏览器验证：`/admin` 登录后出现“用户管理”，未出现“登录失败，请稍后重试。”。
- `uv run pytest tests/integration/api/test_admin_users.py`：13 passed。
- `pnpm --dir src/web test -- --run src/admin-auth.test.tsx`：26 passed。
- `openspec validate fix-admin-web-login-api-proxy-and-spa-fallback --strict`：通过。
- `python scripts/validate-openspec-language.py`：通过。

## 知识沉淀评估

本次缺陷属于 Docker Web nginx 代理与 SPA fallback 配置缺口，部署文档、env 示例、OpenSpec delta 和脚本测试已覆盖修复后的治理语义；暂不新增 `docs/knowledge-base/incidents/` 事件文档，归档时在归档说明中保留该判断。
