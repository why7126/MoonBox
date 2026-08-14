---
change_id: fix-admin-user-self-freeze-delete-protection
acceptance_status: passed
created_at: 2026-08-12 14:00:30
updated_at: 2026-08-12 14:28:57
source_bug: BUG-0008-admin-users-self-freeze-delete-not-forbidden
---

# 验收计划

## 后端验收

- 当前后台管理员调用冻结自己的接口返回 `403 Forbidden`。
- 当前后台管理员调用删除自己的接口返回 `403 Forbidden`。
- 自冻结和自删除被拒绝后，当前用户状态、`deleted_at` 和当前会话保持不变。
- 冻结、解冻、删除其他非系统用户仍保持既有行为。
- 系统内置超级管理员保护仍返回 `403 Forbidden`。

## 前端验收

- 当前账号行保留冻结按钮但置为禁用状态，并提供不可冻结当前登录账号的原因。
- 当前账号行保留删除按钮但置为禁用状态，并提供不可删除当前登录账号的原因。
- 当前账号行不显示额外“当前账号”文案。
- 其他非系统用户仍可打开冻结、解冻、删除确认弹窗。
- 确认弹窗仍使用设计系统弹窗，不回退到 `window.confirm`。

## 测试命令

```bash
uv run pytest tests/integration/api/test_admin_users.py
pnpm --dir src/web test -- admin-user-management
```

## 验收结果

```yaml
acceptance_status: passed
accepted_at: 2026-08-12 14:06:21
accepted_by: opsx-apply
source_bug: BUG-0008-admin-users-self-freeze-delete-not-forbidden
source_sprint: sprint-002
evidence:
  - command: pnpm --dir src/web test -- admin-user-management
    result: passed
    summary: 5 files, 69 tests passed
  - command: uv run pytest tests/integration/api/test_admin_users.py
    result: passed
    summary: 19 tests passed
  - command: openspec validate fix-admin-user-self-freeze-delete-protection --strict
    result: passed
failed_items: []
notes: OpenAPI schema 未变化，仅补充 403 错误语义和文档说明，无需客户端生成。
```

## 验收返修结果

```yaml
modified_at: 2026-08-12 14:16:51
feedback: 当前账号行保留冻结和删除按钮但禁用，比隐藏或替代按钮更符合后台操作列一致性。
adjustment: 前端当前账号行保留冻结/删除按钮，按钮 disabled，并显示禁用原因；其他账号操作保持可用。
validation: passed
evidence:
  - command: pnpm --dir src/web test -- admin-user-management
    result: passed
    summary: 5 files, 69 tests passed
  - command: openspec validate fix-admin-user-self-freeze-delete-protection --strict
    result: passed
  - command: git diff --check -- <touched-files>
    result: passed
```

## 验收返修结果 2

```yaml
modified_at: 2026-08-12 14:28:57
feedback: 删除当前账号行额外“当前账号”文案。
adjustment: 当前账号行仅保留冻结/删除按钮禁用态和禁用原因，不再显示额外当前账号标签。
validation: passed
evidence:
  - command: pnpm --dir src/web test -- admin-user-management
    result: passed
    summary: 5 files, 69 tests passed
  - command: openspec validate fix-admin-user-self-freeze-delete-protection --strict
    result: passed
  - command: git diff --check -- <touched-files>
    result: passed
```
