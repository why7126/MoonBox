---
bug_id: BUG-0043-requirement-center-card-width-sprint-tag-wrap
title: 需求中心卡片宽度与迭代标签换行根因分析
created_at: "2026-10-19 09:26:49"
updated_at: "2026-10-19 09:26:49"
status: confirmed
---

# 需求中心卡片宽度与迭代标签换行根因分析

## 根因状态

status: confirmed

确认范围是已观察的布局缺陷，尚未实施或验证修复。

## 现象

九阶段列宽固定 320px；长 Change ID 与 Sprint 同排时，`sprint-010` 在连字符处拆成两行。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | `screenshots/sprint-tag-wrap.png` | 用户截图显示长 ID 旁的 Sprint 标签换行 | 直接证明视觉缺陷 |
| E2 | computed_style | `capture.md` 同会话 Chrome 采样摘要 | `/requirements`、1470×697，九列均为 320px；标签 white-space: normal、flex-shrink: 1、高度 35px | 标签具备换行和被压缩条件 |
| E3 | code_path | `src/web/src/styles/globals.css` 的 `.rc-board`、`.rc-card-top`、`.rc-sprint-tag` | 固定九列 320px，顶部 flex；标签无单行和禁止压缩约束 | 解释空间竞争与断行路径 |
| E4 | code_path | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的共用卡片渲染 | ID strong 与 Sprint span 同属 `.rc-card-top` | 触发条件为长 ID 与标签同排 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| Sprint 数据缺失造成显示不完整 | E1、E2 中完整文本为 sprint-010，实际是排版折行 |
| 仅验收阶段特有的样式问题 | 附件为验收中，同会话已完成卡片也出现问题，E3、E4 为共用样式与渲染路径 |

## 已确认根因

固定列宽限制可用空间，长 ID 与 Sprint 标签在同一 flex 行内竞争宽度。标签默认允许收缩和普通换行，使含连字符的 Sprint 编号在空间不足时折行。仅扩宽不能保证更长 ID 场景的稳定性，需同步明确标签与 ID 的空间分配。

## 修复方向

九列共用宽度改为 380px；标签使用单行与禁止收缩约束，ID 允许在剩余空间内收缩、合理折行。保留横向滚动与业务交互，不改变 Sprint 显示条件或业务状态。

## 验证闭环

现象、计算样式与代码路径已相互印证；浏览器采样为同会话已加载页面，未刷新，不用于证明后端当前可用。修复后按 acceptance.md 的 AC-001 至 AC-005 重新采集截图、计算样式和交互证据；本次缺陷完善不宣称这些验收已经通过。
