---
change_id: fix-admin-user-self-freeze-delete-protection
created_at: 2026-08-12 14:00:30
updated_at: 2026-08-12 14:28:57
---

# Tasks

- [x] 1. 后端冻结接口拒绝当前登录用户冻结自己，返回 `403 Forbidden`，且不得修改状态或撤销当前会话。
- [x] 2. 后端删除接口拒绝当前登录用户删除自己，返回 `403 Forbidden`，且不得设置 `deleted_at` 或撤销当前会话。
- [x] 3. 保持冻结、解冻、删除其他非系统用户以及系统内置超级管理员保护不回归。
- [x] 4. 前端用户管理当前账号行保留冻结、删除按钮但置为禁用状态，并通过禁用原因说明不可自操作。
- [x] 5. 前端非当前账号行继续保留冻结、解冻、删除和重置密码等既有操作流程。
- [x] 6. 补充 `tests/integration/api/test_admin_users.py` 回归测试，覆盖自冻结、自删除 `403`、状态不变和会话仍可用。
- [x] 7. 补充 `src/web/src/admin-user-management.test.tsx` 回归测试，覆盖当前账号危险操作不可用和其他账号操作可用。
- [x] 8. 同步 API/权限边界文档；如 OpenAPI 描述发生变化，同步客户端生成物。
- [x] 9. 运行后端 API 测试、前端用户管理测试和相关格式/类型校验。
- [x] 10. 评估是否需要在 `docs/knowledge-base/incidents/` 沉淀账号自操作保护经验；如无复用价值，在归档说明中记录不适用。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-12 14:16:51 | 当前账号行直接隐藏/替代冻结和删除操作不如保留按钮但禁用清晰。 | 前端当前账号行保留冻结/删除按钮，设置 disabled、禁用原因和“当前账号”标记；同步前端回归测试与规格措辞。 | `pnpm --dir src/web test -- admin-user-management` 通过；`openspec validate fix-admin-user-self-freeze-delete-protection --strict` 通过；`git diff --check` 通过。 |
| 2026-08-12 14:28:57 | 当前账号行不需要额外显示“当前账号”文案。 | 删除当前账号行额外文案，保留冻结/删除按钮 disabled 和禁用原因；同步前端回归测试与规格措辞。 | `pnpm --dir src/web test -- admin-user-management` 通过；`openspec validate fix-admin-user-self-freeze-delete-protection --strict` 通过；`git diff --check` 通过。 |
