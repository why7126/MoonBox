---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
review_result: approved
reviewed_at: 2026-08-11 08:31:11
reviewer: user
created_at: 2026-08-11 08:31:11
updated_at: 2026-08-11 08:31:11
---

# 缺陷评审

## 评审结论

批准修复。该问题为官网首页核心 CTA 的前台路由语义缺陷，当前实现进入 `/#login` hash 视图，不符合 `/login` 独立登录页预期。

## 评审清单

- [x] 可复现或根因充分：已确认首页登录入口由 `#login` hash 状态控制，应用级路由未识别 `/login`。
- [x] 严重等级合理：`medium`，不阻断服务或后端接口，但影响官网核心 CTA URL 语义、直达访问和测试治理。
- [x] 回归验收明确：已覆盖首页 CTA、顶部入口、直接访问 `/login`、返回首页、登录提交后进入 `/requirements`。
- [x] 是否需 hotfix 路径：不需要 hotfix，按常规 Sprint 修复。

## 决策

- 状态：`approved`
- 阶段迁移：`plan` → `review`
- 下一步：先纳入 Sprint，再创建 BUG 修复 OpenSpec Change。
