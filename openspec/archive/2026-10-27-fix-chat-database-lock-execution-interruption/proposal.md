---
title: Chat 数据库锁竞争与执行中断修复提案
created_at: '2026-10-27 08:42:55'
updated_at: '2026-10-27 08:42:55'
---

# Chat 数据库锁竞争与执行中断修复提案

## 背景

[BUG-0068](../../../issues/bugs/review/BUG-0068-chat-database-lock-execution-interruption/bug.md)已评审且纳入sprint-014。需求中心核验在UPDATE之后扫描项目文件，持有写事务导致共享SQLite竞争；现场线程与独立复现已确认零行UPDATE也占锁。Chat历史中断为result_persistence_failed，但06:53具体失败SQL未记录，不追溯伪造。

## 变更内容

- 将文件快照与核验计算移出数据库写事务；短事务重新检查版本与身份后应用最小变更。
- 避免无状态变化的终态核验重复UPDATE，保持并发围栏与核验保护。
- 明确数据库锁错误分类、有界事务恢复及提交结果不明的读回边界，不重放模型或治理命令。
- 补充脱敏事务诊断、SQLite/MySQL并发回归及独立真实样本。

## 能力影响

### 新增能力

无独立新产品能力。

### 修改能力

- governance-command-durable-recovery：追加核验事务时长边界、锁错误处理及并发诊断要求；不扩大可自动恢复的治理动作范围。

## 影响范围

后端governance/reader.py、execution_context.py、execution_guard.py及相关核验写路径；chat持久化错误处理与诊断。鉴权作为共享库竞争回归方，节流仅在保留撤销/过期语义且证据支持时实施。默认无API响应结构、物理表、UI或部署拓扑变更。

## 回滚方案

无数据迁移前提下回退代码版本，保留原执行记录、完成证明和保护状态。回退会重新暴露长事务风险，先限制新增重负载核验并按发布流程处置；不得删除业务记录或通过重启冒充修复。本次不执行部署或回滚。

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow；validation: 根因证据11条通过，产品修复验收待执行。usage_events、对象存储、客户端生成当前N/A：不新增用户动作、上传或API契约。
