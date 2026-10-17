---
title: 规划卡片状态与长负责人视觉复核
created_at: 2026-10-13 19:49:00
updated_at: 2026-10-14 09:00:00
---

# 规划卡片状态与长负责人视觉复核

在 BUG-0025 专用隔离产品 `http://127.0.0.1:39102/requirements` 登录后，从需求中心筛选 `REQ-0041`（registry `draft/plan`）和 `BUG-0036`（registry `enriching/plan`）。两者均位于“规划中”，1440×900 与 390×900 四组产品画面分别见同目录 `AC-044-{draft,enriching}-{1440x900,390x900}.png`，对应 DOM `getComputedStyle` 见同名 `-style.json`。

- 两种状态的卡片元信息仅有 2 个标签：草稿为 `P1` 与“产品团队”，完善中为 `low` 与长负责人；未渲染独立“草稿”或“完善中”标签。
- BUG-0036 长负责人在两个视口均占 223.9375px，`overflow:hidden`、`text-overflow:ellipsis`、`white-space:nowrap`；DOM `title` 是完整负责人标识。`low` 标签宽 34.0625px，与负责人不重叠且画面可见。草稿 `P1` 也可见。
- REQ-0041 保留 `requirement.md`、`trace.md`、`capture.md` 与“完善需求”入口；BUG-0036 保留 `bug.md`、`trace.md`、`acceptance.md`、`capture.md`、`root-cause.md`、`workaround.md`，根因补证提示与“继续完善”入口。BUG-0036 在隔离事实源中仍为 `enriching`，未因卡片显示简化而越过内部完成门禁。

以上为当前隔离产品的真实视觉与 DOM 观察。内部卡片规则同时由 AC-044 聚焦 Vitest 命令复验；其他 AC 的结论互不替代。
