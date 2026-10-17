---
bug_id: BUG-0027-page-scroll-bottom-light-background-exposed
title: 页面向上滑动时底部露出浅色背景验收标准
acceptance_status: passed
created_at: 2026-10-04 23:36:44
updated_at: 2026-10-17 16:45:27
owner: 产品团队
---

# 页面向上滑动时底部露出浅色背景验收标准

## 回归 AC

- [x] AC-001：深色主题下访问 `/chat`，`html`、`body`、`#root` 与 `[data-testid=chat-shell]` 的背景不会形成浅色根层与深色页面壳不一致。
- [x] AC-002：1440px 桌面视口下，向上滑动或触发页面边界 overscroll 时，页面底部不再露出浅色背景。
- [x] AC-003：Chat 输入区、会话内容区、侧边栏和执行详情面板下方均保持深色工作台背景，不出现透明穿透。
- [x] AC-004：浅色主题下访问 `/chat`，全局根层背景与浅色工作台背景一致，不被深色修复误污染。
- [x] AC-005：访问 `/requirement-center`，深色与浅色主题的根层背景同步策略与 Chat 页面一致。
- [x] AC-006：Playwright 或等价浏览器取证记录 `body`、`#root`、工作台根容器的 computed style，并保存深色主题截图。
- [x] AC-007：修复不改变登录页、官网首页、管理后台的既有背景和滚动行为。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:27
accepted_by: workflow-sync
source_change: fix-page-scroll-root-background-exposed
source_sprint: sprint-008
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
