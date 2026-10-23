---
bug_id: BUG-0062-archive-requirement-scope-conflict
severity: high
environment: local
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0052-verified-result-execution-guard-not-released
owner: 产品团队
title: 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻
status: done
created_at: '2026-10-21 17:50:06'
updated_at: 2026-10-21 19:11:19
discovered_at: '2026-10-21 17:45:33'
related_change: null
root_cause_status: confirmed
---

# 归档恢复按模块误判冲突导致验收进度失真与迭代关闭受阻

## 缺陷摘要

REQ-0046-chat-execution-output-status-feedback 的 Change fix-chat-unified-run-status-verification 已完成归档，36项验收全部通过且附件完整。后续Change仅修改相同规格模块内的其他Requirement，归档恢复却因模块目录交集被拒绝。错误继续传播成验收pending及0/36，造成sprint-011浅层预检PASS、深层同步预演受阻，迭代无法安全关闭。

本缺陷统一处理这条归档判定因果链：冲突粒度、验收事实保真、Sprint预检与同步一致性。不是重新实施REQ-0046，也不要求重放已完成归档。

## 环境与触发条件

- 环境：本地治理仓库与CLI，只读核验；本轮未重新观察部署产品UI。
- 目标归档：`openspec/archive/2026-10-21-fix-chat-unified-run-status-verification/`。
- 受影响迭代：sprint-011；本BUG已评审通过并纳入sprint-012。
- 目标完成归档后，正式规格经其他已完成Change演进；哈希链连续、归档身份唯一、交付及证据哈希匹配。
- 后继与目标共享规格模块，但实际Requirement标题不相交，原条文和后继最终条文仍匹配当前正式规格。

## 复现步骤

1. 保留现有正式归档、恢复日志和验收清单，不修改哈希或历史证据。
2. 运行 `python scripts/validate-sprint-archive-readiness.py --sprint sprint-011`。同会话五处陈旧文档引用修正后，该检查返回PASS。
3. 运行 `python scripts/sync-workflow-status.py --event sprint.archive --sprint sprint-011 --dry-run`；REQ-0046验收被预演投影为pending，不执行真实同步。
4. 运行 `python scripts/validate-issue-acceptance-ready.py fix-chat-unified-run-status-verification`，返回ACCEPTANCE_GATE_BLOCKED。
5. 只读核对 `archive_recovery.recovery_state`、`acceptance_evidence.archived_readiness` 与 `archive_admission.change_acceptance`：分别得到archive_spec_baseline_changed、archived-evidence-invalid和ready=false/done=0/total=36。
6. 比较原验收manifest、附件及后继增量：36项passed、附件全部匹配、后继链连续，模块交集存在而Requirement标题交集为空。

以上为同会话已执行的现场结果；未来复现需重新确认输入版本，不能把历史结果当作修复后验证。

## 期望与实际

| 维度 | 期望 | 实际 |
|---|---|---|
| 冲突识别 | 证据完整且条文不相交的同模块后继可以承接；真实冲突仍拒绝 | 按模块目录交集一律拒绝 |
| 验收进度 | AC证据有效性与恢复准入独立表达，保留36/36 | 恢复错误被当作验收证据整体无效，呈现0/36 |
| 诊断 | 返回具体错误码、相关Change及冲突范围 | 统一变为archived-evidence-invalid或通用验收阻断 |
| Sprint关闭 | 迁移前预检与同步、产品和CLI使用同一深层判定 | 浅层预检PASS，同步预演pending |

## 影响范围与严重等级

严重度high：阻断已完成交付的迭代关闭，错误进度可能诱导重复验收或归档。已确认现场为REQ-0046与sprint-011；共享机制可能影响其他对象，但尚未逐条核验，不宣称全量受影响。无数据丢失、越权归档或生产故障证据。

涉及后端归档恢复、结构化验收及诊断投影、Workflow Sync、Sprint归档预检。BUG-0052/0060/0061的执行保护和BUG-0035的卡片投影仅为关联历史，判重依据见[capture.md](capture.md)。

## 已确认根因与证据

根因机制为confirmed，直接证据来自同会话只读函数核验、规格比较和同步预演；完整证据表E1—E8见[capture.md](capture.md#已有证据与根因判断)。

| 证据 | 定位 | 结论 |
|---|---|---|
| E1/E2 | 目标trace、恢复日志、验收运行20261020232423610065-fcce3bed | 唯一归档、完成事实、交付及增量哈希匹配；36项passed，附件全部匹配 |
| E3/E5/E6 | 目标与四条后继归档日志、增量规格；verify_chain_effects与verify_delta_effects | 连续哈希链到当前正式规格，原条文与后继最终结果均匹配 |
| E4 | `src/backend/app/governance/archive_recovery.py`：delta_scope、transition_chain | 范围仅为模块目录；scope与protected相交即丢弃合法链节点 |
| E7 | `src/backend/app/governance/acceptance_evidence.py`：archived_readiness；`archive_admission.py`；`scripts/workflow_sync/issue_subdocuments.py` | RecoveryBlocked被归并成通用证据无效；进度与pending随之失真 |
| E8 | `scripts/validate-sprint-archive-readiness.py` | 任务、trace/摘要、陈旧状态检查未覆盖共享深层验收判断 |

后继链先经过无模块交集的fix-verified-result-execution-guard-convergence，再依次经过：

| Change | 与目标重叠模块 | 与目标重叠Requirement |
|---|---|---|
| fix-direct-command-completion-proof | governance-command-durable-recovery | 无 |
| fix-chat-turn-message-order | web-catalog-chat-workbench | 无 |
| fix-cross-entry-continuation-guard | governance-command-durable-recovery | 无 |

现有 `tests/unit/test_archive_baseline_transition.py` 明确测试模块重叠拒绝；这说明需要评审调整冲突语义和测试，不能仅删除判断。已排除本现场的附件哈希损坏、交付输入变化、归档身份重复、后继哈希断链和目标条文被覆盖；未外推到所有历史归档。

## 推荐修复边界

1. 使用“模块＋Requirement标题”计算冲突；同模块不同条文可在完整证明下承接。同条文修改/删除/重命名、重复标题、未知操作及不可可靠解析仍阻断。保留完整链、唯一身份、交付与附件哈希、原条文及后继最终效果核验。
2. 独立表达证据有效AC进度与恢复准入，传播具体阻断原因；恢复失败不清零有效AC，AC损坏也不能被历史passed掩盖。
3. Sprint关闭预检复用产品、CLI和Workflow Sync共享的只读判断，在目录迁移或状态写入前阻断；未知与缺证据保持拒绝。
4. 不修改原manifest、journal、历史哈希或已归档Issue终态来绕过门禁；不扩大为允许同条文任意后继覆盖，不重放模型或重复合并规格。

## 后续验收重点

- 同模块不同Requirement且完整证据链时通过；REQ-0046显示36/36及正确恢复结论。
- 同条文冲突、删除/重命名、重复标题、断链、未完成归档、身份歧义、交付/附件篡改、未知与并发变化仍拒绝。
- 恢复受阻时保留真实AC结果和可定位原因；AC证据确实损坏时正确减少有效计数。
- Sprint预检、同步、产品与CLI同输入同结论；深层失败不得先迁移Sprint。
- 历史journal、manifest、归档内容保持不变；只读判定无业务写入，重复核验幂等。

验收标准已整理至[acceptance.md](acceptance.md)，当前11项AC通过，部署观察与临时归档预演通过；最终共享准入ready，待显式归档。

## 产品数据采集与链路观测

product_data_collection_observability: applicable。
affected_layers: agent_workflow_governance、归档准入、验收与错误诊断投影、Sprint预检、Workflow Sync。
reason: 推荐方案改变治理判定及诊断传播语义。
validation: 复用capture的只读身份、哈希、规格比较与同步预演证据；修复后需覆盖共享入口、进度、负向安全场景及脱敏诊断。
N/A：本次仅生成缺陷文档，不改API、DB、UI、请求封装、对象存储、部署、权限或客户端。后续实现若改变响应字段须同步API/OpenAPI、客户端及测试；不新增原始会话、凭证或本机路径采集。

## 追溯与当前状态

来源为用户bug-generate及bug-complete授权和已完成只读探索，关联REQ-0046与BUG-0052。状态in_sprint，iteration为sprint-012，已关联fix-archive-requirement-scope-conflict（已实施，任务11/11）。已补齐[root-cause.md](root-cause.md)、[workaround.md](workaround.md)及[acceptance.md](acceptance.md)，根因证据门禁通过，评审通过且已纳入Sprint；已在授权Change内修复代码，256项回归通过；部署观察与最终验收通过，未关闭sprint-011。
