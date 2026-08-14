---
change_id: fix-admin-user-actions-validation-feedback
acceptance_status: passed
created_at: 2026-08-13 09:38:58
updated_at: 2026-08-13 09:53:24
---

# Acceptance

## 验收范围

- `BUG-0010` 的 6 条验收标准全部覆盖。
- 用户管理页新增用户、编辑用户、重置密码、冻结、解冻、删除流程不回归。

## 验收项

- 编辑已有异常用户名用户时，可保存昵称、头像或角色等可编辑字段。
- 新增用户时，非法用户名仍展示明确错误并阻断提交。
- 空操作原因点击确认时展示错误提示。
- 短操作原因展示错误提示并不调用对应 API。
- 重置密码、冻结、解冻、删除确认弹窗的“操作原因”均展示红色 `*` 必填标识，且 `*` 紧跟字段名同一行展示。
- 合法操作原因仍调用对应 API，并保持既有成功反馈。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: "2026-08-13 09:44:44"
evidence:
  - command: "pnpm --dir src/web test -- admin-user-management.test.tsx --run"
    result: "passed, 6 files / 78 tests"
  - command: "pnpm --dir src/web build"
    result: "passed"
  - command: "pnpm --dir src/web test -- admin-user-management.test.tsx --run"
    result: "passed, 6 files / 79 tests, includes required reason marker coverage"
  - command: "pnpm --dir src/web build"
    result: "passed after opsx.modify"
  - command: "pnpm --dir src/web test -- admin-user-management.test.tsx --run"
    result: "passed, required star inline style covered"
  - command: "pnpm --dir src/web build"
    result: "passed after inline star modify"
failed_items: []
```
