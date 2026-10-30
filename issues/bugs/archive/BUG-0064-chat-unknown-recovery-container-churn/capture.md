---
bug_id: BUG-0064-chat-unknown-recovery-container-churn
status: done
created_at: '2026-10-26 13:07:04'
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
---

# Chat 未知轮次无界恢复导致执行容器持续重复创建

## 现象与影响

用户观察到任务结束后 moonbox-chat-session 容器仍不断创建。2026-10-26 同会话只读排查时没有 queued/running/connecting/stopping 轮次，仅有1条长期 unknown；执行器持续创建并销毁，不是同一容器一直存活，也没有证据表明原业务任务被重复执行。

严重度初判 high：无人执行新任务时仍持续消耗容器启动、沙箱校验和状态读取资源，恢复轮次不能收敛，且恢复在worker空闲循环中串行执行，存在延迟新任务领取的风险；未量化CPU/内存或实际调度延迟，不宣称已发生全站不可用或数据损坏。

## 判重与单条范围

读取 bugs/CHANGELOG.md 与 _registry.yaml，并核对候选 capture：BUG-0026针对归档权限与setup失败；BUG-0052针对业务完成证明与保护解除；BUG-0058针对前端历史状态重复读取。候选只作背景关联，尚无本次原轮次与旧BUG的确定因果关系。本BUG修复后台unknown恢复调度、重试预算与检查成本，复现和验收可在同一链路闭环，保持单条。

已归档 add-temporary-docker-lifecycle 治理临时验证资源登记与结束清理，不改变产品Chat恢复机制，不能替代本BUG。历史临时容器清理已另行完成，不纳入此次修复。

## 本轮脱敏证据

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

## 根因判断与未决项

重复创建机制 confirmed：旧unknown保持活动身份，空闲worker反复调度恢复，恢复创建预检和状态读取容器，没有有效重试收敛；容器关闭后下一轮继续。

原执行为何进入unknown仍 unknown：错误码只表明访问或工作区类异常，无法区分具体历史故障。本轮未截获每次thread/read响应或异常代码，因此单次未恢复究竟是缺终态、RPC拒绝或其他读取错误仍待补证。原记录缺终态支持恢复证据不足，不能直接断言原任务已成功或已失败。

## 复现与补证步骤

1. 在授权隔离样本中保留具有active_turn、executor thread/turn身份、有效工作区的unknown轮次，使外部轮次持续无权威终态；真实历史样本只读检查，不修改状态取证。
2. 确认没有新任务和会话删除任务，观察worker空闲期间相同工作区执行容器的创建、预检和销毁。
3. 对照运行版本恢复循环、数据库更新时间与外部session终态；记录尝试原因、错误分类和下次重试时间是否存在。
4. 后续补证只采集脱敏错误码、时间、工作区/轮次哈希和结果分类，不输出prompt、auth或完整日志。不要再次执行原业务命令来证明恢复。

## 期望与实际

期望：恢复检查有预算、有等待间隔、有结束或暂停条件；无新证据不持续创建高成本执行器；不能凭时间推断原业务终态。
实际：旧轮次保持unknown，恢复失败或无终态后下一空闲循环再次创建容器；清理当前容器不能阻止重建。

## 分步修复建议

1. 先限制恢复调度：按轮次持久化attempt_count、next_retry_at、last_error与独立recovery_state；逐步延长间隔并设置次数/总时间预算，到限暂停恢复、显示待处理。worker重启不得重置预算，多个unknown不得相互饿死或阻塞正常新任务。
2. 再降低单次成本：外部执行记录、配置与凭据版本均无变化时避免高频高成本检查；沙箱预检可按镜像、策略、工作区身份和有效期缓存，变化时重新验证。不得绕过安全检查，不直接用缺失终态伪造成功。
3. 补恢复观测：关联轮次、触发原因、重试次数、错误类别、下次时间、预检与读取耗时、容器创建/销毁计数；后台恢复不伪造用户行为事件，记录脱敏Task Trace节点。
4. 恢复暂停与原轮次业务状态分离。无权威终态时保留unknown及必要写入保护；人工或条件触发恢复需明确语义，不能直接改数据库清除active_turn掩盖问题。

临时处置边界：不建议反复删执行容器、全局prune或无证据把unknown改成completed；本次没有停止worker或改运行配置。

## 建议验收

- 永久缺少终态：有限尝试后暂停，在约定观察窗内不再创建恢复容器。
- 瞬态故障：按退避重试，权威终态到达后正确收敛，保持账务和执行保护语义。
- worker重启：重试预算和下次时间不丢失，不形成启动风暴。
- 多轮次：分别调度，旧unknown不阻塞正常新任务；无重复业务执行。
- 预检缓存：相同身份有效期内复用，镜像/策略/工作区变化后失效，安全校验失败拒绝执行。
- 观测：恢复原因、结果和资源计数可追踪，不泄露原文或凭据。
- 真实容器证据与合成测试分开报告，验证清理闭环且共享服务不受影响。

## 产品数据采集与系统影响

product_data_collection_observability: applicable（拟修复后台恢复观测）；affected_layers: task_traces、task_trace_spans。请求日志仅在后续新增人工恢复API时适用；后台扫描不生成usage_events。validation: 本次已保留脱敏代码/运行证据；正式观测与回归尚未实现，后续按docs/standards/product-data-collection-observability.md完善。

预计涉及worker调度、持久化恢复元数据（SQLite/MySQL兼容）、后端测试及恢复状态展示；是否改API/UI与客户端生成在方案评审确定。当前仅capture，不改业务代码、数据库或部署，不创建Change或纳入Sprint。

