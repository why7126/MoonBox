---
requirement_id: REQ-0002-login-page
title: Web 登录页原型上下文
status: in_sprint
source:
  - <local-downloads>/MoonBox-Landing-v1.0.2/prototype-context.md
  - <local-downloads>/MoonBox-Landing-v1.0.2/prototype.html
  - <local-downloads>/MoonBox-Landing-v1.0.2/prototype-login.png
---

# Web 登录页原型上下文

## 抽取范围

原始原型同时包含官网首页与登录页。本需求只抽取 `loginPage` 相关内容：

- `#login`：登录页页面状态。
- `[data-open-login]`：首页进入登录页入口。
- `[data-back-home]`：登录页返回首页入口。
- `#loginForm`：登录表单。
- `input[name="username"]`：用户名输入。
- `input[name="password"]`：密码输入。
- `input[name="remember"]`：记住我控件。

## 页面结构

```text
loginPage
├── 返回首页入口
├── 背景产品视觉 + 深色遮罩
└── 登录卡片
    ├── MoonBox Logo
    ├── 标题：开启你的宝盒
    ├── 说明：登录 MoonBox，继续构建你的 Agent 研发组织。
    ├── 用户名输入
    ├── 密码输入
    ├── 记住我
    └── 主按钮：登录并开启宝盒
```

## 交互说明

- 首页点击登录入口后执行 `showLogin()`：隐藏首页、显示登录页、滚动到顶部、写入 `#login`、聚焦第一个输入框。
- 登录页点击返回后执行 `showLanding()`：隐藏登录页、显示首页、清除 `#login`。
- 表单提交执行 `preventDefault()`，只用于原型展示与必填校验，不连接真实鉴权服务。
- 直接打开 `#login` 地址时自动展示登录页。

## 视觉说明

- 登录页背景复用首页产品视觉，并增加深色遮罩。
- 登录卡片居中，使用深色面板、细线边框、金色主按钮。
- 登录卡片顶部展示 MoonBox 产品 Logo。
- 截图已保存为 `prototype-login.png`，用于后续评审对照。

## 非范围说明

- 不包含首页视觉替换、首页导航、首页内容结构。
- 不包含忘记密码、申请体验、注册、第三方登录。
- 不包含真实登录接口、Token、会话保持、登录后跳转。
