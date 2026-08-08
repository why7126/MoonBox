---
requirement_id: REQ-0001-homepage
prototype: homepage
source_version: MoonBox Landing v1.0.2
status: pending_review
created_at: 2026-07-30 08:21:16
updated_at: 2026-07-30 08:21:16
---

# 首页原型上下文

## 来源

- 产品原型上下文：`/Users/why7126/Downloads/MoonBox-Landing-v1.0.2/prototype-context.md`
- 产品原型 HTML：`/Users/why7126/Downloads/MoonBox-Landing-v1.0.2/prototype.html`
- 首页截图：`/var/folders/26/jcqks9nx23185wqvs17rzgkw0000gn/T/codex-clipboard-e5fe34e5-bcdf-45b5-bc9b-3ebd58e8ebe7.png`

## 抽取范围

仅抽取 `landingPage` 首页内容：

- 顶部品牌区 `nav .brand`
- 顶部右侧 CTA `Open first project`
- 首屏左侧定位、标题、说明文案和 `Open MoonBox` CTA
- 首屏右侧产品视觉 `.stage img`
- 三项能力摘要：`Agent Workflow`、`Product Knowledge`、`Delivery Harness`

## 资产

- `assets/Logo1-20260728001940.png`：首页左上角品牌 Logo。
- `assets/image.png`：首页首屏右侧产品视觉。

## 跳转边界

- 首页两个 CTA 对应原型中的 `[data-open-login]`，进入既有登录页入口。
- 本首页需求不定义 `#login` 页面、登录表单、返回首页、登录背景遮罩和必填校验。

## 设计约束

- 深色主题背景、金色强调按钮、近直角按钮与克制排版。
- 保持左文案右视觉的首屏结构。
- 不新增首页模块，不改变 v1.0.1 Features、Closing、Footer。
- 移动端允许双栏折叠为单列，但必须保证 Logo、标题、CTA 和产品视觉不互相遮挡。

## 待导出

- `prototype/web/homepage.png`：可在后续评审或实现前从 `homepage.html` 导出。
