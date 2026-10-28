---
bug_id: BUG-0064-chat-unknown-recovery-container-churn
title: Chat 未知轮次重复创建执行容器根因分析
root_cause_status: confirmed
created_at: '2026-10-26 13:11:48'
updated_at: '2026-10-26 13:11:48'
---

# Chat 未知轮次重复创建执行容器根因分析

## 根因状态

status: confirmed

确认范围：unknown恢复调度缺少退避、次数/时间预算及暂停条件，导致无权威终态的旧轮次反复创建容器。原执行最初进入unknown的具体历史原因不属于已确认结论；单次thread/read失败的具体分支也未被截获。

## 现象

无正常排队或运行轮次时，moonbox-chat-session持续创建并销毁。唯一unknown仍为会话active_turn，原执行记录没有轮次终态。删除某个容器不能解除调度触发条件。

## 证据链

以下复用2026-10-26同会话只读运行观察，完整脱敏摘要见[capture.md](capture.md#本轮脱敏证据)。本次未重放业务命令、修改数据库或创建新Docker样本，不声称重新运行修复测试。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | runtime_log | Docker create/destroy事件及AutoRemove采样 | 多个实例短时间连续创建后销毁 | 重复创建而非同一实例清理失效 |
| E2 | data_sample | canonical SQLite只读chat_turns/chat_conversations查询 | completed=62、failed=9、stopped=11、unknown=1；无运行/排队态；unknown仍active，更新时间为10月12日08:46:32（Asia/Shanghai） | 有长期满足恢复扫描条件的旧轮次 |
| E3 | code_path | 运行版本platform_worker.main；本地src/backend/app/chat/platform_worker.py同名函数 | 空闲时逐条扫描unknown调用恢复，无next_retry_at过滤或重试上限 | 调度触发条件长期成立且缺少退避 |
| E4 | code_path | 运行版本execution.reconcile_unknown；本地src/backend/app/chat/execution.py同名函数 | 身份校验后server_factory/read_turn；无映射终态或受捕获异常返回False；finally关闭server | 恢复不成功后仍保持unknown，下一轮再次处理 |
| E5 | code_path | 运行版本container_server.persistent_container_server；本地src/backend/app/chat/container_server.py同名函数 | 每次创建预检容器，再创建读取执行器 | 每次无效恢复都有重复启动成本 |
| E6 | config_diff | 两次容器工作区采样与会话source绑定的哈希比对 | 工作区哈希499e0c5d85一致，匹配session文件存在 | 创建资源与唯一unknown所在工作区关联 |
| E7 | data_sample | 匹配session的生命周期元数据 | 目标轮次有task_started与item_completed，无轮次完成/中断终态；最后记录停在10月12日08:46:24.233 | 缺少权威终态，工具完成不等于任务完成 |
| E8 | data_sample | chat_cleanup_jobs聚合 | 查询时队列为空 | 该采样时段并非删除会话维护队列触发 |

## 已排除假设

| 假设 | 处置与依据 |
|---|---|
| 只是历史验证容器没有删除 | E1显示新实例反复创建销毁；此前临时环境清理后现象仍存在 |
| 有正常新任务连续执行 | E2采样无排队或运行轮次；结论仅覆盖该采样时段 |
| 删除会话队列反复创建 | E8队列为空 |
| 执行容器没有自动删除 | E1包含destroy，AutoRemove=true |
| 原业务任务已经权威completed | E2与E7不支持；保留unknown，不推断成功或失败 |
| 部署与本地代码整体相同 | 全文指纹不同；仅确认关键恢复函数逐段一致 |

## 已确认根因

空闲worker持续挑选unknown，恢复函数对无终态或异常返回False，不更新重试预算或下次检查时间。容器工厂重复构建预检与读取执行器，关闭后仍无改变下一轮触发条件。控制循环有短暂主循环等待，但没有单轮次退避，实际创建频率还受Docker启动和读取耗时影响，不能把主循环等待值当作真实容器速率。

## 未决边界与补证

历史错误码execution_access_or_workspace_error未区分具体访问/工作区异常；本轮没有thread/read返回值或异常代码。已尝试数据库只读状态、session生命周期与部署代码核对；没有读取凭据或重放原业务。该缺口不影响无界调度机制的确认，但不能据此把旧轮次改成成功、失败或停止。

后续优先从授权历史日志提取同时间段错误类别，若历史不足如实标明不可恢复；在隔离样本分别模拟RPC拒绝、无终态和缺失轮次，记录脱敏尝试次数、错误类别、下次时间、容器计数及业务状态。无需为进入本BUG修复评审而索取历史对话正文或密钥。

## 修复方向

先落地持久化退避、预算、暂停和并发幂等，再优化无变化检查与预检复用，补后台恢复观测。恢复暂停与原业务终态分离，保留写入、并发、账务保护。预检缓存以镜像、沙箱策略、工作区身份和有效期约束，不复用安全失败。具体参数和迁移方案在Change设计确定，不能用无限默认值规避预算。

## 验证闭环

E1/E2/E6证明现象与候选关联，E3—E5解释重复触发及成本，E7/E8限制结论范围；这构成本缺陷的诊断证据闭环。修复闭环尚未执行，后续按[acceptance.md](acceptance.md)逐项取得合成回归与真实Docker证据，不把文档门禁通过称为修复验收通过。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: task_traces、task_trace_spans；validation: 已有脱敏运行证据，修复观测待开发。后台恢复不伪造usage_events；无HTTP触发时request_logs为N/A，新增人工恢复API时再覆盖请求与权限链路。

