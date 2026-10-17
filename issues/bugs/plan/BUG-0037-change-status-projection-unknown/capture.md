---
bug_id: BUG-0037-change-status-projection-unknown
title: 需求看板将端口迁移 Change 误判为状态异常
status: captured
created_at: '2026-10-11 09:57:28'
updated_at: '2026-10-11 09:57:28'
severity: medium
environment: local Docker
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
---

# 需求看板将端口迁移 Change 误判为状态异常

## 现象

需求研发流转看板将 `migrate-local-host-ports-to-39000-range` 列入“数据异常”，提示状态或归档版本存在歧义，并将其排除在统计之外。用户提供截图后，在 Firefox 刷新本地 `/requirements` 页面仍见该异常。

## 复现步骤

1. 在本地 Docker 环境打开需求中心 `/requirements`，刷新看板。
2. 展开“数据异常”，观察端口迁移 Change 的提示及统计排除情况。
3. 对照 Change 的 `trace.md`、`tasks.md` 和 `sprint-009/sprint.yaml`，核对状态事实、任务进度与迭代归属。

## 期望 vs 实际

- 期望：看板依据有效的 Change 生命周期事实展示阶段；数据不足时指出缺失字段，并保留可追溯的诊断。
- 实际：该 Change 显示为状态异常且不计入统计。仓库 `tasks.md` 为 4/4，但 `trace.md` 未见新版索引所需的 `status` 或 `execution` 字段；运行服务所读文件版本仍待核实。

## 影响与初判

- 严重度初判 `medium`：影响 Change 可见性和看板统计，尚无数据丢失或越权证据。
- 只读定位显示 `ChangeIndex` 对缺少有效状态的活动 Change 投影为 `unknown`；运行服务与当前仓库的数据源是否一致，需在后续补证中确认。
- 判重：已归档 BUG-0020 涉及 REQ 完善后的状态传播；进行中的 BUG-0035 涉及验收投影及文档入口，均非本 Change 状态缺失与异常排除场景。

## 附件

- 用户本次对话截图（未复制到仓库）；2026-10-11 Firefox 本地页面刷新观察。不得将截图中的用户信息或完整接口响应写入公开文档。
