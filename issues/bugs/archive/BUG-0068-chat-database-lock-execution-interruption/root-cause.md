---
bug_id: BUG-0068-chat-database-lock-execution-interruption
title: Chat 执行中断与数据库锁竞争根因分析
created_at: '2026-10-27 08:25:20'
updated_at: '2026-10-27 08:33:41'
status: confirmed
---

# Chat 执行中断与数据库锁竞争根因分析

## 根因状态

status: confirmed

## 现象

BUG-0056 的 apply 在运行中发生数据库操作异常，随后进入 unknown，恢复核对为 stopped；没有正式完成同步。同期 Chat 与项目读取出现 504。后续多次采样 backend 持有业务库锁，读取也被阻塞。

## 证据链


证据复用 2026-10-27 同会话 explore 的浏览器、Docker 日志、只读数据库查询、内核锁与代码核对；本次生成复用该证据，不重新触发原执行。时间均为 Asia/Shanghai。未保存凭据、原始对话、数据库、原始容器输出或本机路径。

| id | type | source | 摘要与确认边界 |
|---|---|---|---|
| E1 | network_request | 浏览器与 Web 代理日志 | 原 Chat 提示事件读取失败、项目连接 504；同一时间段事件、会话消息、项目列表均发生 upstream response header timeout。代理目标与实际 backend 地址一致。 |
| E2 | runtime_log | worker 历史日志 | 06:53:01.951 记录 chat_execution_unhandled cause_type=OperationalError phase=running，随后记录 reason_code=result_persistence_failed。没有保存具体失败 SQL 或完整原始异常堆栈。 |
| E3 | runtime_log | 控制器与 backend 历史日志 | 06:53:48 起控制器反复 database is locked；06:56:53 backend 在 resolve_token 查询失败，06:59:52 同函数更新会话时间也报锁错误。同期锁竞争已确认，尚不能精确关联为 E2 的同一笔事务。 |
| E4 | data_sample | 指定轮次只读查询与治理 journal | 终态 stopped，06:57:53 的终态事件 reconciled=true；journal 为 terminal、sync_incomplete，没有 sync_succeeded=true。仅有 opsx.start 正式写入和 opsx.apply dry-run，不能作为完成证明。 |
| E5 | runtime_log | 内核锁与文件描述符匹配 | 后续取证采样中，业务库 inode 与 backend PID 1（uvicorn）的持锁文件一致，同时存在读写锁；下一次采样锁已消失。只证明采样时持锁来源，不追溯认定 06:53 的持锁进程。 |
| E6 | config_diff | 部署代码哈希核对 | chat/execution.py、chat/resource_guard.py、repositories/admin_auth.py、governance/reader.py 与本地对应文件哈希一致。OperationalError 被统一归类为 result_persistence_failed；异常日志仅保留类型和阶段。 |
| E7 | code_path | 代码路径 | resolve_token 每次鉴权更新 admin_sessions 并提交；ProjectReader._call 逐项核对治理状态后统一提交；早期为调查候选；后续 E13—E15 已定位需求中心核验事务，鉴权仍仅作为竞争方。 |
| E8 | data_sample | 任务与工具轨迹 | Change 为 in_progress、completed_at=null、13项未勾选；基线测试曾因缺少 app 模块导入失败，调整后重试未见完成结果。没有性能修复已交付的证据。 |
| E13 | runtime_log | 2026-10-27 08:29 非阻塞线程采样与内核锁 | 08:29:03.329 backend PID1 在业务库 inode1593 持 WRITE 字节1073741825与 READ 区间1073741826..1073742335；线程11843位于 snapshot.walk → read_once → stable → execution_context.reconcile:176 → reader._call:123 → get_requirement_center_context:78。08:29:11/12 线程11890采到同路径和锁；08:29:19/20线程11843再次采到。采样间隙曾无锁，不认定为一笔连续事务。 |
| E14 | config_diff | 部署文件 SHA-256 与本地核对 | execution_context.py=75cdc05298167c89ee3d71f714b34f1580469dad820cc6e67232f8593e840a08；execution_guard.py=c71818e7e776027ef29d6e79ced5ed43e0763d9a167a0272ee622886139dd087；reader.py=75cb1c98ddf03fe542c1673c75c64868eacdae088179f365746ebb0bf8b90f88。三者部署/本地一致。 |
| E15 | test_result | 容器内独立临时 SQLite，调用部署的 terminal() | 仅创建临时库和合成 guard（needs_review/stopped）；A 调用 terminal 得 rowcount=0且不提交，B 更新独立表，timeout=0.2秒，实测0.237秒后 database is locked，code=5 / SQLITE_BUSY；A rollback 后B立即成功。未访问业务库，临时库已删除。 |


补充 E9—E12 详见 [缺陷主文档](bug.md) 的生成阶段自主补证：08:21:43 再次锁采样，mode=ro 查询因锁失败；08:19:30 鉴权更新时间报锁错误；浏览器重连后读出167条事件与 stopped，证明读取可恢复，不等于原执行恢复。

## 已排除假设

| 假设 | 排除证据及范围 |
|---|---|
| 代理指向旧后端地址 | 取证时代理目标与实际后端地址匹配，仅排除该采样时地址漂移。 |
| 任务已经完成，仅前端显示滞后 | 轮次 stopped、无最终回答、journal sync_incomplete、Change 完成时间为空且13项未完成。 |
| 正式完成同步已成功，只是证明丢失 | 记录仅有 opsx.start 写入和 opsx.apply dry-run，不能形成正式完成证明。 |
| 暂无事件等于历史输出被删除 | 重连后167条事件可读；读取失败期间的空态不是数据删除证据。 |
| 测试导入失败本身证明持久化中断原因 | 它是另一条工具错误；worker持久化异常为OperationalError，不能混为同一根因。 |

## 已确认根因与未确认边界

已确认的缺陷机制：需求中心 `ProjectReader._call` 调用 `execution_context.reconcile`，后者先调用 `execution_guard.terminal` 发出 UPDATE，再调用 `stable(project.root)` 扫描文件。Session 在后续逐卡核验结束后才于 reader.py:163 提交。因此数据库写事务覆盖了文件扫描与解析等耗时工作，其他连接写入会被阻塞。对已经 needs_review/stopped 的记录，terminal 的条件 UPDATE 即使匹配零行也会开启写事务；重复读取仍能重复触发竞争。

现场业务库锁归属 backend PID 1，08:29:03 的 AnyIO 线程 11843、08:29:11 的线程 11890 均采到上述 reconcile → stable 栈；不是把等待写入的鉴权线程误判为持锁来源。线程采样与内核锁不是原子快照，不能据此测出完整事务时长或断言排他锁全程连续存在；结合一致部署代码与真实函数的独立数据库实验，确认这条持锁事务路径存在。

历史边界：06:53 的 worker 原始 OperationalError 仅记录类型，没有失败 SQL、完整栈和当时线程信息；不能把08:29线程身份追溯为06:53的线程。历史中断与同期锁竞争高度一致，但未证明其具体失败事务。confirmed 指本次现场捕获并独立复现的长写事务机制，不表示历史每个细节已恢复，也不表示问题已修复。OperationalError 的统一分类仍无法区分不同数据库操作错误。

## 修复方向

针对已确认的持锁调用链缩短事务边界，避免在持有写事务期间扫描/解析大量文件或执行外部操作；评估鉴权更新时间合并或节流，保留撤销与权限正确性。对可安全重试且尚未提交的锁冲突采用有界恢复，账务、事件与执行身份保持幂等；提交结果不明时不盲重试。是否采用数据库日志模式调整或MySQL部署属于后续方案比较，当前不更改。

## 验证闭环

真实运行证据覆盖持锁进程、线程函数栈和部署版本；独立临时数据库实验确认实际 terminal() 的零行 UPDATE 阻塞另一连接，持锁 Session 回滚后解除。该实验是机制复现，不是业务修复验收；完整并发与修复回归仍待执行，见 acceptance.md。

## 补证方式与历史限制

用户授权准备诊断工具后，在现有 backend 容器临时目录安装 py-spy 0.4.2，以 `dump --pid 1 --nonblocking` 获取自然请求的线程栈，不采集局部变量、不发起 apply、不重启服务。非阻塞采样偶有 Bad address，失败样本不作证据。成功栈与 `/proc/locks`、业务库文件编号对照；日志与证据只保留函数名、线程号和时间，无正文或 SQL 参数。

没有持续事务跟踪与历史完整堆栈，无法补出原轮次失败 SQL、原线程或事务起止时间。当前通过现场样本与独立验证完成缺陷机制确认；后续修复增加脱敏事务/请求关联和原始错误细分码，禁止编造历史字段。

## 产品数据采集声明

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow。validation: 证据核对完成，修复验证未执行。usage_events、对象存储、客户端生成本阶段N/A：不新增用户动作、上传或API契约。

## 完善阶段追加补证

2026-10-27 08:25:52，再次匹配 backend 的业务库文件编号与PID 1 fd 23：持有读写锁。只读查询数据库日志模式仍返回 database is locked，未取得模式值，不能猜测运行模式。浏览器原轨迹展开原因明确显示 result_persistence_failed，提示已保存内容保留、末尾可能不完整；显示167条事件及停止终态。该轮尚未取得线程栈，曾保持 probable；后续补证见下表。

## 持锁线程与事务补证

复核 E15：创建独立 SQLite 引擎及 execution_guards 表，插入 needs_review/stopped guard 并提交；创建另一测试表；Session A 调用 `terminal(A, 'test', 'stopped')` 保持事务；连接 B 更新测试表观察超时；A.rollback 后重复 B 更新确认成功。测试需使用临时目录，禁止对业务库运行。

## 评审准入与同步边界

前一轮 probable 时未执行成功态 bug.complete，保持 enriching。现在已取得现场线程栈、部署一致性与独立机制复现，根因状态更新 confirmed；完成根因与标题门禁后运行 bug.complete。历史信息缺失继续保留，不以状态推进代替修复验收。既有 workflow_sync 未内置根因门禁的差异只作为规范建议，不在本BUG中改脚本或创建额外Change。

诊断工具与临时库已清理；未创建新容器，登记资源扫描结果全部clean。
