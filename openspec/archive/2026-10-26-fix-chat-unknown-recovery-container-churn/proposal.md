---
title: Chat 未知轮次有界恢复修复提案
---

# Chat 未知轮次有界恢复修复提案

## 背景

[BUG-0064-chat-unknown-recovery-container-churn](../../../issues/bugs/review/BUG-0064-chat-unknown-recovery-container-churn/bug.md) 已评审并纳入 sprint-014。已确认空闲 worker 对长期 unknown 无界恢复，反复创建预检与状态读取容器；自动销毁有效但无法停止下一次创建。原始历史执行异常及单次读取失败分支仍未确认。

## 变更内容

持久化每轮次的尝试预算、退避时间、恢复租约和独立暂停状态；正常任务优先，恢复并发有界。无变化检查和安全预检复用减少启动成本，补充脱敏恢复观测及受控运维续接入口。保持业务 unknown、写入与账务保护，不重放业务命令。

## 能力影响

### 新增能力

无新增独立能力。

### 修改能力

- `codex-session-execution`：补充未知轮次有界恢复、独占领取、暂停续接、安全预检复用与恢复观测要求。

## 影响范围

涉及后端 chat/platform_worker.py、execution.py、container_server.py、app_server.py 及模型、迁移、测试；新增恢复元数据兼容 SQLite/MySQL，更新数据库设计、兼容记录与部署运维文档。初版通过受控运维命令续接，不增加 HTTP API 或 UI，因此无客户端生成变化；不改变沙箱权限边界。预计沿用 Sprint 的5人天，不新增外部服务。

## 回滚方案

采用增量 schema，保留原始轮次和恢复记录。异常时禁用自动恢复并保留正常任务调度，修复后受控续接；不可直接回退到会无限扫描 unknown 的旧 worker。必须回退旧镜像时先停止其恢复执行路径并验证隔离，否则阻止回退。生产变更另按发布授权执行。

