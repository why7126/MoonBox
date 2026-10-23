---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 跨入口续接证明与执行保护收敛修复评审
review_result: approved
reviewed_at: '2026-10-21 15:57:03'
created_at: '2026-10-21 15:57:03'
updated_at: '2026-10-21 15:57:03'
review_basis: 用户明确执行 bug-review --approve；缺陷包及根因证据门禁
---

# 跨入口续接证明与执行保护收敛修复评审

## 评审结论

批准修复，维持high，采用常规fix，不走hotfix。范围为跨入口后继完成证明、直接命令同步采集的dry-run误识别、保护安全收敛及产品/CLI实际归档准入一致性；以BUG-0055为恢复现场，不按对象ID特判。

批准仅允许进入Sprint规划，不代表实现、验收、恢复或归档已完成。先纳入Sprint并同步in_sprint，再创建OpenSpec Change。

## 评审清单

| 项目 | 结论 | 依据 |
|---|---|---|
| 可复现或根因充分 | 通过 | 根因confirmed，10条证据；旧progress证明、CLI后继变化与两条恢复路径缺口相互印证；dry-run分号误识别已纯函数复核 |
| 严重等级合理 | high | 阻断合法治理流转及归档，诱导重复执行风险；无数据丢失或P0事故证据 |
| 回归验收明确 | 通过 | AC-001—AC-014覆盖证明语义、差异分类、权限、并发、幂等、产品实际发送及CLI归档、现场恢复与历史边界；全部未执行 |
| hotfix路径 | 不采用 | 无绕过正确性门禁的依据，按常规修复验证交付 |
| 临时处理 | 无已验证的解除方案 | 保留旧保护和成果，仅只读核查，禁止手改guard或重放原命令 |

## 证据边界与实施约束

- 19项是旧最后同步至探索当前态的累计差异，不是首次冲突文件清单；同步时正文缺失，历史行级归因仍partial。该边界不否定已确认机制，也不授权忽略真实冲突。
- 保留旧操作未完成事实，创建独立后继核验关系；核对对象、Change、绑定、权限、事件、输入与验收证据，用版本比较防止并发及过期回调。
- 不把外层退出0、任意sync_succeeded、任务勾选、静态ready或按钮可点当成产品业务完成证明。
- 负向门禁覆盖真实冲突、缺证/过期、身份变化、运行中操作；评审和归档保留专用协议，不重复合并规格。
- 部署后完成产品受阻→CLI续接→产品安全核验→实际发送→归档终态，并用等价隔离对象对照CLI。正式现场操作前重新确认状态，避免覆盖后续执行。
- 关联BUG-0060与BUG-0052；BUG-0055仅为恢复现场。本BUG不继承现场Sprint，不混入消息排序实现。

## 文档与观测

product_data_collection_observability: affected

affected_layers: governance workflow、completion proof、API admission、UI projection、recovery audit。

validation: 依AC-006/007/009/010/013验证关联、版本、脱敏原因与审计；API/客户端及UI文档随实现同步，DB迁移按设计判断。无须为本次文档评审修改代码、部署或安全权限。

## 门禁与提醒

根因证据门禁通过（10项）。root-cause.md status=confirmed表达根因确认度，保留该字段；不将扫描器的语义提醒误改为Issue状态。验收保持not_started，历史归因partial继续显式保留。

## 下一步

/sprint-propose --bug BUG-0061-cross-entry-continuation-guard-convergence
