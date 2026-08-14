---
requirement_id: REQ-0010-admin-user-menu-password-change
acceptance_status: passed
created_at: 2026-08-10 08:57:06
updated_at: 2026-08-14 16:29:34
owner: product
---

# 验收清单

## 功能 AC

- [x] AC-001 管理后台用户菜单存在“修改密码”菜单项，点击后打开修改密码 modal，不再展示占位 toast。
- [x] AC-002 修改密码 modal 包含当前密码、新密码、确认新密码、提交和取消操作。
- [x] AC-003 当前密码、新密码、确认新密码均为必填，未填写时展示可恢复的字段级或表单级反馈。
- [x] AC-004 新密码与确认新密码不一致时阻止提交，并展示清晰反馈。
- [x] AC-004A 当前密码、新密码、确认新密码输入框分别支持显示/隐藏密码明文，切换不改变提交值。
- [x] AC-005 自助修改密码接口必须要求有效后台登录态，并从服务端会话解析当前操作者。
- [x] AC-006 后端不得信任前端传入的 `user_id`、`role`、`is_admin` 或等价身份字段作为修改目标。
- [x] AC-007 当前密码错误时后端返回受控错误，不更新密码，不泄露账号状态、密码哈希算法、系统路径或内部异常。
- [x] AC-008 新密码必须拒绝空密码、示例密码、明显弱密码，并应复用或收紧后台认证安全规则。
- [x] AC-009 新密码与当前密码相同时应返回受控错误，不更新密码。
- [x] AC-010 密码修改成功后更新当前用户密码哈希和更新时间。
- [x] AC-011 密码修改成功后撤销当前用户所有后台会话，包括当前会话。
- [x] AC-012 修改成功后前端清理本地后台登录态，并跳转或引导到后台登录入口。
- [x] AC-013 修改成功后复用旧 access token 调用 `/api/v1/admin/**` 返回 401。
- [x] AC-014 密码变更审计记录包含操作者、目标用户、动作、时间和安全摘要。
- [x] AC-015 API 响应、日志、审计明文、前端持久化状态和错误反馈不得保存当前密码、新密码、密码哈希、access token 或会话 ID 明文。
- [x] AC-016 未登录、登录态失效、账号不可用、当前密码错误、新密码不合规和服务端异常均有受控反馈。
- [x] AC-017 后端测试覆盖成功改密、当前密码错误、弱密码、与当前密码相同、未登录、会话失效和旧 token 失效。
- [x] AC-018 前端测试覆盖菜单打开 modal、字段校验、确认密码不一致、提交成功后清理登录态并进入登录入口。
- [x] AC-019 API 文档和错误码文档同步自助修改密码接口、认证 Header、401/403 和密码规则错误。
- [x] AC-020 安全文档同步密码修改后的会话撤销策略和敏感信息禁止明文记录约束。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [x] AC-PROTOTYPE-002 `/req-opsx` 的 Change `design.md` 必须写入修改密码 modal 的 UI Skeleton，包含用户菜单触发、modal 容器、字段插槽、错误区、底部操作和登录态清理边界。
- [x] AC-PROTOTYPE-003 `/opsx-apply` 必须在 1440px 桌面视口验收用户菜单、modal 宽度、字段间距、底部按钮、toast/错误反馈、滚动和文本溢出。
- [x] AC-PROTOTYPE-004 `/opsx-archive` 前必须确认实现后的用户菜单、modal 行为、会话策略和本文档最终一致。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md` — 预防 Sprint 002/003 复发类缺陷

- [x] AC-XCUT-001 修改密码 modal 的 TSX 实现不得让通用 `modal-card` 与专属宽度类并存，避免通用样式覆盖业务弹窗宽度。
- [x] AC-XCUT-002 `/opsx-apply` 必须在浏览器 computed style 中验收修改密码 modal 最终宽度与设计预期一致。
- [x] AC-XCUT-003 低视口下修改密码 modal body 必须可滚动，底部提交和取消操作必须可访问。
- [x] AC-XCUT-004 modal 背景遮罩不得吞掉内部滚动，也不得导致页面主体误滚动。
- [x] AC-XCUT-005 必填字段、错误提示和底部操作区不得互相遮挡。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-admin-user-menu-password-change
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

