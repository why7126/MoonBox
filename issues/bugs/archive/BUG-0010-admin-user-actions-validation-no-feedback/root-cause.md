---
bug_id: BUG-0010-admin-user-actions-validation-no-feedback
created_at: 2026-08-13 09:29:45
updated_at: 2026-08-13 09:29:45
---

# 根因分析

## 直接原因

用户管理页的前端表单校验把不可见或不可操作的失败条件静默挂在按钮禁用和 early return 上，导致管理员点击「保存」或「确认」时看不到错误原因。

## 根本原因

1. 编辑用户弹窗复用了新增用户的 `username` 正则校验。编辑态下用户名不可编辑，后端更新接口也不接收 `username`，但前端保存按钮和提交逻辑仍受 `validUsername` 影响。
2. 用户操作确认弹窗通过 `disabled={reason.trim().length < 4}` 阻断提交，同时错误文案只在 `reason.length > 0 && reason.trim().length < 4` 时展示。空原因场景既不能提交，也不会显示错误。

## 触发条件

- 编辑保存：已有用户的 `username` 不满足当前前端新增用户校验规则，或未来出现兼容历史账号、迁移账号、外部导入账号等情况。
- 确认操作：重置密码、冻结、解冻、删除弹窗中，操作原因为空或只包含空白字符。

## 缺陷分类

- 分类：frontend / validation / UX feedback
- 影响层：管理后台用户管理页
- 后端约束：`AdminUserUpdate` 不要求 `username`；`AdminUserAction.reason` 要求最少 4 个字符，约束本身合理。

## 修复方向

- 编辑态只校验可编辑字段；用户名正则仅用于新增用户。
- 确认弹窗应在空原因或不足 4 个字时显示可见错误；避免以静默 disabled 作为唯一反馈。
- 错误信息应使用现有 `.admin-form-error` 样式，并具备 `aria-live` 或等价可访问性反馈。
