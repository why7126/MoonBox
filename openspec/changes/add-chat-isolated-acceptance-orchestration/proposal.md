---
title: Chat 隔离验收与原操作续接变更提案
created_at: 2026-10-29 17:11:36
updated_at: 2026-10-29 17:11:36
---

# Chat 隔离验收与原操作续接变更提案

## 背景

REQ-0048 已评审并纳入 sprint-016。sprint-015 已交付固定候选隔离供应，但尚不能代表用户在原 Chat 内自动准备环境、以短期身份验收并安全续接的完整体验。本 Change 承接剩余范围，保留已归档依赖证据与需求 partial 状态，直到完整 20 项 AC 取得当前有效证据。

## 变更内容

- 将可信项目绑定、授权代码快照和验收计划关联到稳定原操作，复用验证任务及候选供应底座。
- 增加面向 Chat 的持久环境编排、短期角色身份、逐 AC 调度、输入变化失效及证据回传。
- 对刷新、重启、重复回调、停止、撤权及迟到 worker 实施幂等与执行围栏；保留原轮次终态，最多一次自动关联续接。
- 在现有 Chat 详情展示准备、局部阻塞、恢复和清理状态，成族实现核验、继续、停止及清理动作。
- 按已批准资源预算、双库和架构矩阵验证完整生命周期；不自动部署生产或扩大归档授权。

## 能力影响

### 新增能力

- `chat-isolated-acceptance-orchestration`：原 Chat 的自主隔离验收、短期身份、持久调度与安全续接。

### 修改能力

无现有规格需求被替换。复用 `isolated-candidate-validation`、`project-verification-environment`、`governance-command-durable-recovery` 的既有边界；新增 Chat 编排契约单独定义，预配置目标与固定候选调用仍可独立工作。

## 影响范围

后端 `src/backend/app/verification/`、`app/chat/` 与既有工作区执行适配；Web `src/web/src/components/chat/` 及 ChatWorkbenchPage；API/OpenAPI/Orval、SQLite/MySQL schema 与迁移、部署批准模板、权限/网络/观测及对应文档测试。管理后台、小程序、移动端不新增入口；对象存储复用证据鉴权和保留策略，不新增公开访问。

依赖归档：`openspec/archive/2026-10-29-add-isolated-candidate-validation/`。本次命令仅生成方案与任务，不修改业务代码、正式规格或已归档结果。
