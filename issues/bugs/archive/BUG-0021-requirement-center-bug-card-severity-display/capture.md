---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: done
created_at: '2026-09-14 13:13:50'
updated_at: 2026-09-14 14:44:39
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0020-req-complete-status-projection-drift
environment: local
severity: medium
---

# 现象

需求中心 BUG 类型卡片不应显示优先级 P 值，而应显示 BUG 严重性 `severity`。用户提供截图显示 BUG-0020 卡片标签为 `P2`，但该 BUG 的事实源 `trace.md`、`bug.md` 与 `_registry.yaml` 均为 `severity: medium`。

严重度初判 medium：该问题违反 REQ/BUG 分级契约，可能误导缺陷评审、迭代排序和卡片快速判断；当前未发现数据丢失、权限越界、生产不可用或安全风险证据。

# 复现步骤

1. 打开需求中心页面。
2. 定位 BUG 类型卡片，例如 BUG-0020-req-complete-status-projection-drift。
3. 查看卡片元信息标签。
4. 对照 BUG-0020 的 `trace.md`、`bug.md` 和 `issues/bugs/_registry.yaml` 中的分级字段。

# 期望 vs 实际

| 项目 | 期望 | 实际 |
|---|---|---|
| BUG 卡片分级标签 | 显示 `severity`，例如 `medium` 或对应中文“中” | 显示 REQ 优先级格式 `P2` |
| REQ 卡片分级标签 | 继续显示 `priority`，例如 `P0` / `P1` / `P2` / `P3` | 不应受 BUG 修复影响 |
| API 响应契约 | REQ 暴露 `priority`，BUG 暴露 `severity`，不混用字段 | 当前展示链路疑似只暴露或只渲染 `priority` |

# 已有探索证据

- 规范要求 REQ 仅使用 `priority: P0|P1|P2|P3`，BUG 仅使用 `severity: blocker|critical|high|medium|low`，不得互相映射或把 BUG 严重度称为优先级。
- BUG-0020 的 `trace.md`、`bug.md` 与 `issues/bugs/_registry.yaml` 均记录 `severity: medium`。
- 只读探索发现需求中心响应模型与前端卡片渲染路径仍围绕 `priority` 字段展示分级标签，现有前端测试 fixture 也存在 BUG 使用 `priority` 的样本。

# 修复范围与建议验收

- BUG 卡片显示 `severity`，可显示原始值 `medium` 或产品确认的中文映射“中”。
- REQ 卡片仍显示 P0-P3。
- API 响应区分 REQ `priority` 与 BUG `severity`，并保持 Capture 创建时的字段契约一致。
- 后端构卡、前端渲染与前后端测试覆盖该差异。
- 不批量迁移历史归档正文；如发现当前活动 BUG 缺失合法 `severity`，应由 Workflow Sync 聚焦同步报告。

# 附件

用户截图显示 BUG-0020 卡片标签为 `P2`；截图作为当前会话证据，不复制或转存原始本机临时路径。
