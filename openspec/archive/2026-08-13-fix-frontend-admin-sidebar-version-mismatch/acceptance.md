---
change_id: fix-frontend-admin-sidebar-version-mismatch
acceptance_status: passed
created_at: 2026-08-12 14:28:19
updated_at: 2026-08-12 14:35:11
---

# 验收标准

## AC-001 前后台版本展示一致

WHEN 用户分别打开前台需求中心与管理后台用户管理页  
THEN 两个侧边栏品牌区域展示的 MoonBox 产品版本号 MUST 一致。

## AC-002 后台不保留硬编码补丁号

WHEN 检查后台用户管理页侧边栏实现  
THEN 后台不得继续硬编码 `v1.0.5` 作为产品版本号。

## AC-003 回归测试覆盖

WHEN 运行前端测试  
THEN 后台用户管理页测试 MUST 覆盖版本展示，前台需求中心版本展示测试 MUST 保持通过。

## AC-004 边界不扩大

WHEN Change 完成实现  
THEN 不应产生后端 API、数据库、权限、部署、OpenAPI 或客户端生成变更。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-12 14:35:11
accepted_by: ai
source_change: fix-frontend-admin-sidebar-version-mismatch
source_sprint: sprint-002
evidence:
  - pnpm --dir src/web test -- admin-user-management.test.tsx requirement-center.test.tsx --run
  - pnpm --dir src/web build
failed_items: []
notes: 后台侧边栏改为使用共享 PRODUCT_VERSION；前台需求中心既有版本展示测试保持通过；本 Change 不涉及 API、数据库、权限、部署、OpenAPI 或客户端生成。
```
