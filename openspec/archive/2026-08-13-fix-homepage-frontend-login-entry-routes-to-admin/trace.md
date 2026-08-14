---
change_id: fix-homepage-frontend-login-entry-routes-to-admin
type: fix
status: applied
created_at: 2026-08-10 22:23:07
updated_at: 2026-08-10 23:34:40
source_bug: BUG-0002-homepage-frontend-login-entry-routes-to-admin
source_requirement: null
source_sprint: sprint-002
---

# Change Trace

## 基本信息

| 字段 | 值 |
|---|---|
| Change | fix-homepage-frontend-login-entry-routes-to-admin |
| 类型 | fix |
| 状态 | applied |
| 来源 BUG | BUG-0002-homepage-frontend-login-entry-routes-to-admin |
| 所属 Sprint | sprint-002 |

## 影响范围

- Web 前台首页 CTA 路由。
- Web 前台登录页展示状态。
- 管理后台明确入口回归测试。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-10 23:34:40 | opsx.modify | 验收反馈明确期望进入前台工作台或需求中心；已将前台登录原型提交调整为进入 `/requirements`，保持不发真实认证请求和不跳 `/admin`。 |
| 2026-08-10 23:18:20 | opsx.modify | 验收反馈指出前台登录提交静默无响应；已补充原型反馈，保持不发真实认证请求和不跳 `/admin`。 |
| 2026-08-10 22:58:04 | opsx.apply | 完成首页 CTA 前台登录入口修复、回归测试和构建验证。 |
| 2026-08-10 22:23:07 | bug.opsx | 从 BUG-0002 创建前端路由修复 Change。 |

## 验证记录

| 时间 | 命令 | 结果 |
|---|---|---|
| 2026-08-10 22:58:04 | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx` | 通过：5 个测试文件，39 个用例通过；首页 CTA 打开前台登录页，后台路由测试保留。 |
| 2026-08-10 22:58:04 | `pnpm --dir src/web build` | 通过：TypeScript 与 Vite 构建成功。 |
| 2026-08-10 22:58:04 | `openspec validate fix-homepage-frontend-login-entry-routes-to-admin --strict` | 通过。 |
| 2026-08-10 23:18:20 | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx` | 通过：5 个测试文件，39 个用例通过；登录提交显示原型反馈且不请求后端。 |
| 2026-08-10 23:18:20 | `pnpm --dir src/web build` | 通过：TypeScript 与 Vite 构建成功。 |
| 2026-08-10 23:18:20 | `openspec validate fix-homepage-frontend-login-entry-routes-to-admin --strict` | 通过。 |
| 2026-08-10 23:18:20 | `git diff --check -- <touched-files>` | 通过。 |
| 2026-08-10 23:34:40 | `pnpm --dir src/web test -- homepage.test.tsx admin-auth.test.tsx` | 通过：5 个测试文件，39 个用例通过；登录提交进入 `/requirements` 且不请求后端。 |
| 2026-08-10 23:34:40 | `pnpm --dir src/web build` | 通过：TypeScript 与 Vite 构建成功。 |
| 2026-08-10 23:34:40 | `openspec validate fix-homepage-frontend-login-entry-routes-to-admin --strict` | 通过。 |
| 2026-08-10 23:34:40 | `git diff --check -- <touched-files>` | 通过。 |
