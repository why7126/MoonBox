---
requirement_id: REQ-0001-homepage
status: archived
created_at: 2026-07-30 08:21:16
updated_at: 2026-08-07 18:03:48
---

# 首页业务流程

## 首页浏览流程

```text
未登录访客
  |
  v
进入 MoonBox 官网首页
  |
  v
识别顶部品牌 Logo + 顶部 CTA
  |
  v
阅读首屏定位、标题、说明文案
  |
  v
查看右侧产品视觉 image.png
  |
  v
浏览三项核心能力摘要
  |
  +--> 点击 Open MoonBox --------+
  |                              |
  +--> 点击 Open first project --+--> 进入既有登录页入口（REQ-0002）
```

## 页面结构

```text
Homepage
├── Header
│   ├── brand: Logo1-20260728001940.png
│   └── cta: Open first project
├── Hero
│   ├── eyebrow: AI Native Software Factory
│   ├── title: Open the box, own a software company
│   ├── description: MoonBox puts Harness, Agent Workflow and product knowledge into one AI-native software factory.
│   ├── primary cta: Open MoonBox
│   └── visual: image.png
└── Feature Summary
    ├── 01 Agent Workflow
    ├── 02 Product Knowledge
    └── 03 Delivery Harness
```

## 与原始混合需求的边界差异

- 原始设计稿同时包含 `landingPage` 与 `loginPage`，本需求仅抽取 `landingPage`。
- `showLogin()`、`#login`、返回首页、登录表单、记住我等登录页逻辑由 `REQ-0002-login-page` 承接。
- 首页只保证 CTA 继续指向既有登录入口，不定义登录页表单行为。

## 与父需求差异

无父需求。本需求来源于 `REQ-0001-homepage` capture，并基于 MoonBox Landing v1.0.2 设计原型完善。
