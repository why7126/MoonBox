---
title: 独立 Change 创建时自动分级与卡片只读展示原型拆解
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:25:42'
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 创建时自动分级与卡片只读展示原型拆解

## 页面与数据边界
需求中心交付看板的局部卡片原型，HTML 为 Mock，不调用 API、不执行保存、不表示实际产品验收完成。PNG 暂不要求，留待实现阶段对真实产品采集。页面清单仅需求中心，看板壳、列头、卡片、标题、标签、文档链接、底部动作构成层级。

## UI Reference Replication Contract 种子
模式为局部一致；用户截图界定要移除的入口和保留区域，当前组件/token 为保留区样式来源，PRD 为业务语义来源。原型只表达结构与状态，不覆盖既有全页布局。保留卡片标题、负责人、工作量、文档与交付动作；变更标签维度、缺失文案并删除设置入口。非目标为整体重设计、任何新增分级浮层及改变验收逻辑。

| 区域 | 原型 selector | 产品 selector 候选 | 检查 |
|---|---|---|---|
| 卡片 | .card | [data-testid=rc-delivery-card] | 层级、宽度、overflow |
| 分级 | .level | .rc-priority-tag / .rc-severity-tag | 文字、字体、padding、颜色 |
| 保留元信息 | .meta | .rc-card-meta | gap、换行 |
| 删除编辑 | 不存在 | [data-testid=change-priority-edit] / [data-testid=change-priority-editor] | DOM 和焦点均不存在 |
| 底部动作 | .actions | .rc-card-actions | 原能力保留 |

## 状态矩阵与交互
fix/high、non_fix/P2、fix 缺失、non_fix 非法各一张 Mock 卡片；实际验收扩展来源 Issue、类型冲突、各交付阶段、只读和权限态。标签只读无点击；标题/文档/返修等保留动作在 Mock 仅以静态文字标明，真实产品继续原交互。

动作矩阵：设置优先级 → 原内联编辑 → change-priority-edit/editor → 全状态删除 → DOM/键盘/Network 证据；保留的返修、验收、归档动作 → 原有组件与流程 → .rc-card-actions 内原 selector → 原状态 → 回归证据。无新增 modal，实施前核对保留动作族的精确 selector，不重建其组件。

## 响应式及分批门禁
原型大于 700px 两列，小于等于 700px 单列；这是状态比较布局，不替换实际看板断点。实际产品遵循既有断点。1440px 检查信息顺序、字号、标签、空白回收；390px 检查换行无横向溢出。第一批确认 Skeleton 及标签状态，第二批核验无编辑入口和保留动作，第三批双视口双主题与数据回读。computed style 清单及证据矩阵见 acceptance.md。

## REQ-0059 实施证据

用户已确认卡片结构并沿用既有样式。实现、selector动作矩阵、Mock/API边界、真实CLI观察及视觉证据见 `openspec/changes/update-standalone-change-auto-classification/evidence/acceptance/implementation-review.md`；原型状态比较布局不替代产品看板。
