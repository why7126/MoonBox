---
title: 独立 Change 优先级维护与展示提案
created_at: '2026-10-31 21:27:39'
updated_at: '2026-10-31 21:27:39'
---

# 独立 Change 优先级维护与展示提案

## 背景
REQ-0057-standalone-change-priority 已评审并纳入 sprint-018。独立 Change 卡片目前 priority 为空，用户无法判断交付优先级。

## 变更内容
为无来源 Issue 的活动 Change 增加 P0/P1/P2/P3 分级维护、卡片标签及筛选，区分负责人。采用 trace.priority，授权保存、版本冲突保护、必要审计与缺失/非法值兼容。关联 Issue 不覆盖，归档只读，不批量回填。

## 能力影响
### 新增能力
- standalone-change-priority：独立 Change 分级事实源、维护、展示与验收。
### 修改能力
无；扩展独立对象能力，保留既有 Issue 分级和卡片身份规范。

## 影响范围
backend、web、api 与治理规则；复用 REQ-0056 已交付卡片。同步 OpenAPI、客户端、API 文档及测试。优先采用文件事实源，不新增业务表；若实施发现持久操作设施需 schema 变化，先补设计和 SQLite/MySQL 迁移验证。管理后台、对象存储及部署拓扑不变。估算5人天。
