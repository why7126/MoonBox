---
title: Admin List Page Consistency
purpose: 管理后台列表页一致性治理，预防分页、toast、确认弹窗和行内操作复发类缺陷
source: REQ-0004-admin-user-management
status: active
created_at: 2026-08-07 22:21:34
updated_at: 2026-08-07 22:21:34
---

# 管理后台列表页一致性

## 适用范围

适用于管理后台 CRUD 列表页，尤其是表格、筛选、分页、行内操作、状态变更和操作反馈组合出现的页面。

## 验收 gate

- 列表分页 DOM 必须与当前用户管理基准一致：总数位于左侧，翻页、页码、“每页显示”文案和条数下拉位于右侧。
- 成功和失败反馈必须使用 fixed toast，不得引发布局位移，不得挤压列表、分页、弹窗或抽屉内容。
- 冻结、解冻、删除、重置密码等状态变更必须使用设计系统确认弹窗。
- 禁止在管理后台状态变更中调用 `window.confirm`。
- 表格行内操作列在横向滚动或列较多时必须保持易访问。
- 筛选条件变化后，列表结果、分页状态和空态提示必须与当前条件一致。

## 落地要求

- `/req-complete` 命中 `admin-list` 时，必须将分页 DOM、fixed toast、设计系统确认弹窗和禁用 `window.confirm` 转化为横切 AC。
- `/opsx-apply` 实现前必须复核对应 AC，并在前端验证中覆盖筛选、分页、状态变更和 toast 不位移。

