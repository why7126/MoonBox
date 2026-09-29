---
change_id: fix-requirement-center-bug-card-severity-display
source_bug: BUG-0021-requirement-center-bug-card-severity-display
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:38:53
---

# 设计说明

## 根因

需求中心卡片数据模型与展示链路把 `priority` 当作 REQ/BUG 通用分级字段：

- `RequirementCenterIssue` 响应模型只有 `priority: str = "P2"`。
- 后端构卡统一写入 `priority=str(entry.get("priority") or "P2")`。
- 前端 `IssueCard` 类型只定义 `priority`，卡片标签只渲染 `issue.priority`。
- 测试 fixture 中 BUG 样本仍使用 `priority`。

因此 BUG 即使事实源为 `severity: medium`，也会被卡片投影为 `P2`。

## 修复方案

1. 后端响应模型增加 `severity` 字段或等价类型表达，并允许 REQ/BUG 分级字段按类型分流。
2. 后端构卡逻辑：
   - REQ：读取 `priority`，合法值为 P0/P1/P2/P3。
   - BUG：读取 `severity`，合法值为 blocker/critical/high/medium/low。
   - BUG 缺失或非法 `severity` 时输出可诊断信息，不静默猜测为 P 值。
3. 前端类型和渲染：
   - `IssueCard` 支持 `severity`。
   - 卡片标签按 `issue.type` 分流展示。
   - 标签 class 同时携带分级值，REQ 使用 `p0`、`p1`、`p2`、`p3`，BUG 使用 `blocker`、`critical`、`high`、`medium`、`low`，供 CSS 按等级着色。
   - 筛选条件若继续使用“优先级”控件，不得误过滤 BUG 严重性；本 Change 至少保证卡片展示不混用。
4. 测试：
   - 后端 API / 构卡测试覆盖 REQ priority 与 BUG severity。
   - 前端测试 fixture 改为 BUG 使用 severity，断言 BUG 卡片不显示 P 值，并覆盖分级标签按等级映射颜色。
   - 保留 REQ P0-P3 显示和独立 Change 卡片不回退。

## 兼容性

历史归档 BUG 文档不批量迁移；构卡读取以当前 trace/registry 的合法 `severity` 为事实源。若个别历史样本仍保留旧 `priority` 字段，聚焦 Workflow Sync 按 Issue 分级元数据规则处理，不在本 Change 中批量清理。

## 测试策略

- 后端：聚焦需求中心上下文构卡 / API 集成测试。
- 前端：Vitest / Testing Library 覆盖卡片标签展示。
- 合同：如 OpenAPI / generated 类型受影响，执行对应生成或校验，并只复核目标 schema。
- 回归：文档入口、负责人、Sprint 标签、任务进度和独立 Change 卡片不回退。
