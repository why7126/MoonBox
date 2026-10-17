---
bug_id: BUG-0027-page-scroll-bottom-light-background-exposed
title: 页面向上滑动时底部露出浅色背景
status: done
owner: 产品团队
discovered_at: 2026-10-04 23:23:29
environment: local
related_requirement:
related_change: fix-page-scroll-root-background-exposed
created_at: 2026-10-04 23:29:22
updated_at: 2026-10-05 21:16:25
severity: medium
---

# 页面向上滑动时底部露出浅色背景

## 现象

页面向上滑动或触发外层滚动后，深色主界面没有继续覆盖完整视口，底部露出大面积浅色背景。用户截图中，输入区仍处于深色面板内，右下角悬浮宠物位于浅色区域上方，整体呈现为深色页面与浅色宿主背景之间的视觉断层。

## 复现步骤

1. 打开出现问题的页面。
2. 在页面中向上滑动，或触发页面外层滚动、宿主 overscroll。
3. 观察页面底部是否出现浅色背景区域。

## 期望结果

页面在滚动、弹性滚动或视口边界变化时仍保持统一深色背景；主界面、输入区和悬浮元素下方不应暴露浅色宿主背景。

## 实际结果

向上滑动后，深色区域在输入区下方终止，底部大面积显示浅色背景，造成明显视觉断层。

## 影响范围

- 视觉影响：深色主题一致性被破坏，页面底部出现明显露底。
- 交互影响：当前证据尚未证明核心流程被阻断。
- 潜在范围：若该现象发生在 MoonBox Web 页面，可能影响使用 `.requirement-center` / Chat 工作台深色主题的页面；若发生在 Codex 客户端宿主界面，则缺陷归属可能不在当前仓库内。

## 严重等级说明

严重等级初判为 `medium`。理由：问题可见度高，影响深色主题页面的基础视觉完整性；但当前证据尚未显示数据错误、流程阻断、权限绕过或不可恢复操作失败。

## 根因摘要

根因状态已确认为 `confirmed`。浏览器取证显示，产品 Chat 壳 `[data-testid=chat-shell]` 为深色背景，但 `body` 仍保持浅色背景，且 `html` 与 `#root` 背景透明。结合用户截图可确认：当外层滚动、宿主 overscroll 或根容器高度边界外露时，用户看到的是浅色 `body` 根层背景。

完整证据链见 `root-cause.md`，浏览器 computed style 证据见 `logs/chat-page-computed-style.json`。

## 附件

- 截图：`screenshots/page-scroll-bottom-light-background-exposed.png`
