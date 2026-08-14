---
bug_id: BUG-0009-frontend-admin-sidebar-version-mismatch
title: 前台与后台侧边栏版本号不一致
severity: medium
status: done
owner:
discovered_at: 2026-08-12 14:12:57
environment: local
related_requirement:
related_change: fix-frontend-admin-sidebar-version-mismatch
created_at: 2026-08-12 14:19:41
updated_at: 2026-08-13 22:40:16
---

# 现象

MoonBox 前台需求中心与管理后台用户管理页的侧边栏品牌区域展示不同产品版本号：

- 前台侧边栏显示 `v0.1.0`。
- 后台侧边栏显示 `v1.0.5`。

当前代码中，前台通过共享版本常量展示版本号，后台侧边栏直接硬编码了另一版本号，导致同一产品在不同入口展示的发布版本不一致。

# 复现步骤

1. 打开 MoonBox 前台需求中心。
2. 查看左侧侧边栏品牌区域版本号。
3. 打开 MoonBox 管理后台用户管理页。
4. 查看左侧侧边栏品牌区域版本号。

# 期望 vs 实际

## 期望

前台与后台侧边栏使用同一产品版本事实源，并展示一致版本号。

## 实际

前台侧边栏展示 `v0.1.0`，后台侧边栏展示 `v1.0.5`。

# 影响范围

- 影响前台需求中心侧边栏与后台用户管理页侧边栏的产品版本展示一致性。
- 用户在前台与后台之间切换时可能误判当前部署版本、发布状态或是否进入了不同环境。
- 当前未发现后端 API、数据库、权限、部署拓扑或客户端生成受到影响。

# 严重等级说明

严重等级为 `medium`。该问题为用户可见的产品元信息错误，会造成发布状态误导，但不阻断登录、导航、用户管理或需求中心核心操作。

# 已知证据

- `src/shared/product-version.ts` 定义 `PRODUCT_VERSION = "v0.1.0"`。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx` 使用 `PRODUCT_VERSION` 展示前台侧边栏版本。
- `src/web/src/pages/admin/AdminUserManagementPage.tsx` 的后台侧边栏硬编码 `<em>v1.0.5</em>`。
- 前台测试断言 `v0.1.0`，后台用户管理测试暂未断言版本一致性。
