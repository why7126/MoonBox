---
change_id: fix-frontend-admin-sidebar-version-mismatch
created_at: 2026-08-12 14:28:19
updated_at: 2026-08-12 14:28:19
---

# 测试计划

## 前端测试

```bash
pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx --run
```

覆盖：

- 后台用户管理页侧边栏版本号展示。
- 前台需求中心侧边栏版本号展示。
- 后台用户管理页既有渲染与交互测试不回归。

## 构建 / 类型校验

```bash
pnpm --dir src/web build
```

覆盖共享版本常量导入路径和 TypeScript 编译。

## 不适用

- 后端 pytest：本 Change 不触达后端逻辑。
- API / OpenAPI / Orval：本 Change 不改变接口契约。
- 数据库 / 部署：本 Change 不改变数据结构或部署拓扑。
