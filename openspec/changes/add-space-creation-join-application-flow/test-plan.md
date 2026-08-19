---
change_id: add-space-creation-join-application-flow
status: proposed
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-15 11:08:25
---

# Test Plan

## 后端

- pytest：创建空间申请成功、字段校验失败、重复待审批申请、未授权提交。
- pytest：精准搜索无匹配、多匹配、不可申请、无权限可见、唯一可申请。
- pytest：加入空间申请成功、已加入空间重复申请、待审批重复申请。
- pytest：撤回仅允许待审批申请。
- pytest：被拒申请重新提交保留历史记录。

## 前端

- Vitest/Testing Library：申请类型切换、创建表单校验、提交 loading/success/error。
- Vitest/Testing Library：精准搜索状态矩阵和申请理由必填。
- Vitest/Testing Library：创建空间入口、必填星号、自动标识、提交待审批申请、待审批结果态和无进入空间入口。

## UI 视觉

- 1440px 截图：申请中心默认态、创建表单、精准搜索命中、无结果、申请列表、撤回确认。
- computed style：状态标签、弹窗宽高、toast fixed、表单间距、列表行操作。
