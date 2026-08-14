---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
status: done
lifecycle_stage: archive
created_at: 2026-08-09 23:04:45
updated_at: 2026-08-13 22:45:09
severity_hint: high
priority: P1
environment: docker
related_requirement:
related_bug:
related_change: fix-admin-web-login-api-proxy-and-spa-fallback
iteration: sprint-002
---

# 追踪

```yaml
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
status: done
lifecycle_stage: archive
severity_hint: high
priority: P1
environment: docker
related_requirement:
related_bug:
related_change: fix-admin-web-login-api-proxy-and-spa-fallback
iteration: sprint-002
openspec_changes:
  - change_id: fix-admin-web-login-api-proxy-and-spa-fallback
    type: fix
    status: archived
```

## 修复方向

- 采用同源 `/api` 请求路径，由 Web nginx 将 `/api/` 反向代理到后端 `backend:8000`。
- 为 Web nginx 增加 SPA fallback，确保 `/admin` 直达和刷新返回 `index.html`。
- 将 `VITE_API_BASE_URL` 从 Docker 默认必需配置降级为可选开发或分域部署配置；Docker 默认不依赖构建期 API base URL。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:45:09 | /opsx-archive | Change `fix-admin-web-login-api-proxy-and-spa-fallback` 已归档，状态同步完成。 |
| 2026-08-10 08:24:53 | /opsx-apply | Change `fix-admin-web-login-api-proxy-and-spa-fallback` apply 完成，待 archive。 |
| 2026-08-09 23:04:45 | bug.capture | 捕获 Docker Web 管理后台登录 API 误路由与 SPA fallback 缺失问题。 |
| 2026-08-09 23:10:25 | bug.generate | 生成缺陷正文 bug.md，状态推进为 draft。 |
| 2026-08-09 23:12:33 | bug.complete | 补齐 root-cause、workaround、acceptance，状态推进为 pending_review。 |
| 2026-08-09 23:15:49 | bug.review | 评审通过，确认修复。 |
| 2026-08-09 23:20:31 | sprint.propose | 归档前纳入 sprint-002。 |
| 2026-08-09 23:24:11 | bug.opsx | 创建 OpenSpec Change `fix-admin-web-login-api-proxy-and-spa-fallback`。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:41:26 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive BUG-0001-admin-web-login-api-proxy-and-spa-fallback
