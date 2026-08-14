---
bug_id: BUG-0011-admin-user-list-enum-time-display-unclear
created_at: 2026-08-13 09:32:22
updated_at: 2026-08-13 09:32:22
classification: ui
---

# 根因分析

## 直接原因

用户管理列表的表格渲染仍沿用早期字段直出方式：

- 角色列直接输出 `user.role`，没有使用角色标签组件或专用样式。
- 状态列统一使用 `.admin-status`，仅依赖文本和小圆点颜色表达状态语义。
- 最近登录时间和创建时间直接渲染字段值，没有统一格式化入口。
- 列定义和 `colgroup` 未包含 `updated_at` 对应的更新时间列。

## 根本原因

后台用户列表的 UI contract 没有把枚举字段、状态语义和审计时间字段固化为验收约束；后续接口和类型补齐 `updated_at` 后，前端列表没有同步更新展示列和测试断言。

空间管理页已有更新时间展示和 `formatDate` 类似处理方式，但用户管理页没有复用或抽取同类展示策略，导致两个后台管理列表在时间展示和审计字段上不一致。

## 触发条件

满足以下条件时稳定出现：

1. 进入管理后台用户管理页。
2. 用户列表接口返回至少一个包含 `role`、`status`、`last_login_at`、`created_at`、`updated_at` 的用户。
3. 查看角色、状态、最近登录时间、创建时间和更新时间相关列。

## 分类

- 类型：UI 展示缺陷。
- 层级：Web 前端。
- 数据边界：后端列表查询和响应 schema 已包含 `updated_at`，暂未发现数据库或接口缺字段。
- 测试缺口：现有用户管理页单测覆盖当前列顺序，且未断言更新时间列、角色标签、状态语义或统一时间格式。

## 关联证据

- `src/web/src/pages/admin/AdminUserManagementPage.tsx` 的 `AdminUser` 类型包含 `updated_at`。
- 用户列表列定义缺少「更新时间」。
- 用户列表渲染中角色、状态和时间字段为直出。
- `src/backend/app/repositories/admin_users.py` 的 `list_users` 查询已 SELECT `updated_at`。
- `src/backend/app/schemas/admin_users.py` 的 `AdminUserRead` 已声明 `updated_at`。
