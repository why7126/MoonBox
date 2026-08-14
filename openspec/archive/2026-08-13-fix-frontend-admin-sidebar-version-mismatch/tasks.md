---
change_id: fix-frontend-admin-sidebar-version-mismatch
created_at: 2026-08-12 14:28:19
updated_at: 2026-08-12 14:28:19
---

# Tasks

- [x] 1. 后台用户管理页侧边栏导入并展示共享 `PRODUCT_VERSION`。
- [x] 2. 移除后台侧边栏独立硬编码 `v1.0.5`。
- [x] 3. 补充 `src/web/src/admin-user-management.test.tsx` 回归测试，覆盖后台侧边栏版本展示与共享版本一致。
- [x] 4. 保持前台需求中心 `PRODUCT_VERSION` 展示和既有测试不回归。
- [x] 5. 运行前端相关测试：`pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx --run`。
- [x] 6. 运行前端构建或等价类型校验：`pnpm --dir src/web build`。
- [x] 7. 确认本修复不需要同步 API、数据库、权限、部署、OpenAPI 或客户端生成。
- [x] 8. 评估是否需要在 `docs/knowledge-base/incidents/` 沉淀版本事实源分叉经验；如无复用价值，在归档说明中记录不适用。
