---
change_id: add-space-creation-join-application-flow
status: modified
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-27 09:20:00
---

# Test Plan

## 后端

- pytest：创建空间申请成功、字段校验失败、重复待审批申请、未授权提交。
- pytest：申请人和拟负责人使用当前登录用户，提交后不直接创建正式空间。
- pytest：成员上限、存储空间、AI Tokens 和到期时间按后台空间管理一致规则校验。
- pytest：前台不暴露加入空间、精准搜索、我的申请、撤回或重新提交能力。

## 前端

- Vitest/Testing Library：创建空间入口、弹窗标题、整合副标题、无重复审批 hint、无加入入口。
- Vitest/Testing Library：必填星号、后台一致默认值和输入限制、AI Tokens 无单位、自动标识。
- Vitest/Testing Library：到期时间控件视口限位、快捷按钮关闭、外部点击关闭并保留值、日历图标二次点击关闭。
- Vitest/Testing Library：提交 loading、待审批结果态和无进入空间入口。

## UI 视觉

- 1440px 截图：创建空间弹窗默认表单、配额、有效期、提交按钮和待审批结果态。
- 1440x900 关键交互：到期时间选择器近底部打开时在视口内完整可操作。
- computed style：弹窗宽高、双列网格、输入框单位、必填星号、日期时间面板、关闭按钮和底部操作。
