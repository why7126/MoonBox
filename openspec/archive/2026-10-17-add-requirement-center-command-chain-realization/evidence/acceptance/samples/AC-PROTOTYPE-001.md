---
title: AC-PROTOTYPE-001 原型拆解与动作契约复核
created_at: 2026-10-13 15:00:00
updated_at: 2026-10-17 15:34:00
status: passed
---

# AC-PROTOTYPE-001 原型拆解与动作契约复核

`prototype/web/context.md` 已拆解页面层级、八动作、状态与浮层矩阵；Change `design.md` 的 UI Contract 保留八动作阶段契约，并新增原型候选 selector 到当前 DOM 的完整映射。实际卡片以 `article.rc-card[data-issue-id="完整 REQ ID"]` 限定对象；按钮按可访问名称、浮层按 `role="dialog"` 与名称定位，避免跨卡片误操作。`开始开发` 后按钮切换为 `查看进度`，不是仍显示原按钮；当前实现没有原型的 `req-action-*` 测试标识。

2026-10-17 运行 `NODE_OPTIONS=--no-experimental-webstorage npm --prefix src/web test -- --run src/requirement-center.test.tsx`：1 个测试文件、130 项通过，退出码 0。组件测试在渲染 DOM 中核对完整 ID 卡片作用域、生成/分析/完善/评审/迭代/OpenSpec/开发/归档按钮及相应浮层或进度入口。代码定位：`src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `renderIssueCard`、`renderActionDialog` 与 `actionModalCopy`；实际映射表在 Change `design.md`。本项只签认原型拆解与 selector 契约；1440/390 视觉和交互由 AC-PROTOTYPE-003/005 独立验收。

结论：**passed**。
