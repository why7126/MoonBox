---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡新增 Sprint 已完成与累计数量
owner: product
created_at: 2026-09-14 14:50:18
updated_at: 2026-09-14 14:50:18
---

# 业务流程

## 总流程

```text
用户进入需求中心
  |
  +-- 前端请求需求中心上下文数据
        |
        +-- 后端聚合 Sprint 事实源
        |     |
        |     +-- 读取 iterations/change/ 下有效 Sprint -> 计入累计
        |     +-- 读取 iterations/archive/ 下有效 Sprint -> 计入累计与已完成
        |     +-- 兼容 completed 未归档状态 -> 按固定口径处理并去重
        |
        +-- 返回 Sprint 数量摘要
              |
              +-- 成功 -> 指标区展示 已完成 / 累计
              +-- 无 Sprint -> 展示 0 / 0
              +-- 失败或解析异常 -> 展示轻量错误态并保留页面可用
```

## 筛选与刷新流程

```text
用户搜索或筛选卡片
  |
  +-- 卡片列表与局部对象统计按筛选变化
  |
  +-- Sprint 数量指标保持项目级总览

用户手动刷新或切换空间
  |
  +-- 重新请求需求中心上下文
  |
  +-- Sprint 数量指标与卡片数据同步刷新
```

## 与父 REQ 差异

| 项 | REQ-0012 基线 | REQ-0030 增强 |
|---|---|---|
| 指标区 | 展示需求中心对象统计 | 新增 Sprint 已完成与累计数量 |
| 统计事实源 | 需求中心阶段与卡片数据 | Sprint 生命周期事实源 |
| 筛选影响 | 看板对象与部分统计可随筛选变化 | Sprint 数量保持项目级总览 |
| 空态异常 | 通用加载、空态、错误态 | 增加 Sprint `0 / 0`、解析失败和刷新失败状态 |

## 数据依赖

- Sprint 目录事实源：`iterations/change/` 与 `iterations/archive/`。
- Sprint 元信息：`sprint.yaml` 或等价 Sprint 文件中的 ID、状态和成员关系。
- 需求中心聚合接口：提供页面上下文、指标摘要和刷新后的最新数据。
- 前端状态：搜索、筛选、当前空间和刷新状态。
- 观测数据：页面加载、手动刷新、空间切换和需求中心请求日志的脱敏摘要。

## 异常分支

- 无 Sprint：展示 `0 / 0`，不隐藏指标卡。
- Sprint 元信息缺失：按可识别目录 ID 保守计入累计，并返回可展示 warning。
- Sprint 状态冲突：后端返回脱敏阻塞或漂移提示，不静默选择任一状态。
- 请求失败：保留最近一次可用值或展示错误态，其他需求中心卡片继续可用。
- 权限不足：展示无权限态，不暴露内部文件路径或原始异常。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - usage_events
  reason: 需求中心上下文请求会返回 Sprint 指标，页面加载、手动刷新和空间切换可能产生行为事件；本需求不新增长耗时、多步骤、异步任务或对象存储链路。
  validation: 后续实现阶段需验证请求日志只记录接口、状态码、耗时和脱敏统计摘要；行为事件只记录页面、刷新或空间切换上下文，不记录原始治理文档或内部路径。
```
