---
bug_id: BUG-0064-chat-unknown-recovery-container-churn
title: Chat 未知轮次恢复调度与资源消耗验收
acceptance_status: passed
created_at: '2026-10-26 13:11:48'
updated_at: 2026-10-30 08:33:53
---

# Chat 未知轮次恢复调度与资源消耗验收

## 验收状态

隔离修复验收通过（passed）；原运行部署未升级

以下回归标准已按当前源码完成隔离验证，证据来自自动验收与真实Docker观察。范围对应bug.md的AC-01至AC-08。

## 环境与证据约定

使用独立授权测试库、工作区与临时容器，不能改写历史真实unknown记录。容器创建前遵守docs/standards/temporary-docker-lifecycle.md，保存必要证据后清理并复查；不影响共享服务、卷与宿主数据。测试参数使用有限明确值，记录最大退避周期、次数/时间预算、缓存有效期和调度预算，禁止用缩小到零或无限值伪装通过。

合成时钟用于快速覆盖调度边界，真实Docker观察覆盖状态与资源效果，分别标明。部署验收核对实际代码/镜像版本，不能仅凭本地测试断言运行实例已修复。数据库迁移与持久化在SQLite和MySQL兼容路径分别验证。

## 回归验收项

| 编号 | 条件与操作 | 通过条件 | 证据 | 状态 |
|---|---|---|---|---|
| AC-01 | 外部轮次永久无权威终态或记录缺失，启动有限恢复预算 | 到限进入独立暂停态；跨至少一个最大退避周期无该轮次新恢复容器；原业务unknown与必要保护保持 | 合成调度时间线、真实Docker create/destroy计数、状态投影 | 通过 |
| AC-02 | 读取先暂时失败、后返回权威completed/failed/interrupted | 下次时间前不尝试，按退避恢复；正确映射终态、清理active身份并保持既有账务语义；不重发原命令 | 受控执行器响应、调度/状态记录与副作用计数 | 通过 |
| AC-03 | 等待或暂停期间重启worker；领取恢复后异常中断 | 尝试预算和下次时间不重置；中断租约/并发声明可恢复且不永久锁死；恢复暂停不启动风暴 | 双库持久化回归、重启前后快照、真实容器事件 | 通过 |
| AC-04 | 多条unknown与正常任务并存，重复/并发触发同一恢复 | 每轮次独立预算；同轮次至多一个有效恢复；旧轮次不饿死新任务，正常任务在预先约定的调度预算内领取 | 可控时钟并发测试、任务领取顺序、实际等待时间 | 通过 |
| AC-05 | 相同及变化的镜像/策略/工作区身份、缓存过期与预检失败 | 有效身份可复用，改变或过期重新校验；失败从不复用为通过；配置/凭据变化后的恢复按设计重新验证，不输出秘密 | 缓存命中/失效计数、安全拒绝测试、真实预检证据 | 通过 |
| AC-06 | 暂停后无权威终态，随后显式恢复或新证据触发 | 不伪造业务终态，不跳过写入/并发/计费保护；恢复触发有权限和幂等检查，续接预算语义明确，不被后台轮询无限重置 | 状态机正反例、权限/幂等测试；有UI时补真实交互证据 | 通过 |
| AC-07 | RPC拒绝、无终态、身份异常、超时等恢复分支 | 有脱敏原因、次数、下次时间、暂停结果和容器计数；观测故障有降级记录、不阻断业务；后台无伪造用户行为 | Task Trace/span摘要及敏感信息检查 | 通过 |
| AC-08 | 恢复成功、失败、取消、中断后资源收尾及实际部署复核 | 本次容器最终退出回收；未触碰共享服务和数据；运行版本匹配交付版本，重复创建受预算控制 | 真实Docker观察、资源登记/check结果、部署版本指纹 | 通过 |

## 数据采集与文档一致性

product_data_collection_observability: applicable；affected_layers: task_traces、task_trace_spans；validation: AC-01至AC-08隔离验收通过。无HTTP来源的后台恢复request_logs为N/A，usage_events为N/A；新增人工恢复API须同步请求日志、权限、API文档、客户端生成与交互验收。

恢复元数据迁移需可升级并保持历史unknown及执行身份；新增前端提示与操作若纳入修复需同步UI文档。未新增界面时写明UI N/A，不能跳过后端恢复状态的可诊断性。生产迁移、发布及停止服务不由本验收文档自动授权。

## 通过条件与证据归属

全部适用AC均通过且有可复核证据，资源收尾无未说明残留，才可声明修复验收完成。后续关联Change的evidence/acceptance保存长期脱敏证据，Issue回填逐项结论；不把原始数据库、凭据、完整执行记录或本机路径写入文档。失败项保留原因并返修，未采集不得勾选通过。


## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-30 08:33:53
accepted_by: workflow-sync
source_change: fix-chat-unknown-recovery-container-churn
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-26-fix-chat-unknown-recovery-container-churn/evidence/acceptance/20261026143724020477-0ad85f24/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮逐项签认

AC-01至AC-08全部通过，详见[自动验收清单](../../../../openspec/archive/2026-10-26-fix-chat-unknown-recovery-container-churn/evidence/acceptance/20261026143724020477-0ad85f24/summary.md)及[交付验证](../../../../openspec/archive/2026-10-26-fix-chat-unknown-recovery-container-churn/verification.md)。SQLite142通过、MySQL23通过；各有一项明确不适用/显式模型样本跳过。真实Docker使用合成认证、当前代码和固定镜像，不调用模型；暂停330秒新增0容器，6创建/6销毁及取消、中断、超时回收通过。登记资源最终零残留。该签认针对隔离交付版本，不表示已发布或原运行实例已升级。
