---
bug_id: BUG-0009-frontend-admin-sidebar-version-mismatch
created_at: 2026-08-12 14:19:01
updated_at: 2026-08-12 14:19:01
classification: code
---

# 根因分析

## 直接原因

管理后台用户管理页侧边栏直接硬编码展示版本号 `v1.0.5`，未复用前台已经使用的共享版本常量。

## 根本原因

产品版本展示缺少统一使用约束与后台测试覆盖。前台需求中心已经通过 `PRODUCT_VERSION` 展示 `v0.1.0`，但后台侧边栏仍保留独立静态文案，导致两个入口在同一产品版本信息上分叉。

## 触发条件

同时访问以下两个入口并查看侧边栏品牌区域：

1. 前台需求中心。
2. 管理后台用户管理页。

## 缺陷分类

- 类型：代码缺陷。
- 位置：前端 Web UI。
- 边界：不涉及后端 API、数据库、权限、部署拓扑或客户端生成。

## 证据

- 前台版本来源：`src/shared/product-version.ts` 定义 `PRODUCT_VERSION = "v0.1.0"`。
- 前台展示位置：`src/web/src/pages/catalog/RequirementCenterPage.tsx` 使用 `PRODUCT_VERSION`。
- 后台异常位置：`src/web/src/pages/admin/AdminUserManagementPage.tsx` 硬编码 `<em>v1.0.5</em>`。
- 测试缺口：前台测试断言版本号；后台用户管理测试未覆盖版本一致性。
