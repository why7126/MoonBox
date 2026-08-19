---
bug_id: BUG-0011-admin-user-list-enum-time-display-unclear
created_at: 2026-08-13 09:32:22
updated_at: 2026-08-15 09:13:31
classification: ui
---

# 根因分析

## 根因状态

status: confirmed

## 现象

- 管理后台用户管理列表中，角色字段直接以普通文本展示，缺少标签化视觉表达。
- 状态字段使用统一 `.admin-status` 样式，主要依赖小圆点颜色区分，不同状态的语义区分不够明显。
- 最近登录时间和创建时间直接输出字段值，缺少统一 `yyyy-mm-dd hh:mm:ss` 展示策略。
- 后端和前端类型已具备 `updated_at` 字段，但列表未展示更新时间列。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:14` | `AdminUser` 类型已声明 `updated_at` 字段。 | 前端数据模型已具备更新时间字段，问题不是前端类型缺字段。 |
| E2 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:285` | 用户列表列定义包含「最近登录时间」「创建时间」「操作」，但没有「更新时间」。 | 更新时间未展示的直接原因是列表列定义缺少该列。 |
| E3 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:389` | `colgroup` 仅包含登录时间和创建时间列宽，未包含更新时间列宽。 | 表格结构未为更新时间预留列，说明 UI 结构未同步 `updated_at`。 |
| E4 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:440` | 角色单元格直接渲染 `{user.role}`。 | 角色枚举值缺少标签化渲染入口。 |
| E5 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:441` | 状态单元格统一渲染 `.admin-status ${user.status}` 并输出状态文本。 | 状态展示依赖统一样式，未为不同状态建立足够语义化的展示结构。 |
| E6 | code_path | `src/web/src/pages/admin/AdminUserManagementPage.tsx:443` | 最近登录时间和创建时间分别直接渲染 `user.last_login_at` 与 `user.created_at`。 | 时间字段没有统一格式化函数或展示策略。 |
| E7 | code_path | `src/backend/app/repositories/admin_users.py:116` | 后端用户列表查询 SELECT 了 `created_at, updated_at`。 | 后端列表查询已返回更新时间字段，问题不在 repository 查询遗漏。 |
| E8 | code_path | `src/backend/app/schemas/admin_users.py:11` | `AdminUserRead` 响应 schema 声明 `updated_at`。 | API 响应契约已包含更新时间，问题集中在前端列表渲染。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 后端列表查询未返回 `updated_at` | E7 显示 `list_users` 查询已 SELECT `updated_at`。 |
| API 响应 schema 未暴露 `updated_at` | E8 显示 `AdminUserRead` 已声明 `updated_at`。 |
| 前端类型未包含 `updated_at` 导致无法渲染 | E1 显示 `AdminUser` 类型已声明 `updated_at`。 |
| 问题需要优先修改数据库结构 | E7、E8 证明查询和响应已有字段，当前证据指向前端展示层。 |

## 已确认根因

用户管理列表的前端展示结构没有随账号审计字段和后台列表一致性要求同步演进：虽然后端查询、API schema 和前端类型均已具备 `updated_at`，但列表列定义、`colgroup` 和行渲染仍只覆盖角色纯文本、统一状态样式、最近登录时间和创建时间直出。因此该缺陷的已确认根因是 Web 管理后台用户列表 UI contract 和渲染实现缺少对枚举标签、状态语义、统一时间格式和更新时间列的明确约束与实现。

## 修复方向

- 在用户列表中为角色字段增加稳定标签样式。
- 为用户状态建立更清晰的标签语义、图标或状态样式映射，避免冻结/删除等状态只靠相近颜色区分。
- 增加统一时间格式化函数，覆盖最近登录时间、创建时间和更新时间，空值展示 `—`。
- 在创建时间后增加「更新时间」列，同步 `colgroup`、表格宽度和用户管理页单测。
- 保持后端 API/DB 不变，除非后续实现验证发现字段格式存在新证据。

## 验证闭环

- 根因证据已覆盖前端类型、列定义、表格结构、行渲染、后端查询和响应 schema。
- 后续修复必须补充或更新 `src/web/src/admin-user-management.test.tsx`，覆盖角色标签、状态语义、时间格式化和更新时间列。
- 建议修复后运行：

```bash
pnpm --dir src/web test src/admin-user-management.test.tsx
python scripts/validate-root-cause-evidence.py --bug BUG-0011-admin-user-list-enum-time-display-unclear
```
