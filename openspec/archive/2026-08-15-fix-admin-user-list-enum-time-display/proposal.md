---
change_id: fix-admin-user-list-enum-time-display
type: fix
status: applied
created_at: 2026-08-15 09:24:03
updated_at: 2026-08-15 09:30:17
source_bug: BUG-0011-admin-user-list-enum-time-display-unclear
sprint: sprint-003
owner: MoonBox 产品团队
---

# Proposal: 修复用户管理列表枚举标签与时间字段展示不清晰

## 背景

`BUG-0011-admin-user-list-enum-time-display-unclear` 已确认管理后台用户列表存在展示缺陷：

- 角色字段直接以纯文本展示，缺少标签化视觉表达。
- 状态字段主要依赖统一 `.admin-status` 和小圆点颜色区分，冻结、删除等状态语义不够清晰。
- 最近登录时间和创建时间直接输出字段值，缺少统一 `yyyy-mm-dd hh:mm:ss` 展示策略。
- 后端列表响应和前端类型已有 `updated_at`，但列表未展示更新时间。

根因证据已在 BUG `root-cause.md` 中确认：后端查询、API schema 和前端类型均具备 `updated_at`，问题集中在 Web 管理后台用户列表 UI contract 和表格渲染。

## 变更内容

- 在管理后台用户列表中增加角色标签展示。
- 为用户状态建立更清晰的语义标签、图标或状态样式映射。
- 增加统一时间格式化策略，覆盖最近登录时间、创建时间和更新时间。
- 在创建时间后增加「更新时间」列，并同步表格列宽、横向滚动密度和回归测试。
- 不修改后端 API、数据库结构或认证权限边界。

## 影响范围

- 影响模块：Web 管理后台用户管理页。
- 影响文件预计：`src/web/src/pages/admin/AdminUserManagementPage.tsx`、`src/web/src/styles/globals.css`、`src/web/src/admin-user-management.test.tsx`。
- API/DB：无契约变更；仅消费既有 `updated_at` 字段。
- 测试：必须补充用户管理页前端回归测试。

## 回滚计划

如修复后出现表格布局溢出、列遮挡或状态标签可读性问题：

1. 回退用户列表列定义、状态/角色标签渲染和 CSS 变更。
2. 保留后端和 API 不动，因为本 Change 不修改接口契约。
3. 重新运行 `pnpm --dir src/web test src/admin-user-management.test.tsx` 确认回退后现有用户管理页行为稳定。
