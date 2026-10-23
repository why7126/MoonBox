---
title: 归档恢复条文冲突与验收进度修复提案
created_at: '2026-10-21 18:31:15'
updated_at: '2026-10-21 18:31:15'
---

# 归档恢复条文冲突与验收进度修复提案

## 背景

来源：[BUG-0062](../../../issues/bugs/review/BUG-0062-archive-requirement-scope-conflict/bug.md)，已批准并纳入sprint-012，L／5人天。REQ-0046原36项验收有效，同模块不同条文后继却被模块级范围阻断，错误传播为0/36与pending，sprint-011预检和同步结论不一致。

## 变更内容

- 按模块与Requirement标题计算冲突，保持连续证明及全部安全门禁。
- 分离有效AC进度与恢复准入，贯通具体诊断。
- Sprint关闭前采用产品、CLI和Workflow Sync共享深层判定。

## 能力影响

### 新增能力

无新能力模块；在现有治理恢复能力中新增条文范围定义、验收进度保真和Sprint预检一致性要求，保留原REQ-0046条文原文，避免修复自身归档重新触发冲突。

### 修改能力

- governance-command-durable-recovery：细化跨链路连续证明的冲突范围，补充真实AC进度与关闭前判定。

## 影响范围

后端archive_recovery、acceptance_evidence、archive_admission，Workflow Sync与Sprint readiness脚本、相关测试和治理文档。按实际响应变更同步API/客户端，UI不增加动作或modal；若展示受影响按原REQ契约验证。不得修改原归档journal或manifest，不直接编辑正式specs。

## 回滚方案

回滚本次实现及兼容字段消费端后恢复保守阻断；保留新增诊断证据和历史归档，不回滚业务数据库或删除恢复记录。回滚不宣称sprint-011可以关闭，不自动重放归档。

## 数据采集与观测

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档准入、验收及诊断投影、Sprint预检、Workflow Sync；reason: 调整恢复判定与跨入口诊断语义；validation: 计划按BUG AC-001—011验证条文冲突、哈希链、真实AC进度、四入口一致性及脱敏。N/A：无新增DB表、对象存储、权限、模型调用或保留周期；现有请求日志与Task Trace关联保持，直接CLI不伪造usage_events，不采集Prompt或凭证。实现保留公开响应字段，内部诊断复用既有进度、原因及Sprint blocker字段；无需OpenAPI/客户端生成。真实部署观察单列验收，不以本地测试替代。
