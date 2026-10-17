---
bug_id: BUG-0027-page-scroll-bottom-light-background-exposed
title: 页面向上滑动时底部露出浅色背景追溯记录
status: done
created_at: 2026-10-04 23:23:29
updated_at: 2026-10-05 21:16:25
owner: 产品团队
source: /bug-capture
lifecycle_stage: archive
iteration: sprint-008
related_bug:
related_change: fix-page-scroll-root-background-exposed
openspec_changes:
  - change_id: fix-page-scroll-root-background-exposed
    type: fix
    status: archived
lifecycle:
  generated: 2026-10-04 23:30:07
  completed: 2026-10-04 23:36:44
  reviewed: 2026-10-04 23:40:44
  approved: 2026-10-04 23:40:44
  opsx_created: 2026-10-04 23:54:49
severity: medium
---

# 页面向上滑动时底部露出浅色背景追溯记录

## 当前摘要

用户反馈页面向上滑动时，底部会露出浅色背景。已补齐缺陷包并评审通过，根因状态为 confirmed：深色主题只作用于 Chat 工作台根容器，`body` 仍保持浅色背景，宿主 overscroll 或根容器边界外露时会显示浅色根层。当前已纳入 `sprint-008`，OpenSpec Change `fix-page-scroll-root-background-exposed` 已 apply 完成；下一步执行 `/opsx-archive BUG-0027-page-scroll-bottom-light-background-exposed`。

## 重复/相似检查

| 候选 | 当前状态 | 相似原因 | 处理方式 |
|---|---|---|---|
| 无明确候选 | N/A | BUG 看板与注册表中未发现同页面、同触发条件、同现象的记录；关键词检索仅命中历史背景词或无关滚动验收描述 | 新建独立 BUG |

## 证据摘要

| 证据 | 结论 |
|---|---|
| 用户截图 `screenshots/page-scroll-bottom-light-background-exposed.png` | 页面向上滑动后，深色主界面底部出现大面积浅色背景，属于视觉/滚动边界异常 |
| `/explore` 只读判断 | 根因状态为 probable/hypothesis；需要补充页面来源、视口、DOM 与 computed style 后才能确认根因 |
| Playwright computed style `logs/chat-page-computed-style.json` | `body.backgroundColor=rgb(244, 246, 250)`，`[data-testid=chat-shell].backgroundColor=rgb(10, 13, 20)`，证明根层浅色与 Chat 壳深色不一致 |
| Playwright 截图 `screenshots/chat-page-1440-evidence.png` | 本地产品 Chat 壳在 1440px 视口下可复核页面层级与深色工作台背景 |

## 待补证项

| 证据名称 | 为什么需要 | 需要返回的字段 | 脱敏要求 |
|---|---|---|---|
| 页面来源与环境 | 判断缺陷归属 MoonBox Web 页面、Chat 平台页面还是 Codex 客户端宿主壳 | 页面路由、运行环境、浏览器或客户端、窗口尺寸、是否全屏 | 不提供账号、Token、Cookie 或真实用户信息 |
| 关键布局 computed style | 判断是否由根背景、视口高度、滚动容器或 overflow 边界导致 | `html`、`body`、根节点、主布局容器的 `height`、`min-height`、`background-color`、`overflow`、`position` | 只返回样式值，不返回敏感 DOM 数据 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-05 21:16:25 | /opsx-archive | Change `fix-page-scroll-root-background-exposed` 已归档，状态同步完成。 |
| 2026-10-05 00:13:15 | /opsx-apply | Change `fix-page-scroll-root-background-exposed` apply 完成，待 archive。 |
| 2026-10-05 00:12:14 | /opsx-apply | Change `fix-page-scroll-root-background-exposed` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-10-05 00:01:24 | /opsx-apply | Change `fix-page-scroll-root-background-exposed` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-10-04 23:54:49 | /bug-opsx | in_sprint | 创建 OpenSpec Change `fix-page-scroll-root-background-exposed`，状态 proposed；下一步执行 /opsx-apply。 |
| 2026-10-04 23:51:02 | /sprint-propose | in_sprint | 已纳入 sprint-008，估算 M / 3 SP / 3 人天；下一步执行 /bug-opsx。 |
| 2026-10-04 23:40:44 | /bug-review | approved | 评审通过，确认按常规 Sprint 纳入修复；下一步先执行 /sprint-propose。 |
| 2026-10-04 23:38:13 | /bug-complete | BUG-0027-page-scroll-bottom-light-background-exposed 已完成文档补齐，状态同步为 pending_review。 |
| 2026-10-04 23:36:44 | /bug-complete | pending_review | 补齐 root-cause、workaround、acceptance；根因证据门禁通过，待评审。 |
| 2026-10-04 23:30:07 | /bug-generate | BUG-0027-page-scroll-bottom-light-background-exposed 已生成 bug.md，状态同步为 draft。 |
| 2026-10-04 23:23:29 | bug.capture | captured | 创建 BUG-0027，记录页面向上滑动后底部露出浅色背景的问题。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-10-05 21:09:47 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-page-scroll-root-background-exposed
