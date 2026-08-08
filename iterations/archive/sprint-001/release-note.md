---
sprint_id: sprint-001
status: published
created_at: 2026-07-30 08:51:51
updated_at: 2026-08-08 23:23:52
---

# Sprint-001 发布说明草稿

## 发布主题

MoonBox 官网首页品牌视觉、Web 登录页体验、数据库双环境兼容、管理后台用户管理、后台登录认证、后台 CRUD 列表页模板体系与后台用户首次登录激活状态治理更新。

## 正式范围

| 类型 | 编号 | Change | 状态 |
|---|---|---|---|
| REQ | REQ-0001-homepage | add-homepage-brand-visual | archived |
| REQ | REQ-0002-login-page | add-login-page | archived |
| REQ | REQ-0003-database-compatibility | add-database-compatibility | archived |
| REQ | REQ-0004-admin-user-management | add-admin-user-management | archived |
| REQ | REQ-0005-admin-auth-system | add-admin-auth-system | archived |
| REQ | REQ-0006-admin-crud-list-template | add-admin-crud-list-template | archived |
| REQ | REQ-0007-admin-user-first-login-activation | update-admin-user-first-login-activation | archived |

## 用户可见变化

- 官网首页左上角使用新的 MoonBox 品牌 Logo。
- 官网首页首屏右侧展示新的 MoonBox 产品视觉。
- 首页首屏文案、CTA 和三项能力摘要保持既有结构。
- Web 登录页提供返回首页、MoonBox Logo、用户名密码表单、记住我和登录按钮。
- 登录页背景复用首页产品视觉并叠加深色遮罩，保持表单可读性。
- 开发环境保留 SQLite 快速启动路径。
- 生产环境数据库策略调整为 MySQL，并禁止生产静默回退 SQLite。
- 数据库兼容性差异、迁移、Repository 和 MySQL 验证要求进入正式迭代范围。
- 管理后台提供用户列表、创建、编辑、冻结、解冻、逻辑删除、重置密码和头像上传能力。
- 管理后台登录认证系统进入正式迭代范围，覆盖超级管理员账号密码登录、access token、服务端会话记录、退出登录、后台路由守卫和 `/api/v1/admin/**` 正式鉴权。
- 管理后台 CRUD 列表页模板体系进入正式迭代范围，覆盖列表页模板、通用组件边界、用户管理页适配、分页 DOM、fixed toast、设计系统确认弹窗和弹窗宽度/滚动验收。
- 后台用户首次登录激活与冻结前状态恢复进入正式迭代范围，覆盖待激活首次登录自动转正常、冻结前状态记录、解冻恢复待激活/正常、前台用户拒绝后台登录和回归测试。

## 非本次范围

- 普通 Web 前台真实登录、注册、忘记密码、第三方登录、SSO、MFA 和 refresh token 长期续期。
- 小程序、移动端或桌面端能力。
- 真实生产数据从 SQLite 到 MySQL 的迁移工具、MySQL 高可用和容量规划。
- 复杂仪表盘、详情页、跨端组件库和具体业务实体数据模型。
- 激活链接、邮箱验证、短信验证、SSO、MFA、完整首次登录改密流程和已删除用户恢复。

## 发布前检查

- [x] 首页桌面端视觉验收通过。
- [x] 首页移动端视觉验收通过。
- [x] CTA 入口行为符合 Sprint 范围。
- [x] 登录页桌面端视觉验收通过。
- [x] 登录页移动端视觉验收通过。
- [x] 登录页表单必填校验和返回首页行为验收通过。
- [x] SQLite 本地快速验证通过。
- [x] MySQL 关键路径验证通过。
- [x] 数据库设计、部署文档、数据库规则和兼容性记录已同步。
- [x] 管理后台用户管理功能、头像上传、敏感操作确认和审计验收通过。
- [x] 管理后台认证接口、会话撤销、退出登录、后台路由守卫和 `/api/v1/admin/**` 鉴权替换验收通过。
- [x] 管理后台 CRUD 列表页模板、用户管理页适配、分页 DOM、fixed toast、确认弹窗、禁用 `window.confirm`、computed width 和低视口滚动验收通过。
- [x] 待激活后台管理员首次登录自动转正常、冻结待激活用户解冻恢复待激活、正常用户解冻恢复正常、前台用户拒绝后台登录和已删除用户不可恢复验收通过。
- [x] OpenSpec Change 完成 apply 与 archive。
