---
requirement_id: REQ-0001-homepage
title: MoonBox 官网首页品牌视觉更新
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement:
created_at: 2026-08-07 18:03:41
updated_at: 2026-08-07 18:03:59
---

# MoonBox 官网首页品牌视觉更新

## 背景

MoonBox Landing v1.0.2 设计稿将官网首页与登录页放在同一份 Patch 需求中描述。为保证需求边界清晰，本需求仅抽取首页相关内容，聚焦官网首页的品牌 Logo 与首屏产品视觉更新；登录页登录方式、返回首页、登录卡片 Logo 与登录背景等内容归属 `REQ-0002-login-page`。

当前首页已具备 Landing Page 基础结构。本次需求以 v1.0.1 为基线，在不改变首页信息架构、正文内容、CTA 流程和既有设计系统的前提下，替换首页品牌资产并强化首屏产品表达。

## 目标用户

- 未登录访客：首次访问 MoonBox 官网，希望快速理解 MoonBox 的品牌与产品形态。
- 潜在客户或体验申请用户：通过首页首屏识别产品定位，并通过既有 CTA 进入后续登录或体验流程。
- 产品与设计团队：需要确保官网首页与最新品牌资产一致，且 Patch 更新不会影响既有首页结构。

## 范围

### 包含

- 首页左上角品牌 Logo 更新为 `Logo1-20260728001940.png`。
- 首页首屏右侧产品视觉更新为 `image.png`。
- 保留首页首屏左侧标题、描述文案与 CTA。
- 保留两个首页 CTA 进入同一登录页的既有流程。
- 保留 v1.0.1 首页其余模块、交互与视觉，包括 Features、Closing、Footer 及已删除顶部四个导航项的结果。

### 不包含

- 不设计或实现登录页表单、返回首页、登录卡片 Logo、登录页背景遮罩等能力。
- 不新增真实登录鉴权、后端接口、会话管理或权限联动。
- 不调整首页信息架构、导航策略、文案体系、CTA 目标或设计系统 token。
- 不新增移动端、小程序、桌面端或管理后台首页能力。

## 功能要求

### FR-001 首页品牌 Logo

首页导航左上角 MUST 展示 `Logo1-20260728001940.png` 作为 MoonBox 品牌标识，并保持现有导航区位置、布局层级与品牌入口语义。

### FR-002 首屏产品视觉

首页首屏右侧 MUST 展示用户提供的第一张图 `image.png`，用于表达 MoonBox 产品视觉与软件工厂感知。

该视觉 SHOULD 保持清晰可辨，不应被过度裁切、遮挡或拉伸变形。

### FR-003 首屏左侧内容保持

首页首屏左侧标题、描述文案与 CTA MUST 延续 v1.0.1 既有内容和交互，不因本次视觉替换发生文案、布局或目标页面变化。

### FR-004 CTA 入口保持

首页两个 CTA MUST 继续进入同一登录页入口，且本次首页需求不得改变 CTA 的业务含义、触发方式或跳转目标。

### FR-005 既有首页内容保持

除品牌 Logo 与首屏右侧产品视觉外，首页 Features、Closing、Footer、整体结构和设计系统表现 MUST 与 v1.0.1 保持一致。

## UI 约束

- 首页首屏需要优先呈现 MoonBox 品牌和产品视觉，首屏右侧图片应成为明确的第一屏视觉信号。
- Logo 替换不得导致导航高度、品牌区域对齐或响应式布局出现明显跳动。
- 产品视觉在桌面端与移动端均需保持主体可识别，移动端可按既有响应式规则重排。
- 禁止为本次 Patch 引入新的装饰风格、颜色体系或营销模块。
- 若首页与登录页复用同一产品视觉资产，首页侧仍以清晰展示为主，不继承登录页的深色遮罩策略。

## 关联需求

- `REQ-0002-login-page`：登录页功能。外部设计稿中的登录页返回首页、登录页品牌、用户名密码登录等内容应由该需求承接。

## 状态块

```yaml
status: archived
generated_at: 2026-07-30 08:12:07
completed_at: 2026-07-30 08:21:16
reviewed_at: 2026-07-30 08:27:02
approved_at: 2026-07-30 08:27:02
source_material:
  - <local-downloads>/MoonBox-Landing-v1.0.2/requirement.md
  - <local-downloads>/MoonBox-Landing-v1.0.2/patch-request.md
  - <local-downloads>/MoonBox-Landing-v1.0.2/prototype-context.md
next: /req-opsx REQ-0001-homepage
```
