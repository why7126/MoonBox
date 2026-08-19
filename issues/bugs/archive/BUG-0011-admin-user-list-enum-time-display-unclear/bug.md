---
bug_id: BUG-0011-admin-user-list-enum-time-display-unclear
title: 用户管理列表枚举标签与时间字段展示不清晰
severity: medium
status: done
owner:
discovered_at: 2026-08-13 09:22:20
environment: local
related_requirement:
related_change: fix-admin-user-list-enum-time-display
created_at: 2026-08-13 09:30:17
updated_at: 2026-08-15 10:13:22
---

# 现象

管理后台用户管理列表中，用户角色、状态和时间字段的展示语义不够清晰：

- 角色字段作为枚举值直接以纯文本渲染，缺少标签化表达。
- 状态字段主要依赖统一的 `.admin-status` 文本与小圆点颜色区分，不同状态的图标或视觉语义不足，冻结和删除类状态的识别度接近。
- 最近登录时间和创建时间直接输出接口字符串，缺少统一的 `yyyy-mm-dd hh:mm:ss` 展示策略。
- 后端列表响应和前端类型均已有 `updated_at` 字段，但用户列表未展示更新时间列。

# 复现步骤

1. 启动本地环境并登录管理后台。
2. 进入用户管理页。
3. 查看用户列表中的角色、状态、最近登录时间和创建时间列。
4. 对比不同用户状态的视觉标识，检查角色是否以标签形式展示。
5. 检查列表是否在创建时间后展示更新时间。

# 期望结果

- 角色字段应以稳定的标签样式展示，便于快速区分后台管理员和前台用户。
- 状态字段应通过清晰的图标、标签语义或明显样式区分待激活、正常、已冻结、已删除等状态。
- 最近登录时间、创建时间和更新时间应统一格式化为 `yyyy-mm-dd hh:mm:ss`；无值时展示 `—`。
- 用户列表应展示更新时间，方便管理员判断账号最近变更。

# 实际结果

- 角色字段仅展示纯文本。
- 状态字段统一使用 `.admin-status`，主要通过伪元素圆点颜色区分，语义弱。
- 最近登录时间和创建时间直接渲染字段值。
- `updated_at` 已存在于后端响应和前端类型中，但未出现在列表列定义和表格单元格中。

# 影响范围

- 影响端：管理后台 Web 端。
- 影响页面：用户管理列表。
- 影响用户：后台管理员、平台超级管理员等需要查看或维护用户状态的管理角色。
- 影响能力：用户状态识别、角色识别、账号变更审计和列表扫描效率。

# 严重等级说明

严重等级评估为 `medium`。该问题不阻断登录、查询、编辑、冻结、解冻、删除或重置密码等核心操作，也未发现接口字段缺失或数据损坏；但会降低后台用户列表的可读性和审计判断效率，容易导致管理员误读账号状态或遗漏最近变更信息。

# 初步定位证据

- `src/web/src/pages/admin/AdminUserManagementPage.tsx` 中 `AdminUser` 类型已声明 `updated_at`。
- 用户列表列定义包含「用户、空间数、角色、状态、冻结前状态、最近登录时间、创建时间、操作」，未包含「更新时间」。
- 用户列表渲染中角色字段直接输出 `user.role`，状态字段直接输出 `.admin-status ${user.status}`，时间字段直接输出 `user.last_login_at` 和 `user.created_at`。
- `src/backend/app/repositories/admin_users.py` 的列表查询已 SELECT `updated_at`。
- `src/backend/app/schemas/admin_users.py` 的 `AdminUserRead` 已包含 `updated_at`。
