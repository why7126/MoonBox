---
bug_id: BUG-0001-admin-web-login-api-proxy-and-spa-fallback
review_result: approved
reviewed_at: 2026-08-09 23:15:49
reviewer: user
decision: approve
---

# 评审结论

确认修复。

## 评审清单

- [x] 可复现或根因充分
- [x] 严重等级合理
- [x] 回归验收明确
- [x] 已评估是否需要 hotfix 路径

## 判断

该缺陷在 Docker Web 环境中稳定复现，直接影响管理后台登录主流程和 `/admin` 直达能力。根因定位为 Web nginx 缺少 `/api/` 反向代理与 SPA fallback，修复范围明确，验收标准可执行。

严重等级保持 `high`，优先级保持 `P1`。该问题阻断 Docker 环境管理后台使用，但后端认证能力本身可用，因此不升级为 blocker。

## 后续要求

- 必须先纳入 Sprint，再创建修复 OpenSpec Change。
- 修复应覆盖 Web nginx 配置、Docker 启动脚本和部署文档。
- `VITE_API_BASE_URL` 在 Docker 默认路径中应降级为可选开发或分域部署配置，不作为静态 Web 容器运行期必需项。
