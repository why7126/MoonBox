---
change_id: fix-requirement-center-bug-card-severity-display
type: fix
source_bug: BUG-0021-requirement-center-bug-card-severity-display
status: proposed
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:12:36
owner: 产品团队
---

# 修复需求中心 BUG 卡片严重性展示

## 背景

BUG-0021 记录了需求中心 BUG 类型卡片显示 REQ 优先级 P 值，而不是 BUG 严重性 `severity` 的问题。样本 BUG-0020 的 `trace.md`、`bug.md` 与 `_registry.yaml` 均为 `severity: medium`，但卡片显示 `P2`。

根因证据显示需求中心卡片模型和展示链路沿用 REQ `priority` 作为通用分级字段：后端响应模型没有 `severity`，构卡函数对所有 Issue 统一写入 `priority` 并在缺失时默认 `P2`，前端卡片也只渲染 `issue.priority`。这违反 Issue 分级元数据契约，并会误导 BUG 评审、迭代排序和治理看板阅读。

## 变更范围

- 后端需求中心卡片响应区分 REQ `priority` 与 BUG `severity`。
- BUG 卡片不得因缺少 `priority` 被默认投影为 `P2`。
- 前端卡片标签按类型展示：REQ 显示 P0-P3，BUG 显示 `blocker|critical|high|medium|low` 或产品确认的中文映射。
- 更新后端 API / 构卡测试与前端卡片测试，移除 BUG fixture 对 `priority` 的依赖。
- 保持独立 Change 卡片、文档入口、负责人、Sprint 标签和任务进度展示不回退。

## Out of Scope

- 不批量迁移历史归档正文。
- 不改变 Capture 创建字段契约。
- 不新增数据库表、迁移、行为埋点、Task Trace 或对象存储能力。

## Product Data Collection / Observability

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
  reason: 本修复涉及需求中心上下文 API 响应字段与 Web 卡片展示契约；不新增 DB、usage_events、task_traces、task_trace_spans、对象存储或部署拓扑。
  validation: 验证 API 响应中 REQ/BUG 分级字段不混用；确认请求日志、行为事件和 Task Trace 无新增字段或落地需求。
```

## 回滚方案

若修复导致需求中心卡片无法渲染或筛选异常，回滚后端 schema / 构卡逻辑和前端卡片标签分流改动，恢复现有 `priority` 字段展示；保留 BUG-0021 文档并记录回滚原因。回滚后必须继续通过临时规避，以 BUG `trace.md` / `bug.md` / `_registry.yaml` 的 `severity` 判断严重性。
