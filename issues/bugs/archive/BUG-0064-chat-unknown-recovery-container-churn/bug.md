---
bug_id: BUG-0064-chat-unknown-recovery-container-churn
status: done
created_at: '2026-10-26 13:09:09'
updated_at: 2026-10-30 08:33:53
severity: high
environment: docker
owner: 产品团队
source: 用户bug-capture授权及2026-10-26同会话只读探索
lifecycle_stage: archive
related_requirement: null
related_bug:
- BUG-0026-chat-platform-opsx-archive-source-permission
- BUG-0052-verified-result-execution-guard-not-released
- BUG-0058-chat-history-status-replay-request-amplification
title: Chat 未知轮次无界恢复导致执行容器持续重复创建
discovered_at: '2026-10-26'
related_change: fix-chat-unknown-recovery-container-churn
root_cause_status: confirmed
root_cause_scope: 恢复无界调度导致重复创建；不含原执行进入unknown的历史原因
---

# Chat 未知轮次无界恢复导致执行容器持续重复创建

## 缺陷摘要

Chat worker在没有新任务时，对长期unknown轮次反复创建moonbox-chat-session容器；容器虽然自动销毁，恢复检查仍无限重复。已确认的缺陷是恢复调度缺少单轮次退避、重试预算及暂停条件，未确认原业务任务被重复执行。

用户描述的“任务结束”指已无正常新任务执行；目标历史轮次在数据库仍为unknown，不能表述为权威completed后继续执行业务。

## 环境与前置条件

- 本地Docker部署，moonbox-chat-worker与moonbox-chat-executor:0.153.4-test；工作区为source模式。
- 2026-10-26同会话取证：无queued/running/connecting/stopping，存在1条自10月12日起未更新的unknown，仍绑定active_turn及executor thread/turn。
- 部署代码与本地源码全文指纹不一致；恢复扫描、reconcile_unknown和容器工厂关键逻辑已逐段核对一致。本次生成复用已有证据，没有重新创建样本或修改数据库。

## 现象与影响范围

多个执行容器短时间内连续创建并销毁，反复进行沙箱预检与状态读取；容器AutoRemove=true，属于创建频繁而非单实例清理失效。已观察样本仅覆盖当前部署的一条旧轮次，不外推其他环境。

影响后台Docker启动成本、恢复检查负担与状态可解释性。恢复在空闲循环串行执行，存在延迟正常任务领取的风险，但尚无调度延迟或CPU/内存定量测量。没有数据损坏、重复业务副作用或全站不可用证据。

## 复现步骤

1. 只读定位具有有效工作区、executor thread/turn且仍为会话active_turn的unknown轮次；隔离复现时准备持续无权威终态的外部执行记录。
2. 保证无正常排队或运行轮次、无会话删除队列；不要重发原业务命令。
3. 观察worker空闲循环中同一工作区的容器创建与销毁事件，核对预检容器及状态读取容器是否反复出现。
4. 比对数据库更新时间、外部session事件及运行版本恢复路径，检查是否存在next_retry_at、attempt_count、暂停状态。
5. 保存脱敏关联、时间和计数。真实环境只读；后续隔离复现创建容器前遵守临时Docker生命周期契约。

## 期望与实际

| 维度 | 期望 | 实际 |
|---|---|---|
| 恢复调度 | 单轮次有退避和持久化预算 | 每次worker空闲循环重新处理unknown |
| 无终态或错误 | 分类记录，有限重试后暂停待处理 | 返回False，保持unknown，下一循环再创建 |
| 资源成本 | 无新证据时避免高频重复预检与创建 | 每次恢复重复创建沙箱检查和读取执行器 |
| 状态真实性 | 恢复暂停与业务终态独立 | 缺少恢复暂停表达；不能直接改业务终态止血 |
| 重启与并发 | 预算可续接，各轮次公平调度 | 当前未见持久化恢复调度字段，需正式回归覆盖 |

## 严重等级说明

severity为high：已观察持续后台资源消耗与长期不收敛，影响运行稳定性且存在调度干扰风险。未确认服务中断，故不提升为critical或blocker；资源成本收益须实测，不估造下降比例。

## 证据链


证据来自同会话上一轮只读 /explore，本次capture复用，不冒称重新复现。未保存原始数据库、对话正文、凭据、本机路径或原始容器inspect。

| 编号 | 类型与来源 | 事实及确认边界 |
|---|---|---|
| E1 | runtime_log，Docker容器create/destroy事件 | 多个moonbox-chat-session实例短时间内连续创建、随后销毁，采样AutoRemove=true；确认重复创建而非持续堆积。Docker事件窗口有界，不外推为从10月12日起每秒都运行。 |
| E2 | data_sample，运行worker所挂载canonical SQLite的只读查询 | completed=62、failed=9、stopped=11、unknown=1；无排队或运行态轮次。唯一unknown仍为会话active_turn，未归档未删除；error_code=execution_access_or_workspace_error。创建时间2026-10-12 08:43:50，更新时间08:46:32，心跳08:46:31，均为Asia/Shanghai。 |
| E3 | code_path，部署worker代码与本地对应函数逐段核对 | platform_worker.main在空闲循环扫描所有unknown并调用reconcile_unknown，未设置单轮次next_retry_at、退避或尝试上限。部署文件与本地全文指纹不同，关键恢复逻辑逐段一致，未把本地整体版本视为部署版本。 |
| E4 | code_path，execution.reconcile_unknown | 身份前置校验后创建server，调用read_turn；无法映射completed/failed/interrupted则返回False；ChatError/ExecutorError/WorkspaceError同样返回False，finally关闭server。无本次恢复失败分类和调度持久化。 |
| E5 | code_path，container_server.persistent_container_server | 每次先创建独立容器执行沙箱/工具链预检，随后创建实际app-server用于状态读取；相同旧轮次恢复会重复承担该成本。 |
| E6 | runtime_log + config_diff，容器挂载与会话绑定哈希比对 | 两个采样容器工作区哈希均为499e0c5d85，与唯一unknown会话source模式配置工作区一致；匹配执行session文件存在。会话和轮次原始ID未转存。 |
| E7 | data_sample，匹配执行session的生命周期元数据 | 目标轮次有2026-10-12 08:44:58.894开始事件及item_completed事件，无task_complete/abort等轮次终态；最后记录为08:46:24.233的token_usage_record。session cwd为/work。工具完成事件不能当作轮次完成。 |
| E8 | data_sample，chat_cleanup_jobs聚合 | 队列为空，排除该采样时段删除会话维护队列作为创建来源。 |

代码定位：`src/backend/app/chat/platform_worker.py:main`、`src/backend/app/chat/execution.py:reconcile_unknown`、`src/backend/app/chat/container_server.py:persistent_container_server`、`src/backend/app/chat/app_server.py:read_turn`。运行时同名函数已只读核对。

## 根因结论与证据边界

**confirmed，仅针对本BUG重复创建机制。** platform_worker.main在空闲循环反复扫描unknown；reconcile_unknown通过前置身份校验后创建server，读取无可映射终态或遇到受捕获异常便返回False；未持久化重试调度状态，finally关闭容器后下一轮继续。容器工厂每次执行预检并创建读取执行器，放大重复检查成本。E1—E8提供运行事件、唯一候选轮次、工作区关联与部署代码证据。

**原执行异常仍unknown。** execution_access_or_workspace_error不足以确认具体历史故障。原session缺少终态，但本轮未截获每次thread/read响应，所以无法确认每次返回False的具体分支。这个缺口不改变“任何恢复失败均缺少有界调度”的确认结论；不据此改变原轮次状态。

本次不重复运行会改变产品状态的恢复调用；也不伪造浏览器复现。现有证据足以描述本BUG，原始历史异常与单次RPC错误作为后续细化观测项，不冒充已确认原因。

## 修复范围与分步建议

1. 首先建立单轮次持久化恢复调度：尝试次数、下次时间、最近结果分类、独立恢复状态；退避与次数/累计时间预算到限后暂停。具体默认值在方案评审确定，禁止无上限配置或重启重置预算。
2. 保留unknown业务事实、账务与写入保护；恢复暂停不等于completed/failed/stopped。人工恢复或新证据触发需要明确授权和并发控制，不能直接清除active_turn掩盖异常。
3. 再优化检查成本：无新执行记录或配置变化时减少昂贵读取；预检结果按镜像、沙箱策略、工作区身份和有效期复用，身份变化失效，安全失败不得缓存为通过。
4. 补后台恢复Task Trace及脱敏指标，记录触发原因、尝试/结果、等待时间和容器数量；将暂时错误、缺失记录、无终态、身份异常分类。多个unknown公平调度，不阻塞正常任务。

不包含历史临时容器清理、全局Docker回收、原业务命令重放、业务完成证明放宽或无证据修正历史终态。已归档add-temporary-docker-lifecycle只处理验证资源治理，不能替代本修复。

## 建议验收标准

以下为本次修复验收目标；实现与隔离验证结果见acceptance.md及关联Change交付验证。

| 编号 | 场景 | 通过条件 |
|---|---|---|
| AC-01 | 永久缺少外部轮次终态 | 到达配置预算后恢复暂停；至少跨越一个最大退避周期观察，无该轮次新增恢复容器，业务仍unknown |
| AC-02 | 瞬态读取故障 | 按退避而非每循环重试；权威终态到达后正确收敛，记录真实原因与次数 |
| AC-03 | worker重启与中断 | 次数、下次时间和暂停状态保留，不重置预算或形成容器启动风暴 |
| AC-04 | 多条unknown与正常新任务 | 独立预算、无重复并发恢复；旧轮次不饿死新任务，不重放原业务命令 |
| AC-05 | 预检复用边界 | 有效结果可复用；镜像、策略、工作区身份改变或到期后重新验证；安全失败拒绝执行 |
| AC-06 | 状态与权限保护 | 恢复暂停不伪造终态、不绕过并发/写入/账务保护；获授权的恢复可继续 |
| AC-07 | 观测与隐私 | 每次恢复有原因和结果分类，可关联容器计数；不记录凭据、提示词、原文或真实本机路径 |
| AC-08 | 资源收尾与部署验证 | 真实Docker实例最终回收，共享服务不受影响；合成测试与真实运行证据分别记录，部署验证核对实际版本 |

## 后续补证方法

原始异常补证已尝试canonical数据库只读查询、匹配session生命周期和运行代码比对；历史仅保留笼统错误码，无权威终态。后续如需细化，优先从已授权历史日志读取同时间段脱敏错误类型；若历史缺失，标注不可恢复，不要求重放业务命令。

实现恢复观测后，在隔离样本分别模拟RPC拒绝、缺失轮次、无终态与临时错误，返回时间、错误类别、尝试数、下次时间、容器计数和业务状态；不采集消息正文或认证字段。新增人工恢复接口的权限与状态语义需在设计中明确。

## 系统边界与数据采集

product_data_collection_observability: applicable。
affected_layers: task_traces、task_trace_spans。
validation: 本次仅复用E1—E8证据并完成文档校验；修复后的调度、数据库兼容、观测与真实Docker验收待实施。

后台扫描无HTTP/用户交互来源时，usage_events与request_logs为N/A；如新增人工恢复API，则需补请求日志、权限、API文档和客户端生成。持久化元数据须覆盖SQLite/MySQL，展示与API变化待方案评审，不能默认扩展。本命令不修改业务代码、数据库、正式部署、安全配置或客户端。

## 关联与下一步

关联背景缺陷及非重复理由见[capture.md](capture.md)；状态以[trace.md](trace.md)为准。缺陷文档包已补齐，根因确认仅限重复创建机制；已纳入sprint-014，已创建fix-chat-unknown-recovery-container-churn，修复实现及隔离验收已完成，原运行部署未升级。

下一步：`/opsx-archive BUG-0064-chat-unknown-recovery-container-churn`。
