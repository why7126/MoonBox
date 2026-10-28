---
bug_id: BUG-0068-chat-database-lock-execution-interruption
title: Chat 执行期间数据库锁竞争导致持久化失败与任务中断
status: done
created_at: '2026-10-27 08:19:57'
updated_at: 2026-10-27 09:20:40
severity: high
environment: docker
owner: 产品团队
source: 用户 bug-capture 授权及同会话只读探索
lifecycle_stage: archive
related_requirement: null
related_bug: BUG-0056-requirement-center-context-load-latency
root_cause_status: confirmed
---

# Chat 执行期间数据库锁竞争导致持久化失败与任务中断

## 现象与影响

执行 BUG-0056-requirement-center-context-load-latency 的 opsx-apply 时，Chat 出现结果待确认、事件读取失败与写操作不可用；多个项目、会话及事件接口出现 504。恢复读取后本轮为 stopped，错误码 result_persistence_failed，业务核验提示缺少正式同步成功证明。原 Change 未完成交付，不能重复发送 apply 或直接解除保护。

严重度初判 high：核心执行被中断，且影响会话与项目读取；尚无数据损坏、永久丢失或安全事故证据。按一个数据库并发故障记录，诊断缺口纳入同一调查，不拆成多个缺陷。

## 判重与关联

已读取 CHANGELOG.md、_registry.yaml 与候选 capture/trace。BUG-0056 关注首屏聚合性能，BUG-0058 关注历史读取请求放大，BUG-0064 关注 unknown 恢复容器重复创建，BUG-0060 关注正式同步后的证明指纹失效。它们与本条有背景关联，但均未覆盖运行中数据库锁竞争导致持久化异常的独立复现与验收。本条关联用户指定的 BUG-0056，不改变原缺陷、Sprint 或 Change 状态，不宣称共同根因已确认。

## 本轮证据摘要

证据复用 2026-10-27 同会话 explore 的浏览器、Docker 日志、只读数据库查询、内核锁与代码核对；本次 capture 不重新触发执行。时间均为 Asia/Shanghai。未保存凭据、原始对话、数据库、原始容器输出或本机路径。

| 编号 | 来源 | 事实与边界 |
|---|---|---|
| E1 | 浏览器与 Web 代理日志 | 原 Chat 提示事件读取失败、项目连接 504；同一时间段事件、会话消息、项目列表均发生 upstream response header timeout。代理目标与实际 backend 地址一致。 |
| E2 | worker 历史日志 | 06:53:01.951 记录 chat_execution_unhandled cause_type=OperationalError phase=running，随后记录 reason_code=result_persistence_failed。没有保存具体失败 SQL 或完整原始异常堆栈。 |
| E3 | 控制器与 backend 历史日志 | 06:53:48 起控制器反复 database is locked；06:56:53 backend 在 resolve_token 查询失败，06:59:52 同函数更新会话时间也报锁错误。同期锁竞争已确认，尚不能精确关联为 E2 的同一笔事务。 |
| E4 | 指定轮次只读查询与治理 journal | 终态 stopped，06:57:53 的终态事件 reconciled=true；journal 为 terminal、sync_incomplete，没有 sync_succeeded=true。仅有 opsx.start 正式写入和 opsx.apply dry-run，不能作为完成证明。 |
| E5 | 内核锁与文件描述符匹配 | 后续取证采样中，业务库 inode 与 backend PID 1（uvicorn）的持锁文件一致，同时存在读写锁；下一次采样锁已消失。只证明采样时持锁来源，不追溯认定 06:53 的持锁进程。 |
| E6 | 部署代码哈希核对 | chat/execution.py、chat/resource_guard.py、repositories/admin_auth.py、governance/reader.py 与本地对应文件哈希一致。OperationalError 被统一归类为 result_persistence_failed；异常日志仅保留类型和阶段。 |
| E7 | 代码路径 | resolve_token 每次鉴权更新 admin_sessions 并提交；ProjectReader._call 逐项核对治理状态后统一提交；它们是竞争或长事务调查候选，未取得持锁线程栈证明直接因果。 |
| E8 | 任务与工具轨迹 | Change 为 in_progress、completed_at=null、13项未勾选；基线测试曾因缺少 app 模块导入失败，调整后重试未见完成结果。没有性能修复已交付的证据。 |

## 根因状态与待补证

root_cause_status: confirmed。已确认需求中心治理核验在写事务中扫描文件，具体现场线程与独立复现见 root-cause.md；历史06:53失败SQL及线程未记录，不能追溯认定。

已尝试浏览器现有页与刷新、限定时间日志、mode=ro 数据查询、容器内核锁和部署代码核对；只读查询也曾被锁阻断。容器没有现成 py-spy/gdb/pstack，未安装工具、注入诊断或发送进程信号。现有日志不含原始堆栈，不能事后伪造。

后续在授权隔离环境或自然复发时，同步采集请求/轮次的脱敏关联标识、事务起止、锁等待时长、失败数据库错误码与项目堆栈、持锁线程和文件编号；比对需求中心加载与 Chat 事件写入并发。返回脱敏表格：时间、服务、操作、事务耗时、错误码、锁持有者、关联证据。不记录 SQL 参数、Cookie、Token 或业务正文。新增诊断代码先走正式 Change，不在 capture 中实现。

## 复现与期望

1. 保留原失败轮次只读，在隔离样本准备 SQLite 环境与相同部署版本。
2. 并发运行授权测试任务、Chat 事件读取及需求中心加载，观察事务与锁等待；当前未完成确定性复现。
3. 期望并发读取不长期阻塞执行记录写入；失败时保留准确原因与可恢复事实，不重复执行命令、不伪造完成。
4. 实际样本执行中断、多个接口超时、没有正式完成证明。

## 建议验收

- SQLite 并发读取、鉴权更新时间和任务事件写入场景不再因非必要长事务导致任务中断；明确并验证锁等待预算。
- 瞬态锁冲突、持续锁冲突分别验证：重试有界，已保存输出与账务不重复，终态和执行保护依据真实事实。
- 覆盖 MySQL 兼容及权限隔离，不以跳过鉴权、强改状态或无限增加超时替代修复。
- 原始异常具备脱敏错误分类、阶段和关联标识，日志自身失败不阻断业务；合成回归与真实运行证据分开报告。

## 产品数据采集与系统影响

product_data_collection_observability: applicable

affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow

validation: 已有运行日志、只读数据、锁采样与部署代码一致性证据；未修复、未运行新回归或并发验收。usage_events 不新增，因为本条不是新增用户行为；对象存储和客户端生成暂为 N/A，本次未改变上传或 API 契约；UI/部署修改必要性留待方案评审。只创建 capture 和 trace、同步注册表及索引，不修改业务代码、数据库、正式规格或部署。
