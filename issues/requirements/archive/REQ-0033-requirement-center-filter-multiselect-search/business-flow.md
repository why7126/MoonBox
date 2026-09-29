---
requirement_id: REQ-0033-requirement-center-filter-multiselect-search
title: 需求中心筛选下拉框支持复选搜索多选与排序优化
owner: product
source: requirement.md
created_at: 2026-09-14 14:50:41
updated_at: 2026-09-15 08:54:10
---

# 业务流程

## 1. 筛选交互流程

```text
用户进入需求中心
  |
  v
查看工具栏筛选控件
  |
  v
打开某个筛选下拉框
  |
  +--> 输入关键词搜索候选项
  |      |
  |      +--> 有结果：候选列表按匹配与排序规则展示
  |      |
  |      +--> 无结果：展示轻量空态，已选项保持
  |
  v
勾选或取消勾选候选项
  |
  v
触发器摘要更新，默认 Sprint 范围展示默认态文案，页面结果即时刷新
  |
  v
统计、阶段列、卡片、空态与筛选条件保持一致
```

## 2. 条件组合规则

```text
同一维度：OR
  Sprint in [sprint-005, sprint-006]
  Sprint includes [未纳入 Sprint]
  分级 in [requirement:P0, requirement:P1, bug:critical]
  阶段 in [待评审, 验收中]

不同维度：AND
  类型 = Requirement
  AND Sprint in [sprint-005, sprint-006]
  AND 分级 in [requirement:P0, requirement:P1]
  AND 负责人 in [产品团队]
  AND 阶段 in [待评审, 验收中]
```

## 3. 与父需求差异

父需求 REQ-0012 定义需求中心页面、9 阶段看板、卡片信息、基础筛选和刷新体验。本需求只增强筛选下拉控件：

- 不改变看板阶段、卡片结构、阶段主动作或文档入口。
- 不改变真实数据聚合接口和权限事实源。
- 不新增服务端查询协议；实现阶段可继续使用已加载数据做前端筛选。
- 增加多选、下拉内搜索、复选框、全选当前候选项、Sprint 未纳入候选项、默认 Sprint 范围摘要、排序和状态保持的体验要求。

## 4. 异常与降级

```text
候选项为空
  -> 显示空态
  -> 保留筛选控件结构

搜索无结果
  -> 显示当前维度无匹配
  -> 不清空已选项

权限或解析异常
  -> 使用脱敏错误摘要
  -> 不展示隐藏对象名称、数量差异或路径

候选项排序证据不足
  -> 按名称或 ID 稳定排序
  -> 不使用不稳定数组顺序
```

## 5. 数据边界

本需求默认复用需求中心现有上下文数据和前端状态管理。若后续设计将筛选下沉到 API 查询、URL 持久化或个人筛选模板，应在 OpenSpec Change 中补齐 API、请求日志、行为事件和安全验收。
