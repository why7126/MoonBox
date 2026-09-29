---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
acceptance_status: passed
created_at: 2026-09-14 14:01:07
updated_at: 2026-09-29 14:41:41
severity: medium
---

# 验收标准

## AC-BUG-0021-01 BUG 卡片显示严重性

给定 BUG 事实源 `severity: medium`，当用户打开需求中心并查看该 BUG 卡片时，卡片分级标签显示 BUG 严重性 `medium` 或产品确认的中文映射“中”，不得显示 `P2`。

## AC-BUG-0021-02 REQ 卡片继续显示优先级

给定 REQ 事实源 `priority: P0|P1|P2|P3`，当用户打开需求中心并查看 REQ 卡片时，卡片分级标签继续显示对应 P 值。

## AC-BUG-0021-03 API 字段不混用

需求中心上下文 API 中，REQ 卡片数据使用 `priority` 表达优先级，BUG 卡片数据使用 `severity` 表达严重性；BUG 不得因缺少 `priority` 被默认投影为 `P2`。

## AC-BUG-0021-04 缺失或非法分级可诊断

当 BUG 活动事实源缺失或包含非法 `severity` 时，同步或构卡链路应提供可诊断提示，不得静默猜测默认 P 值。

## AC-BUG-0021-05 测试覆盖

后端 API / 构卡测试覆盖 REQ `priority` 与 BUG `severity` 分流；前端卡片测试覆盖 BUG 严重性标签、REQ 优先级标签和现有九阶段文档入口不回退。

## AC-BUG-0021-06 非目标范围不回退

独立 Change 卡片、文档入口排序、负责人标签、Sprint 标签和任务进度展示不因本次修复发生行为回退。

## AC-BUG-0021-07 分级标签颜色按等级区分

给定 REQ `priority` 与 BUG `severity` 的不同合法值，当用户查看需求中心卡片时，同一类型内不同等级的标签应呈现可区分颜色，并由前端样式测试覆盖。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: fix-requirement-center-bug-card-severity-display
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

