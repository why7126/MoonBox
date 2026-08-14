---
change_id: add-admin-user-menu-password-change
status: applied
created_at: 2026-08-10 09:14:08
updated_at: 2026-08-10 09:47:55
---

# Tasks

## 1. UI Skeleton 与设计承接

- [x] 1.1 在实现前确认 `prototype/web/context.md` 与 `prototype/web/prototype.html` 的页面清单、组件层级、状态矩阵和 1440px 验收焦点。
- [x] 1.2 在前端实现计划中建立 `ChangePasswordModal` UI Skeleton：用户菜单触发、modal 容器、字段插槽、错误区、底部操作、状态容器、数据依赖和可测选择器。
- [x] 1.3 确认 modal 使用专属宽度类，不让通用 `modal-card` 与专属宽度类并存。

## 2. 后端自助改密能力

- [x] 2.1 新增当前登录用户自助修改密码 API，挂在 `/api/v1/admin/auth` 能力域并受后台认证依赖保护。
- [x] 2.2 新增请求/响应 schema，包含当前密码、新密码、确认新密码或等价字段，响应不得返回敏感凭证。
- [x] 2.3 仓储层实现当前密码校验、新密码规则校验、密码哈希更新和审计记录。
- [x] 2.4 修改成功后撤销当前用户全部后台会话，包括当前会话。

## 3. 前端用户菜单与 modal

- [x] 3.1 将用户菜单“密码修改”从占位 toast 改为打开修改密码 modal。
- [x] 3.2 实现当前密码、新密码、确认新密码输入、必填校验、确认一致校验和受控错误反馈。
- [x] 3.3 封装自助改密 API 客户端，复用 API base URL、Authorization Header 和错误读取策略。
- [x] 3.4 修改成功后清理本地后台登录态并进入后台登录入口。

## 4. 测试

- [x] 4.1 后端测试覆盖成功改密、当前密码错误、弱密码、与当前密码相同、未登录、会话失效和旧 token 失效。
- [x] 4.2 前端测试覆盖菜单打开 modal、字段校验、确认密码不一致、提交成功后清理登录态并进入登录入口。
- [x] 4.3 回归后台登录、退出、`/me` 和用户管理重置密码相关测试。

## 5. 文档与验收

- [x] 5.1 同步 API 文档和错误码文档，记录自助修改密码接口、认证 Header、401/403 和密码规则错误。
- [x] 5.2 同步安全文档，记录改密后全部旧会话撤销和敏感信息禁止明文记录约束。
- [x] 5.3 执行 admin-modal 横切验收：computed width、低视口滚动、遮罩滚动和字段/操作区无遮挡。
- [x] 5.4 执行 1440px 视觉验收，并记录截图或等价证据入口。
- [x] 5.5 回填 REQ-0010 `trace.md` / `acceptance.md` 中 prototype gate 和最终一致性结果。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-10 09:47:55 | 修改密码弹窗需要支持显示/隐藏密码。 | 为当前密码、新密码、确认新密码添加独立显示/隐藏切换；更新 UI Skeleton、规格 delta、测试和 1440px 视觉证据。 | `pnpm --dir src/web test -- admin-auth.test.tsx --run`、`pnpm --dir src/web build`、`openspec validate add-admin-user-menu-password-change --strict`、1440px Chrome 验收通过；截图：`implementation/visual-1440-password-toggle.png`。 |
