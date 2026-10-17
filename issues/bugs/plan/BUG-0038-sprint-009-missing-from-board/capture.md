---
bug_id: BUG-0038-sprint-009-missing-from-board
title: 需求看板未显示已存在的 sprint-009 迭代
status: captured
created_at: '2026-10-11 09:57:28'
updated_at: '2026-10-11 09:57:28'
severity: medium
environment: local Docker
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
---

# 需求看板未显示已存在的 sprint-009 迭代

## 现象

用户确认“迭代模板信息缺失”具体指 `sprint-009` 未进入需求看板的 Sprint 统计或选项。当前仓库有 `iterations/change/sprint-009/sprint.yaml` 且状态为 `planning`，本地 Firefox 刷新 `/requirements` 后页面仍显示 Sprint 8/8。

## 复现步骤

1. 核对当前仓库 `iterations/change/sprint-009/sprint.yaml` 与 `sprint.md` 存在。
2. 打开本地需求中心 `/requirements`，刷新页面，查看 Sprint 统计及筛选选项。
3. 核对运行服务实际绑定的治理根目录、授权快照及上下文接口返回的 Sprint 列表，再与当前仓库比较。

## 期望 vs 实际

- 期望：当前项目已存在且有效的 `sprint-009` 在 Sprint 统计和可选项中可见，规划状态按事实展示。
- 实际：当前仓库存在 `sprint-009`，运行页面刷新后仍显示 Sprint 8/8；运行服务读取的治理根目录尚未核实，不能仅凭仓库文件断言服务遗漏扫描。

## 影响与初判

- 严重度初判 `medium`：迭代总览和选项可能误导规划操作；未观察到 Sprint 数据被删除。
- 运行页面还出现当前仓库注册表没有的 BUG-0037～0039，提示页面与仓库可能读取不同治理快照；这是待验证假设，不作为已确认根因。
- 判重：BUG-0035 覆盖已生成 Sprint MD 文档在卡片后续阶段的入口；用户已明确本条是整个 `sprint-009` 未进入统计或选项，修复闭环独立。BUG-0016 的加载问题已归档，触发条件和范围不同。

## 附件

- 用户本次对话截图与 2026-10-11 本地 Firefox 刷新观察；未复制截图到仓库。
