---
title: 临时 Docker 验证资源生命周期
created_at: 2026-10-26 12:06:37
updated_at: 2026-10-26 12:06:37
---

# 临时 Docker 验证资源生命周期

## ADDED Requirements
### Requirement: 创建前登记与明确资源归属
Agent MUST 在临时 Docker 验证资源创建前登记 Change、用途、随机运行标识、daemon 和有限期限，并为容器和专属网络设置匹配标签。
#### Scenario: 创建临时环境
- **WHEN** 任务需要临时 Docker 验证环境
- **THEN** 先登记再创建，禁止使用共享 Compose 项目或匿名卷作为临时可回收资源
### Requirement: 任务结束清理与完成门禁
Agent MUST 在停止创建资源并保存必要证据后清理本次登记容器和网络，复查零残留才报告清理完成。
#### Scenario: 清理失败
- **WHEN** daemon 不可达、标签不符、存在卷或网络仍被连接
- **THEN** 返回失败与残留信息，不触碰共享资源或虚报完成
### Requirement: 到期扫描和保守回收
Agent MUST 在后续治理入口扫描到期登记资源，回收前预览；到期仍运行的容器需要核查，不自动终止。
#### Scenario: 中断留下到期停止容器
- **WHEN** 已登记 run 过期且容器已停止、网络无外部连接
- **THEN** 显式执行回收后验证零残留，重复回收保持幂等
#### Scenario: 到期容器仍运行
- **WHEN** 到期 run 中存在运行中的容器
- **THEN** 标记待核查并继续检查其他 run，保留运行容器
