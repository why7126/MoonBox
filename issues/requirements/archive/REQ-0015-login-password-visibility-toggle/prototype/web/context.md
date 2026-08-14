---
requirement_id: REQ-0015-login-password-visibility-toggle
prototype_type: web
status: decomposed
created_at: 2026-08-11 22:03:00
updated_at: 2026-08-11 22:03:00
png_required: false
---

# Web 登录页密码显隐原型拆解

## 页面清单

| 页面 | 路由 | 说明 |
|---|---|---|
| Web 登录页 | `/login` 或 `#login` | 在既有 MoonBox 登录卡片中补齐密码输入框显示/隐藏切换控件。 |

## 关键区域

| 区域 | 要点 |
|---|---|
| 返回首页入口 | 保持既有轻量导航，不受密码显隐状态影响。 |
| 登录卡片 | 保持 Logo、标题、说明、用户名、密码、记住我、登录按钮和错误反馈顺序。 |
| 密码字段 | 在密码输入框右侧加入图标按钮，默认隐藏密码。 |
| 错误反馈 | 登录失败或必填错误展示保持既有位置和 aria-live 语义。 |

## 组件层级

```text
login-page
  login-back
  login-card
    login-logo
    login-title
    login-field(username)
    login-field(password)
      password-input
      password-visibility-button
    login-remember
    login-submit
    admin-login-error
```

## 状态矩阵

| 状态 | 密码输入框 | 切换控件 | 登录行为 |
|---|---|---|---|
| 默认 | `type=password` | 显示密码 | 正常提交 |
| 明文展示 | `type=text` | 隐藏密码 | 正常提交 |
| 登录中 | 保持当前显隐状态 | 可禁用或保持可用，但不得提交表单 | 登录按钮展示登录中 |
| 登录失败 | 保持当前字段值和显隐状态 | 可继续切换 | 错误反馈展示 |
| 返回首页 | 登录页关闭 | 状态随登录页卸载或重置 | 不保留登录页遮罩 |

## 交互触发

- 点击图标按钮：切换密码输入框 `type`。
- Tab 聚焦图标按钮：显示清晰 focus-visible。
- Enter/Space：触发显隐切换。
- 表单提交：只由登录按钮或表单 submit 触发，显隐按钮不得提交。

## 数据依赖

- 复用既有登录表单字段：`username`、`password`、`remember`。
- 不新增 API、请求字段、响应字段或后端状态。
- 不写入本地存储、URL、日志、错误上报或持久化截图说明。

## 响应式断点

| 断点 | 验收重点 |
|---|---|
| 1440px desktop | 密码字段图标右对齐，登录卡片无高度抖动，字段与按钮间距稳定。 |
| 移动视口 | 图标按钮可点按，不溢出登录卡片，不遮挡输入内容。 |

## 1440px 验收焦点

- 登录卡片整体位置、Logo、标题、用户名字段、密码字段、记住我、登录按钮和错误反馈与既有登录页一致。
- 密码字段右侧空间足够，图标按钮不与 placeholder 或输入文本重叠。
- hover、focus-visible、显示态和隐藏态均清晰可见。
- computed style 重点记录密码字段容器 `position`、输入框 `padding-right`、按钮 `width/height/right/color/border/focus`。

## PNG 说明

本需求为既有登录页字段级增强，当前阶段不强制新增 PNG。后续 `/opsx-apply` 必须以 1440px 截图和关键交互截图作为实现验收证据。
