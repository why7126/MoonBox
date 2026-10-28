---
title: Chat 未知轮次有界恢复交付验证
created_at: 2026-10-26 14:30:01
updated_at: 2026-10-26 14:30:01
---

# Chat 未知轮次有界恢复交付验证

## 实现与影响

恢复预算、调度及续接位于src/backend/app/chat/recovery*.py；platform_worker/local_worker共用独立槽，execution保持权威终态及账务规则。container_server/app_server实现有界读取、受信Docker endpoint和预检复用。schema增量建表，cleanup及backup同步历史删除。配置经settings集中解析、Compose透传，数据库/兼容性/部署/容器说明与事故经验已同步。

影响数据库、后台调度、Docker运行及恢复观测；不新增HTTP API、界面或客户端字段，因此API/UI/客户端生成N/A。权限不扩大，暂停不清除unknown保护。未修改真实环境、未发布镜像、未升级原运行worker。

## 验证记录

- SQLite：142通过、1跳过。跳过原有需CHAT_LIVE_PROBE显式启用的模型调用测试；本BUG真实Docker不调用模型。
- MySQL 8.0.40隔离库：23通过、1跳过。跳过SQLite专属离线备份测试，该用例在SQLite已通过；MySQL历史删除独立验证。
- 实现覆盖：默认6次及时间预算、瞬态/权威终态、重启/并发CAS/旧token、正常领取5秒预算、多unknown独立调度、缓存身份与TTL、安全拒绝、受控续接幂等、观测失败降级、历史清理及备份不复活。
- 证据入口：evidence/sqlite.json、mysql.json，记录实际计数与完整后端/测试输入指纹。真实Docker证据evidence/docker-recovery.json须经当前指纹校验后才能用于验收。
- 文档/治理：OpenSpec validate、当前Change中文与标题、Sprint scope、目录结构、上下文预算、环境ignore、Compose透传及git diff --check通过。目录校验另报告已有legacy SQLite目录提醒；按数据保护要求保留，不属于本次新增残留。

## 问题与修复证据

初次真实Docker因隔离HOME丢失daemon地址而返回unsupported_executor_version；核对实际CLI为0.153.4，连接诊断证明默认socket不存在。仅向控制器Docker子进程传递可信Unix endpoint后通过，不复制个人配置、不把socket挂入执行容器。单元OOM fixture经__new__构造，已补齐新增上下文字段；断言保持。备份测试补齐受保护临时目录。一次正在执行的观察被新增历史清理代码的输入指纹门禁拒绝，未发布为当前证据；稳定后重新采集。

## 产品数据采集声明

product_data_collection_observability: applicable；affected_layers: task_traces、task_trace_spans、恢复元数据；validation: 双库恢复与观测降级测试通过，字段仅保留原因、次数、到期、耗时、缓存与容器计数，可用性缺失不伪造零值。无HTTP或用户交互入口，request_logs与usage_events N/A。恢复运行记录维持业务保护，既有遥测保留策略不变。

## 真实环境边界与收尾

真实Docker使用当前宿主源码、固定执行器镜像、合成认证及独立SQLite/MySQL，不访问真实历史unknown，不调用模型。按AC-08核对该隔离运行版本；不将隔离结果表述成原部署已升级。当前指纹校验通过；两次受控恢复创建6个容器且销毁6个，暂停后330秒新增0个；真实正常关闭、异常、取消、中断及超时回收通过。本次登记资源cleanup与check均clean，容器0、网络0，未删除卷或宿主数据，见evidence/resource-cleanup.json。
