---
title: BUG-0035 隔离阶段样本与正式归档尝试观察
created_at: 2026-10-12 16:30:00
---

# BUG-0035 隔离阶段样本与正式归档尝试观察

## AC-009：隔离样本

在临时治理源副本及临时 SQLite 中新增 `sprint-909` 与三个可清理样本，未写入正式 Issue、Change 或 Sprint。Firefox 当前构建的需求中心读取到：

| 样本 | 阶段 | 页面观察 |
|---|---|---|
| BUG-9101 | 迭代规划 | Issue 7 份文档、Sprint 3 份文档，无 Change 分组。 |
| BUG-9102 | 待开发 | Issue 7 份、Change 5 份、Sprint 3 份，研发 0/1。 |
| BUG-9103 | 研发中 | Issue 7 份、Change 5 份、Sprint 3 份，研发 0/1。 |

Firefox 无障碍树确认上述阶段与文档入口。响应式工具栏分别设为 1440×900、390×844，但其导出截图仍为整窗 2880×1800，并把目标卡片裁在看板右缘，不能作为双视口卡片视觉证据。未取得这三个样本的可复核 computed style 或完整文档点击结果。因此 AC-009 仍未签认；既有验收阶段的双视口截图与样式记录见 Change `acceptance-fixes.md`。

## AC-010：正式 BUG-0025 归档尝试

用户授权后，在正式 BUG-0025 对象 Chat 会话发送 `/opsx-archive BUG-0025-requirement-center-command-chain-write-gap`。本轮 `turn_id=f3d624c6-2422-4eee-9a49-3181af97d5fd`，UTC 2026-10-12 08:03:48 至 08:06:59，轮次状态 completed。只读 SQLite 事件记录显示归档脚本对应工具事件 `sequence=42` 为 failed、退出码 1；交付证据检查事件 `sequence=45` 为 completed、退出码 0。脚本报告任务 80/81，且规格合并校验失败；未进入 acceptance readiness 门禁。归档后的 Workflow Sync、Issue promote 和 AI Usage hook 均未执行。正式 Change 和 Issue 仍位于活动目录。

此轮证明正式归档未发生，但不能证明缺少验收签认触发归档门禁。AC-010 继续未签认。产品原始消息、原始事件 payload、数据库与临时凭据均未复制进证据包。

## 后续补证

随后重新设置并提交 Firefox 响应式视口，取得七个 Issue 阶段与独立 Change 的 1440px/390px 完整截图。各对象、截图、关键交互和既有 computed style 来源见 `phase-matrix-1440-390.md`；AC-009 已技术签认。本文件前述“截图未取得”仅描述首次尝试，不代表最终状态。AC-010 的阻塞结论不变。
