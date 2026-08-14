---
change_id: fix-homepage-frontend-login-entry-routes-to-admin
status: applied
created_at: 2026-08-10 22:23:07
updated_at: 2026-08-10 22:58:04
---

# 任务清单

## 1. 前端入口修复

- [x] 1.1 将首页「打开第一个项目」和「开启 MoonBox」的点击行为改为打开前台登录页。
- [x] 1.2 确认前台登录页打开后首页主体不作为当前主交互界面展示。
- [x] 1.3 确认点击「返回首页」后清除登录状态并恢复首页。

## 2. 后台入口边界回归

- [x] 2.1 确认直接访问 `/admin` 仍展示管理后台登录页或已登录后台。
- [x] 2.2 确认具备权限的前台用户点击「进入后台」仍进入 `/admin`。
- [x] 2.3 确认首页 CTA 不再触发管理后台登录页。

## 3. 测试与验证

- [x] 3.1 更新 `src/web/src/homepage.test.tsx`，断言两个首页 CTA 打开前台登录页且不跳 `/admin`。
- [x] 3.2 保留 `/#login` 直达、返回首页和前端原型提交不请求后端的测试。
- [x] 3.3 运行 `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx`。
- [x] 3.4 运行 `pnpm --dir src/web build`。
- [x] 3.5 运行 `openspec validate fix-homepage-frontend-login-entry-routes-to-admin --strict`。

## 4. 文档与追溯

- [x] 4.1 回填 `BUG-0002` 的验收证据与 Change 状态。
- [x] 4.2 归档前确认无需同步 API、数据库、部署、安全或客户端生成。
- [x] 4.3 若修复暴露更通用的入口路由治理经验，补充 `docs/knowledge-base/incidents/`；若无复用价值，记录不适用原因。

## 验收返修记录

### 2026-08-10 23:18:20 前台登录提交静默反馈

- [x] 修改登录页原型提交行为：点击「登录并开启宝盒」后展示明确原型反馈。
- [x] 保持前端原型边界：不发起真实认证请求，不生成 Token，不跳转 `/admin`。
- [x] 更新首页测试，断言提交后出现 `role="status"` 反馈文案。
- [x] 更新 Change 设计、验收、delta spec、BUG acceptance、Sprint 验收报告和 release note。

### 2026-08-10 23:34:40 前台登录提交进入需求中心

- [x] 按验收反馈将登录页原型提交行为从提示反馈调整为进入 `/requirements`。
- [x] 保持前端原型边界：不发起真实认证请求，不生成 Token，不跳转 `/admin`。
- [x] 更新首页测试，断言提交后路径进入前台需求中心且清除 `#login`。
- [x] 更新 Change 设计、验收、delta spec、BUG acceptance、Sprint release note 和追溯记录。
