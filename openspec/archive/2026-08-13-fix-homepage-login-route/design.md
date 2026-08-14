---
change_id: fix-homepage-login-route
status: applied
created_at: 2026-08-11 08:41:00
updated_at: 2026-08-11 09:39:19
source_bug: BUG-0003-homepage-start-moonbox-should-open-login-route
---

# 技术设计

## 根因

`Homepage` 当前通过 `window.location.hash === "#login"` 控制登录视图显隐，并在首页 CTA 点击时写入 `#login`。应用级路由 `App` 未识别 `/login`，导致前台登录页没有独立路由入口。

## 修复方案

1. 在应用级路由中识别 `/login`。
2. 复用现有前台登录页视觉和表单结构，将其作为 `/login` 的主视图。
3. 首页 CTA 使用 `window.history.pushState` 或等价导航进入 `/login`，并触发应用路由同步。
4. 返回首页时导航到 `/`，并清除历史 `#login` 状态。
5. `/login` 表单提交调用既有后台登录 API。
6. 登录成功后写入后台 session，并同步写入轻量前台 session，作为 `/requirements` 的前端路由保护状态。
7. `/requirements` 未检测到前台 session 时规范化回 `/login`，不得复用管理后台登录页。
8. 需求中心上下文加载时，如本地存在后台 admin session，继续携带后台 Bearer token，以便后端返回真实用户信息和 `can_access_admin`；若后端用户为空、姓名为空或姓名为「未登录」，则以前台 session 用户名兜底展示。

## 路由边界

| 路由 | 期望行为 |
|---|---|
| `/` | 展示官网首页 |
| `/login` | 展示统一 MoonBox 登录页，提交时调用后台登录 API |
| `/admin` | 已登录时展示后台页面；未登录时回到 `/login` |
| `/requirements` | 需要前台登录 session；未登录时回到 `/login` 前台登录页，已登录时展示前台需求中心；已有后台 admin session 时可识别后台权限并展示「进入后台」 |
| `/#login` | 不再作为首页 CTA 的目标；兼容与否由实现阶段评估，但测试不得继续把它作为主要期望 |

## 测试策略

- 前端单测覆盖首页 CTA 点击后 `pathname === "/login"` 且 `hash === ""`。
- 前端单测覆盖直接访问 `/login` 展示前台登录页。
- 前端单测覆盖返回首页后 `pathname === "/"`。
- 前端单测覆盖 `/login` 提交统一登录表单后调用后台登录 API 并进入 `/requirements`。
- 前端单测覆盖 `/admin` 未登录时回到统一 `/login`，且不展示 `管理后台登录` 表单。
- 回归 `/admin` 和 `/requirements` 保护逻辑，确认后台登录只保护 `/admin`，前台登录只保护 `/requirements` 前端入口。
- 前端单测覆盖已有后台 admin session 时需求中心上下文请求携带 Bearer token，并显示「进入后台」。
- 前端单测覆盖仅有前台 session 且后端返回显式匿名、空姓名或缺失用户对象时，用户菜单显示前台用户名而不是「未登录」。

## 风险

- 若登录页仍内嵌在 `Homepage` 内，可能出现 `/login` 下首页主视图隐藏/展示状态不同步。
- 若仅修改按钮跳转而未在 `App` 中加入 `/login` 分支，直接访问 `/login` 仍可能落回首页。
- 若测试未更新，旧的 `#login` 断言会继续固化错误行为。

## 文档同步

本 Change 不改变 API、数据库、对象存储、部署配置或后端安全策略。统一登录页复用既有后台登录 API 与后台 session；前台 session 仅用于 `/requirements` 前端路由进入态，不可作为后台权限凭证；后台权限展示仍以既有后台 admin session 和后端 `can_access_admin` 返回为准。
