---
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除 - 业务流程
created_at: 2026-09-15 23:11:38
updated_at: 2026-09-15 23:11:38
owner: product
source: requirement.md
---

# 需求中心文档抽屉简化与 Change 属性模块移除 - 业务流程

## 当前阅读流程

```text
用户进入需求中心
  |
  v
选择 REQ / BUG / 独立 Change 卡片文档
  |
  v
打开右侧文档抽屉
  |
  v
查看文档属性
  |
  v
阅读正文
```

## Change 追溯入口流程

```text
用户需要核对关联 Change
  |
  v
回到抽屉外的卡片、详情或既有文档分组入口
  |
  v
选择目标 Change
  |
  v
打开对应 Change 文档
  |
  v
阅读该 Change 的 proposal / design / tasks / trace
```

## 与父需求 REQ-0026 的差异

REQ-0026 建立了 Change 可见性、关联追溯和独立 Change 卡片能力；REQ-0036 不改变这些底层事实和入口能力，只调整文档抽屉的信息架构。

| 项目 | REQ-0026 | REQ-0036 |
|---|---|---|
| 核心目标 | 让 Change 可见并可追溯 | 简化文档抽屉阅读体验 |
| Change 数据 | 新增聚合与展示 | 保留，不删除 |
| 文档抽屉 | 曾承载 Change 追溯属性 | 删除整个 Change 属性模块 |
| 多 Change | 保留关联数据与追溯 | 抽屉外入口仍需可达 |
| 阶段与任务进度 | 可在 Change 相关区域展示 | 不在文档抽屉顶部展示 |

## 状态矩阵

| 场景 | 抽屉展示 | 追溯入口 | 风险控制 |
|---|---|---|---|
| REQ 无关联 Change | 文档属性 + 正文 | 无需 Change 入口 | 不显示空模块 |
| REQ 关联单 Change | 文档属性 + 正文 | 抽屉外可达该 Change 文档 | 不把追溯模块塞回抽屉 |
| REQ 关联多 Change | 文档属性 + 正文 | 抽屉外逐个可达 | 不默认首项，不串读 |
| BUG 关联 Change | 文档属性 + 正文 | 抽屉外可达 | 权限不放宽 |
| 独立 Change | 文档属性 + 正文 | 自身文档入口继续可用 | 进度和告警不在抽屉模块展示 |

## 数据与权限边界

- 文档读取继续使用现有项目、空间成员、对象授权和文档 URL 约束。
- 本需求不新增 API、DB、请求封装、行为事件、Task Trace 或对象存储路径。
- 若后续实现发现必须扩展接口字段或埋点，应在 OpenSpec Change 中重新评估观测声明。
