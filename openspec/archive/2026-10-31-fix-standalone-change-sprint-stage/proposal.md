---
title: 独立变更迭代准入分列修复提案
created_at: '2026-10-31 10:12:35'
updated_at: '2026-10-31 10:12:35'
---
# 独立变更迭代准入分列修复提案

## 背景
修复 BUG-0072-standalone-change-ready-dev-without-sprint：未排期proposed独立Change直接进入待开发，动作仅禁用而无规划入口。来源：[缺陷](../../../issues/bugs/review/BUG-0072-standalone-change-ready-dev-without-sprint/bug.md)。
## 变更内容
按无归属、唯一有效归属、冲突/失效派生阶段、提示和主动作；保持执行事实及服务端准入。
## 能力影响
### 修改能力
- web-catalog-requirement-center-real-data：独立变更状态映射与迭代归属动作。
## 影响范围
后端ChangeIndex/需求中心响应、Web卡片及诊断、相关测试和文档；不修改历史归档、真实Sprint数据，不实施归档工具版本路由。
product_data_collection_observability: applicable
 affected_layers: 需求中心API、Web、Agent Workflow
validation: 身份透传、可见性、只读与执行准入；复用已有请求日志及链路，不新增DB或采集表；API字段变化时同步OpenAPI/Orval。
## 回滚方案
撤回本Change代码及兼容字段，保持原先开发阻断；无数据库迁移或历史数据回写。
