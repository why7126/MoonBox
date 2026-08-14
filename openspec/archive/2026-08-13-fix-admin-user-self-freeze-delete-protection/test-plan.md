---
change_id: fix-admin-user-self-freeze-delete-protection
created_at: 2026-08-12 14:00:30
updated_at: 2026-08-12 14:00:30
---

# 测试计划

## 后端

- 在 `tests/integration/api/test_admin_users.py` 中新增或扩展测试：
  - 创建普通后台管理员并完成登录激活。
  - 使用该管理员 token 调用自身冻结接口，断言 `403`。
  - 使用该管理员 token 调用自身删除接口，断言 `403`。
  - 请求 `/api/v1/auth/me` 或后台受保护接口，确认会话仍可用。
  - 读取目标用户，确认状态未变、`deleted_at` 未设置。

## 前端

- 在 `src/web/src/admin-user-management.test.tsx` 中新增或扩展测试：
  - 将本地 session 设置为列表中的普通后台管理员。
  - 渲染用户管理页后定位当前账号行，断言冻结/删除按钮存在但不可点击，并提供禁用原因。
  - 断言当前账号行不显示额外“当前账号”文案。
  - 定位其他非系统用户行，断言冻结/删除确认流程仍可触发。

## 回归

- 保留既有超级管理员不可操作测试。
- 保留既有冻结前状态、解冻恢复、重置密码临时密码保护和 fixed toast 测试。
- 如果修改 OpenAPI 描述，补充 OpenAPI/客户端生成校验。
