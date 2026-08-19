---
change_id: fix-admin-user-list-enum-time-display
status: applied
created_at: 2026-08-15 09:24:03
updated_at: 2026-08-15 10:04:45
---

# Design: 用户列表枚举标签与时间展示修复

## 根因摘要

BUG-0011 的根因状态为 `confirmed`。证据显示：

- `AdminUser` 前端类型已声明 `updated_at`。
- 后端 `list_users` 查询和 `AdminUserRead` schema 已返回 `updated_at`。
- 用户管理列表列定义、`colgroup` 和行渲染未展示更新时间。
- 角色、状态、时间字段均为直出或统一弱语义样式。

因此修复应集中在 Web 管理后台用户列表 UI 表达和测试，不扩大到 API/DB。

## 修复方案

### 角色标签

- 增加角色标签渲染函数或轻量组件。
- 「后台管理员」和「前台用户」使用同一尺寸、不同语义的标签样式。
- 保持文本可读，不依赖颜色作为唯一信息。
- 验收返修后，角色标签采用无实线边框、无专属底色的轻量样式，仅保留图标和彩色文字，避免与状态标签和表格网格线竞争视觉层级。

### 状态语义

- 增加状态展示映射，覆盖「待激活」「正常」「已冻结」「已删除」。
- 每个状态至少具备明确文案和可区分样式；可使用 lucide 图标辅助。
- 状态标签沿用空间管理页状态标签表达：无边框、无底色，文字保持表格文本色，通过状态图标颜色表达语义；「正常」状态使用与空间管理页一致的圆形 check 图标。
- 保持现有筛选状态语义不变，不新增「已删除」默认筛选入口。

### 时间格式

- 增加 `formatAdminDateTime(value)` 类函数。
- 输入为 `null`/空值时返回 `—`。
- 输入为 ISO 字符串或已格式化字符串时，稳定输出 `yyyy-mm-dd hh:mm:ss`。
- 最近登录时间、创建时间、更新时间全部走同一格式化函数。

### 更新时间列

- 在「创建时间」后增加「更新时间」列。
- 同步 `colgroup` 增加更新时间列宽，必要时调整 `admin-account-table` 最小宽度。
- 保持操作列 sticky 行为和横向滚动可用。

## 测试策略

- 更新 `src/web/src/admin-user-management.test.tsx`：
  - 列头应包含「更新时间」。
  - 第一行单元格应展示角色标签、状态语义和三类时间字段。
  - 覆盖 `updated_at` 展示和空 `last_login_at` 展示为 `—`。
  - 覆盖 ISO 与已格式化字符串不破坏显示。
- 运行：

```bash
pnpm --dir src/web test src/admin-user-management.test.tsx
python scripts/validate-root-cause-evidence.py --bug BUG-0011-admin-user-list-enum-time-display-unclear
```

## 文档同步

本 Change 不修改 API、DB、部署、安全或客户端生成边界。若实现过程中发现接口字段格式或 OpenAPI 与实际响应不一致，应补充 API 文档和测试，并在 Change trace 中记录原因。
