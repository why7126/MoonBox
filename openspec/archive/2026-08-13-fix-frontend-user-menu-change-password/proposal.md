---
change_id: fix-frontend-user-menu-change-password
type: fix
status: applied
created_at: 2026-08-11 17:37:04
updated_at: 2026-08-12 13:43:11
owner: MoonBox 产品团队
source_bug: BUG-0004-frontend-user-menu-change-password-not-implemented
sprint: sprint-002
---

# 修复前台用户菜单修改密码入口

## 背景

`BUG-0004-frontend-user-menu-change-password-not-implemented` 已确认：前台需求中心用户菜单已经展示“修改密码”入口，但点击后没有打开弹窗，也不会调用既有改密接口。

这会造成已展示账号安全入口不可用。后台用户菜单已具备完整自助改密能力，后端 `/api/v1/admin/auth/change-password` 也已存在，因此本修复聚焦前台菜单接线、弹窗复用和会话清理闭环。

## 变更内容

- 前台需求中心用户菜单点击“修改密码”后打开修改密码弹窗。
- 修改密码弹窗必须包含当前密码、新密码、确认新密码、显示/隐藏密码和错误提示。
- 提交成功时调用既有 `/api/v1/admin/auth/change-password`。
- 普通前台用户没有后台 admin session 时，提交必须使用 frontend session token，不应误提示登录失效。
- 后端自助改密接口允许任意正常登录用户修改自己的密码，但不放开后台管理接口权限。
- 成功后清理 `moonbox.admin.session` 与 `moonbox.frontend.session`，并跳转 `/login`。
- 修改失败或两次新密码不一致时保留弹窗，不清理会话。
- 用户继续编辑密码字段时清理旧接口错误，避免提交级错误与当前字段级错误叠加。
- 保持后台用户菜单修改密码流程不回归。
- 前台打开修改密码弹窗后，弹窗内容、输入框和操作按钮必须在前台主题中清晰可读并可填写。
- 补充前台需求中心与后台修改密码回归测试。

## 非目标

- 不新增新的修改密码 API。
- 不修改后端密码策略、数据库结构、认证模型或对象存储。
- 不放开用户管理、后台个人资料或其它后台管理接口的权限。
- 不把前台“修改密码”降级为跳转后台或 toast 提示。
- 不调整用户角色、空间权限或后台访问权限模型。

## 回滚方案

如修复导致前台需求中心无法打开菜单、弹窗提交异常或会话清理误伤，可回滚本 Change 中的前端菜单接线、共享弹窗抽取和测试变更，恢复当前仅展示菜单入口的状态；同时保留 BUG 与 Change trace，记录回滚原因，并重新评估弹窗复用方案。

## 影响范围

- Web 前端：`src/web/src/pages/catalog/RequirementCenterPage.tsx`、后台改密弹窗相关组件、`src/web/src/pages/admin/adminAuth.ts`、前台/后台相关测试。
- 规格：`web-catalog-requirement-center`。
- 文档追溯：BUG trace、Sprint scope、Change trace。
