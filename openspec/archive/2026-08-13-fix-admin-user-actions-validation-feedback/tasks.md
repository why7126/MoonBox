---
change_id: fix-admin-user-actions-validation-feedback
created_at: 2026-08-13 09:38:58
updated_at: 2026-08-13 09:53:24
---

# Tasks

- [x] 1. 调整用户编辑弹窗校验：新增态保留用户名正则，编辑态不因只读用户名阻断保存。
- [x] 2. 调整用户操作确认弹窗：空原因、空白原因或不足 4 个字时展示可见错误提示。
- [x] 3. 确认校验失败时不调用重置密码、冻结、解冻或删除 API。
- [x] 4. 保持合法操作原因的重置密码、冻结、解冻、删除成功路径不回归。
- [x] 5. 补充 `src/web/src/admin-user-management.test.tsx` 回归测试，覆盖编辑异常用户名、空原因、短原因和合法原因。
- [x] 6. 运行前端相关测试：`pnpm --dir src/web test -- admin-user-management.test.tsx --run`。
- [x] 7. 运行前端构建或等价类型校验：`pnpm --dir src/web build`。
- [x] 8. 确认本修复不需要同步 API、数据库、权限、部署、OpenAPI 或客户端生成。
- [x] 9. 评估是否需要新增 `docs/knowledge-base/incidents/`；如不适用，在归档说明中记录原因。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-13 09:50:43 | 用户管理模块所有操作原因需要新增红色 `*`，提示必填。 | 重置密码、冻结、解冻、删除确认弹窗的“操作原因”标签复用 `label.required` 红星样式。 | `pnpm --dir src/web test -- admin-user-management.test.tsx --run`、`pnpm --dir src/web build` 通过。 |
| 2026-08-13 09:53:24 | 红色星号位置应直接放在“操作原因”后面，不要新起一行。 | 为确认弹窗必填 label 增加 `inline-flex` 覆盖样式，确保红星与字段名同一行紧邻展示。 | `pnpm --dir src/web test -- admin-user-management.test.tsx --run`、`pnpm --dir src/web build` 通过。 |
