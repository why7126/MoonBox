---
requirement_id: REQ-0001-homepage
status: archived
created_at: 2026-07-30 08:21:16
updated_at: 2026-08-07 18:03:48
---

# 首页用户故事

## US-001 未登录访客识别 MoonBox 品牌

作为首次访问 MoonBox 官网的未登录访客，我希望在首屏立即看到 MoonBox Logo、品牌定位和产品视觉，以便判断这是一个 AI Native Software Factory 产品。

验收要点：

- 首页左上角展示 `Logo1-20260728001940.png`。
- 首屏出现英文定位文案 `AI Native Software Factory`。
- 首屏右侧展示 `image.png`，且主体清晰可辨。

## US-002 潜在客户理解核心价值

作为潜在客户或体验申请用户，我希望首页首屏保留核心标题、说明文案和三项能力摘要，以便快速理解 MoonBox 的产品组成。

验收要点：

- 首屏左侧展示标题 `Open the box, own a software company`。
- 首屏说明 MoonBox 将 Harness、Agent Workflow 和 product knowledge 组织到一个 AI-native software factory。
- 首屏下方展示 `Agent Workflow`、`Product Knowledge`、`Delivery Harness` 三项能力。

## US-003 用户从首页进入登录入口

作为准备打开 MoonBox 的用户，我希望首页提供明确 CTA，以便继续进入既有登录页流程。

验收要点：

- 顶部右侧展示 `Open first project`。
- 首屏左侧展示 `Open MoonBox`。
- 两个 CTA 均沿用既有登录页入口，不改变跳转目标。

## US-004 产品团队控制 Patch 范围

作为产品与设计团队，我希望本次首页更新只替换指定品牌资产并保留 v1.0.1 首页结构，以便降低 Patch 影响面。

验收要点：

- 仅允许更新 Logo 与首屏右侧产品视觉。
- 不改变首页已保留的 Features、Closing、Footer 与既有交互。
- 不把登录页表单、返回首页、登录页背景等能力纳入首页需求。
