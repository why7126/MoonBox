---
change_id: fix-admin-user-actions-validation-feedback
created_at: 2026-08-13 09:38:58
updated_at: 2026-08-13 09:53:24
---

# Test Plan

## 自动化测试

- `pnpm --dir src/web test -- admin-user-management.test.tsx --run`
- `pnpm --dir src/web build`

## 重点断言

- 编辑态保存按钮不因只读用户名不符合新增正则而禁用。
- 编辑态提交不会发送 `username` 字段，也不会因 username 校验 early return。
- 确认弹窗空原因和短原因均展示 `.admin-form-error`。
- 重置密码、冻结、解冻、删除确认弹窗的“操作原因”标签均带 `required` 标识，由现有样式渲染红色 `*`，且星号与字段名同一行紧邻展示。
- 校验失败时不调用对应用户操作 API。
- 合法原因保持重置密码弹窗和冻结/解冻/删除 toast 成功路径。

## 手工验证建议

- 在浏览器中打开用户管理页，分别验证编辑弹窗和重置密码、冻结、解冻、删除确认弹窗。
- 低视口下确认错误提示不遮挡按钮，弹窗底部操作仍可访问。

## 执行记录

| 时间 | 命令 | 结果 |
|---|---|---|
| 2026-08-13 09:43:49 | `pnpm --dir src/web test -- admin-user-management.test.tsx --run` | 通过，6 个测试文件、78 个用例通过。 |
| 2026-08-13 09:43:49 | `pnpm --dir src/web build` | 通过。 |
| 2026-08-13 09:50:43 | `pnpm --dir src/web test -- admin-user-management.test.tsx --run` | 通过，6 个测试文件、79 个用例通过。 |
| 2026-08-13 09:50:43 | `pnpm --dir src/web build` | 通过。 |
| 2026-08-13 09:53:24 | `pnpm --dir src/web test -- admin-user-management.test.tsx --run` | 通过，6 个测试文件、79 个用例通过。 |
| 2026-08-13 09:53:24 | `pnpm --dir src/web build` | 通过。 |
