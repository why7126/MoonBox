---
bug_id: BUG-0004-frontend-user-menu-change-password-not-implemented
created_at: 2026-08-11 16:12:20
updated_at: 2026-08-11 16:12:20
classification: code
---

# 根因分析

## 直接原因

前台需求中心用户菜单中的“修改密码”按钮只绑定了 `onMouseEnter={closeSpacePopoverNow}`，没有绑定 `onClick` 处理函数。点击该菜单项时，React 不会打开修改密码弹窗，也不会调用密码修改 API。

## 根本原因

修改密码能力已经在后台用户管理页实现，但该能力没有抽取为前后台可复用的账号安全组件。前台用户菜单在补齐菜单视觉项时只覆盖了图标和文案存在性，未把“修改密码”纳入前台交互状态、弹窗渲染和会话清理闭环。

## 触发条件

- 用户已登录前台并进入需求中心页面。
- 用户打开左侧底部前台用户菜单。
- 用户点击“修改密码”菜单项。

## 证据

- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：前台“修改密码”按钮没有 `onClick`。
- `src/web/src/pages/admin/AdminUserManagementPage.tsx`：后台已有 `ChangePasswordModal`，可提交当前密码、新密码和确认新密码。
- `src/web/src/pages/admin/adminAuth.ts`：已有 `changeAdminPassword`，会调用 `/api/v1/admin/auth/change-password` 并清理后台 session。
- `src/backend/app/api/v1/admin_auth.py`：后端已提供 `/api/v1/admin/auth/change-password`。
- `src/web/src/requirement-center.test.tsx`：当前仅断言“修改密码”菜单图标存在，未覆盖点击打开弹窗和提交改密。

## 分类

- 类型：code / frontend-menu-wiring
- 修复面：Web 前台需求中心用户菜单、账号安全弹窗复用、前台会话清理、前台测试
- 非修复面：后端接口、数据库结构、对象存储、部署反向代理
