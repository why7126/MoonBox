---
title: 迭代归档对象会话与命令预填提案
change_id: add-sprint-archive-chat-entry
requirement_id: REQ-0049-sprint-archive-chat-entry
created_at: '2026-10-21 18:30:10'
updated_at: '2026-10-21 18:30:10'
---

# 迭代归档对象会话与命令预填提案

## 背景

当前迭代归档入口把验收签署与进入会话的条件耦合，且确认后仅提示手动执行。REQ-0049 已评审并纳入 sprint-012，要求完整范围全部完成后直接进入 SPRINT 对象会话并预填归档命令。

## 变更内容

- 将入口资格与最终归档门禁分离；非空完整范围全部完成可进入，容量未知或签署未完成不单独阻止准备会话。
- 扩展对象身份、会话准备与执行准入以支持 SPRINT；复用可用会话，没有则创建关联。
- 直接跳转 Chat，精确预填但不发送；保留已有草稿与执行保护，防止跨项目污染和重复提交。
- 用户发送后重新校验范围、权限与最终签署/同步条件，按真实归档结果刷新。

## 能力影响

### 新增能力

无独立能力域；在既有需求中心与 Chat 规格内扩展。

### 修改能力

- `web-catalog-requirement-center`：修改“当前迭代归档入口”，由容量及确认弹窗改为范围完成与直接 Chat 准备。
- `web-catalog-chat-workbench`：修改“会话历史与关联”，增加 SPRINT 身份；新增 Sprint 归档命令准备与执行分层要求。

## 影响范围

backend 的 requirement_center、chat relations、governance preparation、执行准入/命令路由；web 的 RequirementCenterPage、ChatWorkbenchPage、Composer 与治理会话决策；相应 OpenAPI/生成客户端、API 索引和测试。复用关联模型，若实现检查发现枚举或数据库约束变化则补充双数据库迁移验证。管理端、对象存储与部署拓扑不扩展。

本次仅生成设计、规格、任务与追溯，不修改业务代码。Sprint 估算保持5人天，总容量26/30人天，缓冲4人天，超出既定适配范围时重估。
