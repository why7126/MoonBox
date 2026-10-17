---
bug_id: BUG-0039-standalone-change-sprint-membership-false-warning
title: 需求中心纯 Change 卡片误报缺少 Sprint 归属
status: captured
created_at: '2026-10-11 10:02:20'
updated_at: '2026-10-11 10:02:20'
severity: medium
environment: local Docker
related_requirement: REQ-0026-requirement-center-standalone-change-cards
related_bug: null
---

# 需求中心纯 Change 卡片误报缺少 Sprint 归属

## 现象

用户截图中，需求中心“验收中”的纯 Change 卡片 `enable-agent-browser-product-evidence` 与 `add-git-sync-skill` 均显示“缺少唯一有效的 Sprint 归属”，前者还缺少 Sprint 标签。仓库中的 Sprint 范围分别包含这两个 Change：`sprint-008` 和 `sprint-009`。本条要求从产品卡片的归属解析、状态投影、动作提示与运行数据一致性解决误报，而非仅修订 Change 文档。

## 复现步骤

1. 打开需求中心，定位上述纯 Change 卡片，查看 Sprint 标签及“完成 / 归档”动作提示。
2. 对照对应 Sprint `sprint.yaml` 的 `changes[]`、Change `trace.md` 的迭代字段及页面上下文接口响应。
3. 刷新页面，并在当前运行服务中分别检查活动 Change 与已归档 Change 的卡片状态和归属。

## 期望 vs 实际

- 期望：当唯一有效的 Sprint `changes[]` 包含纯 Change，且 Change 归属元数据一致时，卡片显示正确 Sprint，并且不以“缺少归属”阻断动作；字段或快照冲突时给出可核查的原因。
- 实际：用户截图中两个卡片显示相同的缺少归属提示。`enable-agent-browser-product-evidence` 的 trace 使用 `sprint: sprint-008`，产品索引当前读取 `iteration`，这是该对象误报的可复核代码路径。`add-git-sync-skill` 的归档 trace 已写 `iteration: sprint-009`，但截图是归档前旧状态；当前运行服务是否仍复现需进一步取证。

## 影响与初判

- 严重度初判 `medium`：卡片误导 Sprint 归属与归档准备判断；目前没有证据表明 Sprint 范围数据丢失。
- 产品排查需覆盖 trace 字段兼容、Sprint `changes[]` 唯一性、活动/归档状态投影，以及运行服务所读治理根目录和缓存版本；不得通过放宽真实缺失或多重归属的门禁掩盖异常。
- 两个实例位于同一需求中心纯 Change 卡片功能面，先按一条产品缺陷记录；第二实例是否另有独立运行态原因，由后续取证决定。
- 判重：BUG-0038 处理 Sprint 本身未进入统计/选项；BUG-0035 处理验收投影和文档入口；已归档 BUG-0018 处理验收来源误报。现象和验收闭环均不同。

## 附件

- 用户本次对话截图；未复制到仓库，截图显示 2026-10-09 的卡片状态。
