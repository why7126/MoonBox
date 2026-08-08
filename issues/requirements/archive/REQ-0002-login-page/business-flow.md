---
requirement_id: REQ-0002-login-page
title: Web 端登录页业务流程
status: archived
owner: product
source: requirement.md
created_at: 2026-08-07 18:03:43
updated_at: 2026-08-07 18:03:43
---

# Web 端登录页业务流程

## 主流程

```text
用户访问官网首页
  |
  | 点击登录入口 / CTA
  v
前端执行 showLogin()
  |
  |-- 隐藏 landingPage
  |-- 显示 loginPage
  |-- 滚动到顶部
  |-- 写入 #login 页面状态
  |-- 聚焦用户名输入框
  v
用户查看登录页
  |
  | 输入用户名、密码，可选择记住我
  v
点击“登录并开启宝盒”
  |
  |-- 浏览器执行必填校验
  |-- 原型拦截 submit 默认行为
  |-- 不请求真实鉴权接口
  v
保持在登录页原型状态
```

## 返回首页流程

```text
用户位于登录页
  |
  | 点击“返回首页”
  v
前端执行 showLanding()
  |
  |-- 隐藏 loginPage
  |-- 显示 landingPage
  |-- 清除 #login 页面状态
  v
用户回到官网首页
```

## 异常与边界流程

```text
用户直接打开带 #login 的地址
  |
  v
前端检测 location.hash === '#login'
  |
  v
显示登录页并聚焦用户名输入框
```

```text
用户未填写用户名或密码并提交
  |
  v
浏览器原生 required 校验提示
  |
  v
阻止提交，保持登录页
```

## 与父级或相邻需求差异

- 与 `REQ-0001-homepage` 的差异：本需求只定义登录页本身、首页进入登录页的状态跳转，以及返回首页行为；首页 Logo、首页首屏右侧视觉、首页正文结构和 CTA 文案由 `REQ-0001-homepage` 承接。
- 与后续认证能力的差异：本需求不定义后端鉴权、Token、会话保持、权限路由和登录成功后的工作台加载；这些内容应由后续认证或产品工作台需求承接。
