---
bug_id: BUG-0006-frontend-login-needs-real-frontend-auth
reviewed_at: 2026-08-11 23:18:34
review_result: approve
reviewer: user
created_at: 2026-08-11 23:18:34
updated_at: 2026-08-11 23:18:34
---

# 评审结论

确认修复。该缺陷阻断普通前台用户登录，且当前实现将“登录系统”和“进入后台”绑定在后台管理员认证链路中，和产品目标不一致。

# 评审清单

- [x] 可复现或根因充分
- [x] 严重等级合理
- [x] 回归验收明确
- [x] 是否需 hotfix 路径：暂不走 hotfix，按 Sprint 纳入后进入 OpenSpec fix 流程。

# 评审说明

- 严重等级 high 合理：统一登录核心路径被阻断，并涉及认证与权限边界。
- 修复方向明确：正常或待激活用户均可统一登录，待激活首次登录后自动激活为正常，默认进入前台。
- 后台权限边界必须保留：只有后台管理员或超级管理员在前台用户菜单展示“进入后台”入口，并且进入后台及调用后台 API 时仍需服务端后台权限校验。
- 验收标准已覆盖普通前台用户、后台管理员、超级管理员、待激活自动激活、冻结/删除拒绝、前台接口鉴权和后台 API 拒绝路径。

# 下一步

按流程先纳入 Sprint，再创建 OpenSpec fix Change：

```bash
/sprint-propose --bug BUG-0006-frontend-login-needs-real-frontend-auth
```
