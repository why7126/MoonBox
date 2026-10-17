---
bug_id: BUG-0027-page-scroll-bottom-light-background-exposed
title: 页面向上滑动时底部露出浅色背景
status: done
created_at: 2026-10-04 23:23:29
updated_at: 2026-10-05 21:16:26
environment: local
related_requirement:
related_bug:
severity: medium
---

# 页面向上滑动时底部露出浅色背景

## 现象

页面向上滑动后，深色主界面未能覆盖完整视口，底部露出大面积浅色背景；截图中输入区仍处于深色面板内，右下角悬浮宠物位于浅色区域上方。

## 复现步骤

1. 打开出现问题的页面。
2. 在页面内向上滑动或触发页面外层滚动。
3. 观察页面底部背景区域。

## 期望 vs 实际

期望：页面在滚动或 overscroll 时仍保持统一的深色背景，主界面、输入区和悬浮元素下方不暴露宿主浅色背景。

实际：向上滑动后，深色区域在输入区下方终止，底部大面积显示浅色背景，造成明显视觉断层。

## 附件

- 截图：`screenshots/page-scroll-bottom-light-background-exposed.png`

## 初判

本条为单一视觉/滚动边界缺陷，不拆分。当前证据能证明现象存在，但尚未确认根因；后续需通过页面来源、视口尺寸、DOM 层级和 computed style 进一步补证。
