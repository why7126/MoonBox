---
bug_id: BUG-0062-archive-requirement-scope-conflict
title: 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻
status: done
severity: high
created_at: '2026-10-21 17:45:33'
updated_at: 2026-10-21 19:11:20
environment: local
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0052-verified-result-execution-guard-not-released
---

# 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻

## 现象与影响

REQ-0046 对应 fix-chat-unified-run-status-verification 已归档，完整验收36/36通过且附件哈希匹配。后续三个 Change 修改同一规格模块中的不同 Requirement，恢复门禁仍判冲突；sprint-011 关闭预检通过，但 Workflow Sync 预演将 REQ 验收投影为 pending，准入摘要显示0/36，迭代无法安全关闭。

严重度初判 high：阻断合法归档闭环并丢失真实验收进度表达；未观察到数据丢失或越权放行。影响产品与CLI共享准入、验收投影、Sprint预检和同步；其他对象影响尚未逐一验证。

## 复现步骤

1. 使用已归档的 fix-chat-unified-run-status-verification 及其原始恢复日志、验收计划与完整manifest。
2. 核对后续 fix-verified-result-execution-guard-convergence、fix-direct-command-completion-proof、fix-chat-turn-message-order、fix-cross-entry-continuation-guard 的连续归档哈希链。
3. 执行 `python scripts/validate-sprint-archive-readiness.py --sprint sprint-011`；本会话修正五处陈旧文档引用后结果PASS。
4. 执行 `python scripts/sync-workflow-status.py --event sprint.archive --sprint sprint-011 --dry-run`，观察REQ-0046被投影为pending；不执行真实同步。
5. 执行 `python scripts/validate-issue-acceptance-ready.py fix-chat-unified-run-status-verification`，返回ACCEPTANCE_GATE_BLOCKED。只读调用 recovery_state 可取得 archive_spec_baseline_changed。

## 期望与实际

期望：在完整可信归档链、交付输入和附件完整性均满足时，模块内不相交条文的后继变更不使原验收失效；恢复阻塞与实际AC进度分开表达；Sprint预检、同步、CLI和产品采用同一判定。
实际：模块目录交集即拒绝；恢复错误被归并为archived-evidence-invalid，再变成pending与0/36。Sprint预检仅检查任务、trace/归档摘要及文档状态，未提前发现深层门禁阻塞。

## 已有证据与根因判断

复用同会话2026-10-21只读探索与归档预演，不复制原始会话、数据库或本机路径。以下是已执行检查事实，不是修复后结果。

| 编号 | 来源 | 结果 |
|---|---|---|
| E1 | openspec/archive/2026-10-21-fix-chat-unified-run-status-verification/；archive_recovery.py的只读身份和哈希函数 | 身份唯一、active不存在、完成事实成立，delta_hash与delivery_input_hash匹配 |
| E2 | acceptance_evidence.py：latest_manifest、artifacts_match | 完整运行20261020232423610065-fcce3bed，36项passed，全部附件哈希匹配 |
| E3 | openspec/archive/.archive-recovery/ 目标与上述四条后继日志 | 哈希链连续到当前正式规格；四条后继的delta与delivery哈希匹配 |
| E4 | archive_recovery.py：delta_scope、transition_chain | delta_scope使用模块目录；scope与protected有交集即丢弃节点，返回archive_spec_baseline_changed |
| E5 | 目标与三条重叠后继的增量Requirement标题比较 | 模块交集为governance-command-durable-recovery或web-catalog-chat-workbench，Requirement标题交集均为空 |
| E6 | archive_recovery.py：verify_chain_effects、verify_delta_effects | 后继最终条文与原目标条文均匹配当前正式规格 |
| E7 | acceptance_evidence.py：archived_readiness；archive_admission.py；scripts/workflow_sync/issue_subdocuments.py | 恢复错误变成通用证据无效；真实36项passed被准入摘要显示为0/36，同步预演为pending |
| E8 | scripts/validate-sprint-archive-readiness.py及本会话预检/同步预演 | 预检PASS与深层验收阻塞不一致 |

根因机制 confirmed：冲突粒度为模块目录，且诊断/进度投影未区分恢复阻塞与AC验收失败。现有tests/unit/test_archive_baseline_transition.py明确覆盖模块重叠拒绝，修复须经规格评审调整，不直接删除保护条件。本次未重新验收产品UI，也不把原验收通过解释为所有后继行为已重新验证。

## 判重与关联

已读取BUG注册表和CHANGELOG，并核对BUG-0052、0060、0061、0035等候选capture。
- BUG-0052：评审成果与执行保护收敛；本次为完成归档后的规格连续证明判定，关联但独立。
- BUG-0060、BUG-0061：直接命令完成证明、CLI后继交付与旧执行保护；本次不涉及旧operation解除或命令重放。
- BUG-0035：任务/验收进度及文档入口；本次为恢复错误吞掉真实AC结果，并涉及Sprint深层预检。
- BUG-0053、BUG-0054：部署源码输入解析、卡片诊断；本次无部署输入缺失。
上述候选均已归档，无相同触发条件的活动缺陷。冲突判断、进度保真、预检与同步一致性属于本次同一归档判定闭环，保持单条，不重开原已归档Issue。

## 推荐修复范围与建议验收

1. 冲突范围细化为模块与Requirement标题组合；同模块不同条文在证据完整时允许承接。同条文修改/删除/重命名、重复标题或无法可靠解析仍拒绝；保留唯一身份、连续链、交付/附件哈希、原条文及后继最终效果核对。
2. 验收事实与恢复准入独立表达；保留36/36真实已通过进度，并返回具体恢复原因、冲突Change与条文。不把不可确认项伪装通过。
3. Sprint关闭预检复用产品、CLI、Workflow Sync共用只读判定，深层失败在迁移前阻断；同步不得静默把恢复故障伪装为全部AC未通过。
4. 回归覆盖同模块不同条文、同条文冲突、删除/重命名、断链、重复身份、篡改、未知变化、并发变化、原始manifest不可变与四入口一致性。
5. 修复经正式评审、Sprint、OpenSpec和验收后复核REQ-0046及sprint-011；不重放成功归档，不重写历史哈希、journal或manifest，不强填passed。本次不扩大到同条文任意后继覆盖。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档准入、验收进度与错误诊断投影、Sprint预检和Workflow Sync。reason：改变治理判定与诊断传播语义。validation：本次仅记录已完成的只读函数核验与同步预演；正式修复须验证诊断、进度及各入口一致性。N/A：本次capture不改API、DB、UI、请求封装、对象存储、权限或生产部署，不新增日志/事件字段；实施若改变响应契约再同步API、客户端和对应测试。

## 边界与后续

sprint-011仅为受影响现场，不代表本BUG已纳入该迭代；iteration保持null。当前仅capture，尚未生成bug.md、评审或创建Change。
