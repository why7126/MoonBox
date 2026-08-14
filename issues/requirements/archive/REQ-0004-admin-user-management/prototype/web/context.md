---
requirement_id: REQ-0004-admin-user-management
status: pending_review
created_at: 2026-08-07 22:15:09
updated_at: 2026-08-07 22:15:09
---

# 原型上下文

## 来源

- 外部上下文：`<local-downloads>/MoonBox-Platform-Operations-v1.0.5/prototype-context.md`
- 外部 HTML：`<local-downloads>/MoonBox-Platform-Operations-v1.0.5/prototype.html`
- 外部截图：`<local-downloads>/MoonBox-Platform-Operations-v1.0.5/prototype.png`

## 本需求内资产

- `prototype/web/prototype.html`
- `prototype/web/prototype.png`

## 原型要点

- 视口基准为 1440 × 1000，桌面优先。
- MoonBox 深色主题为默认，支持浅色主题切换。
- 侧边栏为 224px，可折叠至 72px；用户管理位于 `SYSTEM` 分组。
- 用户列表包含头像用户列、角色、状态、空间数、最近登录时间、创建时间和固定操作列。
- 筛选区中搜索框自适应占满剩余宽度，角色与状态筛选保持固定宽度。
- 分页区左侧展示总数，右侧展示图标翻页、页码、“每页显示”文案和条数下拉。
- 创建/编辑用户复用弹窗；创建时用户名可编辑，编辑时用户名只读。
- 头像上传要求同会话即时回显。
- 系统内置唯一超级管理员行展示“系统内置”标识，操作列不可用。

## 实现注意

- 原型中的角色范围以本次用户决策为准：仅保留“后台管理员”和“前台用户”。
- 冻结后会话失效时限以本次用户决策为准：10 秒内。
- 原型中的 Workspace、授权、用量、安全、审计、平台管理员页面不属于 REQ-0004 交付范围。
