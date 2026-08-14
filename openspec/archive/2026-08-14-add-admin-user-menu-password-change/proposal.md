---
change_id: add-admin-user-menu-password-change
status: applied
type: add
source_requirement: REQ-0010-admin-user-menu-password-change
source_sprint: sprint-002
created_at: 2026-08-10 09:14:08
updated_at: 2026-08-10 09:30:46
---

# 新增后台用户菜单栏密码修改功能

## 背景

管理后台已具备账号密码登录、服务端会话、退出登录、会话撤销和管理员重置他人密码能力，但当前登录管理员仍不能从用户菜单自助修改自己的密码。现有用户菜单中的“密码修改”入口仍是占位反馈，无法满足初始化密码更新、首次激活后改密和账号安全治理要求。

## 目标

- 在管理后台用户菜单中提供“修改密码”入口，并以 modal 承载改密流程。
- 后端提供当前登录用户自助改密接口，校验当前密码与新密码安全规则。
- 改密成功后撤销当前用户全部后台会话，并要求重新登录。
- 补齐审计、安全脱敏、API 文档、前后端测试和 1440px UI 验收。

## 非目标

- 不实现忘记密码、邮箱/短信找回、OAuth、SSO、MFA 或普通 Web 前台用户改密。
- 不实现管理员为他人重置密码；该能力由后台用户管理能力覆盖。
- 不新增独立个人资料页或全页设置表单。
- 不实现多端设备列表、refresh token 或复杂多端互踢配置。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  admin: true
  api: true
  database: false
  storage: false
  miniapp: false
capabilities:
  new:
    - 当前登录后台管理员自助修改密码
    - 用户菜单修改密码 modal
    - 改密后全部旧会话撤销与重新登录
  modified:
    - web-admin-auth-system
```

## 验收摘要

- 当前密码、新密码、确认新密码必填，确认不一致时阻止提交。
- 后端从 access token 与服务端会话解析当前操作者，不信任前端传入身份字段。
- 当前密码错误、新密码弱、与当前密码相同、未登录或会话失效时返回受控错误。
- 成功后更新密码哈希、记录审计、撤销当前用户全部后台会话。
- 前端清理本地登录态并进入后台登录入口；旧 access token 访问 `/api/v1/admin/**` 返回 401。
- Change 实现阶段必须完成 admin-modal 横切 AC、UI Skeleton 和 1440px 视觉验收。
