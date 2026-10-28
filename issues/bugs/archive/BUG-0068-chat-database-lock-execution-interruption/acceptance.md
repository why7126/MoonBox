---
bug_id: BUG-0068-chat-database-lock-execution-interruption
title: Chat 数据库锁竞争与执行恢复验收标准
created_at: '2026-10-27 08:25:20'
updated_at: 2026-10-27 09:09:47
acceptance_status: passed
---

# Chat 数据库锁竞争与执行恢复验收标准

## 验收范围

以下均为待执行的验收设计，不代表通过。需使用隔离测试数据，不复用真实失败轮次进行写入试验；保留SQLite与MySQL兼容、权限及执行保护。

| 编号 | 场景 | 验收标准与证据 |
|---|---|---|
| AC-001 | 原因定位 | 并发请求、持锁线程与事务、失败操作可通过同一时间窗和脱敏关联标识复核；原始异常细分码及调用栈足以解释触发条件。历史无法恢复项明确列出，用隔离复现验证机制。 |
| AC-002 | 正常并发 | SQLite中需求中心读取、Chat事件读取、鉴权与执行写入并发时，合法任务可完成并保存最终输出；覆盖 needs_review/stopped 重复读取与 terminal 零行 UPDATE，文件扫描期间不得持有长写事务；记录并发规模、事务时长、锁等待与HTTP错误率，预算在设计评审锁定。 |
| AC-003 | 瞬态与持续锁冲突 | 短暂锁释放后有界恢复；持续锁冲突明确失败或待核验，不死循环、不重复业务执行，已保存输出不丢失。 |
| AC-004 | 提交不确定性与账务 | 提交前失败、提交成功后响应丢失分别验证；事件游标、计费、完成证明不重复，不能无依据把未知结果当成功。 |
| AC-005 | 权限与会话 | 会话使用时间优化不放宽过期、撤销、冻结、跨空间权限；读接口权限校验继续有效。 |
| AC-006 | 恢复与页面 | 读取暂时失败不得误称历史被删除；重连后状态与权威终态一致，未完成交付仍被保护，用户能区分已停止与完成核验。 |
| AC-007 | MySQL与事务兼容 | 同类并发及失败路径在MySQL回归，无SQLite专属语义泄漏；记录环境与版本，不用SQLite测试替代MySQL证据。 |
| AC-008 | 可观测性与脱敏 | 记录错误分类、执行阶段、事务与请求关联；不记录凭据、SQL参数或正文，诊断写入失败不阻断主流程。 |
| AC-009 | 原任务安全续接 | 在隔离样本验证重启worker、恢复读取、人工续接及旧回调：不重跑原命令、不伪造完成，完成证明只来自正式交付。 |

## 执行与证据要求

按AC保存环境、步骤、期望/实际、命令摘要、脱敏请求/事务证据。合成回归、隔离并发和真实运行分别标明；失败不得写passed。性能样本数与时延预算在设计阶段根据基线确定，不编造已测数值。

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、Agent Workflow。validation: 本次只制定验收，全部待执行。usage_events、对象存储本次N/A；API及客户端是否变化在设计确定。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-27 09:09:47
accepted_by: workflow-sync
source_change: fix-chat-database-lock-execution-interruption
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-27-fix-chat-database-lock-execution-interruption/evidence/acceptance/20261027090443095634-888712c4/summary.md]
failed_items: []
source_event: opsx.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮验证签认

AC-001至AC-009已按Change/verification.md矩阵验证：数据库与并发使用隔离SQLite/MySQL；提交未知与恢复使用故障注入；真实执行器新样本completed、结果读回一致；页面使用合成身份的真实浏览器观察。原06:53历史SQL/线程仍缺失，按AC-001约定明确记录。现有部署未更新，不将本次源码验证表述为原生产轮次成功。逐项自动验收结果由Workflow Sync回填。
