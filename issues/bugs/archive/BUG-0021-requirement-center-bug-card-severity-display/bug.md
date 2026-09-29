---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: done
owner: 产品团队
discovered_at: '2026-09-14 13:13:50'
environment: local
related_requirement: REQ-0012-frontend-requirement-center
related_change: null
related_bug: BUG-0020-req-complete-status-projection-drift
created_at: 2026-09-14 13:13:50
updated_at: 2026-09-14 14:44:34
severity: medium
---

# 现象

需求中心 BUG 类型卡片不应显示 REQ 优先级 P 值，而应显示 BUG 严重性 `severity`。用户提供截图显示 BUG-0020 卡片标签为 `P2`，但 BUG-0020 的事实源 `trace.md`、`bug.md` 与 `issues/bugs/_registry.yaml` 均为 `severity: medium`。

# 复现步骤

1. 打开需求中心页面。
2. 定位 BUG 类型卡片，例如 BUG-0020-req-complete-status-projection-drift。
3. 查看卡片元信息中的分级标签。
4. 对照该 BUG 的 `trace.md`、`bug.md` 和 `issues/bugs/_registry.yaml` 分级字段。

# 期望 vs 实际

| 项目 | 期望 | 实际 |
|---|---|---|
| BUG 卡片分级标签 | 显示 `severity`，例如 `medium` 或对应中文“中” | 显示 REQ 优先级格式 `P2` |
| REQ 卡片分级标签 | 继续显示 `priority`，例如 `P0` / `P1` / `P2` / `P3` | 不应受 BUG 修复影响 |
| API 响应契约 | REQ 暴露 `priority`，BUG 暴露 `severity`，字段不混用 | 当前展示链路疑似只暴露或只渲染 `priority` |

# 影响范围

- 需求中心 BUG 卡片的快速分级识别。
- BUG 评审、迭代排序和治理看板阅读体验。
- API 响应模型、后端构卡逻辑、前端卡片渲染和相关测试 fixture 的 REQ/BUG 分级契约一致性。

当前未发现数据丢失、权限越界、真实客户数据泄漏、生产不可用或安全风险证据。

# 严重等级说明

严重等级为 medium。

该问题违反项目的 Issue 分级元数据契约，会把 BUG 严重性误呈现为 REQ 优先级格式，影响治理判断和迭代排序参考；但目前没有证据表明它阻断核心业务流程或造成数据破坏。

# 建议验收

- BUG 卡片显示 `severity`，例如 `medium` 或产品确认的中文映射“中”。
- REQ 卡片仍显示 P0-P3。
- API 响应区分 REQ `priority` 与 BUG `severity`，不混用字段。
- 后端构卡、前端渲染与前后端测试覆盖 REQ/BUG 分级差异。
- 不批量迁移历史归档正文；如发现当前活动 BUG 缺失合法 `severity`，由 Workflow Sync 聚焦同步报告。
