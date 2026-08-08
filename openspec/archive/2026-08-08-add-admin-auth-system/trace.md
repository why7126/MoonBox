---
change_id: add-admin-auth-system
status: archived
type: add
source_requirement: REQ-0005-admin-auth-system
sprint: sprint-001
created_at: 2026-08-07 23:53:12
updated_at: 2026-08-08 23:23:52
---

# Change Trace

## 来源

- REQ：`issues/requirements/archive/REQ-0005-admin-auth-system/`
- Sprint：`iterations/archive/sprint-001/`
- 类型：add

## 影响面

```yaml
impact:
  backend: true
  web: true
  admin: true
  database: true
  storage: false
  api: true
  security: true
capabilities:
  new:
    - web-admin-auth-system
  modified:
    - api-governance
    - database-compatibility
    - deployment-governance
```

## 原型检查

- `issues/requirements/review/REQ-0005-admin-auth-system/prototype/web/prototype.html`：后台登录页结构草图。
- PNG：无，非阻塞。
- 冲突结论：无冲突；实现以验收、安全规则和 `design.md` 为准。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-08 22:35:00 | opsx.modify | 验收返修：调整管理后台登录页密码显示/隐藏按钮垂直居中；1440x900 视觉验收中密码输入框与按钮中心线差值 0px。 |
| 2026-08-08 20:48:00 | opsx.modify | 验收返修：管理后台正式入口改为 `/admin` 并兼容旧 `#admin-users`，首页 CTA 进入后台入口，登录页增加密码显隐、按钮状态和错误反馈样式优化。 |
| 2026-08-08 10:38:00 | opsx.modify | 验收返修：登录失败展示后端受控错误详情；临时密码弹窗提示仅状态正常的后台管理员账号可用临时密码登录后台。 |
| 2026-08-08 10:29:47 | opsx.modify | 验收返修：后端启用 FastAPI CORS 中间件并读取 `BACKEND_CORS_ORIGINS`，修复后台登录预检 OPTIONS 405 导致的浏览器 NetworkError。 |
| 2026-08-08 10:13:58 | opsx.modify | 验收返修：后端 Docker 镜像改为按 `pyproject.toml` 安装完整依赖，SQLite engine 创建前自动创建数据库父目录，并将 backend healthcheck 改为 Python 标准库请求，修复后台登录 API 容器重启和前端 NetworkError。 |
| 2026-08-08 00:25:00 | opsx.modify | 验收返修：管理后台登录/退出请求改用 `VITE_API_BASE_URL` 拼接后端 API，并增加 Vite `/api` 开发代理兜底与前端测试断言。 |
| 2026-08-08 00:13:21 | opsx.apply | 完成实现、测试和文档同步，Change 待验收与 archive。 |
| 2026-08-07 23:53:12 | req.opsx | 从 REQ-0005 创建 OpenSpec Change |
