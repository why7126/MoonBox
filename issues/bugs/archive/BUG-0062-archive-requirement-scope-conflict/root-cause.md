---
bug_id: BUG-0062-archive-requirement-scope-conflict
title: 归档恢复条文冲突误判根因分析
created_at: '2026-10-21 17:58:42'
updated_at: '2026-10-21 17:58:42'
root_cause_status: confirmed
---

# 归档恢复条文冲突误判根因分析

## 根因状态

status: confirmed

确认范围：本地归档证明与同步判定机制；不等同于修复验收通过。2026-10-21本轮再次只读核验，原机制仍可复现。部署UI未重新采样，页面表现不作为本次确认依据。

## 现象

REQ-0046的36项AC与附件完整，但后续同模块不同条文变更使恢复准入失败，进度投影为0/36；Sprint浅层预检与同步预演不一致。现场及命令见[缺陷主文档](bug.md)。

## 证据链

| ID | type | source | 摘要与支持判断 |
|---|---|---|---|
| E1 | reproduction | src/backend/app/governance/archive_recovery.py：recovery_state | 本轮只读返回archive_spec_baseline_changed，定位为规格连续证明准入阻塞 |
| E2 | data_sample | openspec/archive/2026-10-21-fix-chat-unified-run-status-verification/；对应.archive-recovery日志 | 完成事实成立，delivery_input_hash和delta_hash与记录一致 |
| E3 | data_sample | 目标evidence/acceptance/20261020232423610065-fcce3bed/manifest.json；acceptance_evidence.artifacts_match | 本轮读取完整manifest为passed、36项，全部附件哈希匹配 |
| E4 | reproduction | archive_recovery：read_record、requirement_blocks、verify_chain_effects、verify_delta_effects | 本轮四条后继哈希连续到当前规格；三条模块重叠但标题无交集；原条文及后继最终条文均匹配 |
| E5 | code_path | src/backend/app/governance/archive_recovery.py：delta_scope、transition_chain | 使用模块目录集合；scope与protected相交直接跳过该链节点，无法形成可接受链 |
| E6 | code_path | src/backend/app/governance/acceptance_evidence.py：archived_readiness；archive_admission.py：_issue_acceptance | 前者吞掉具体恢复错误，后者把没有stale明细的失败视为所有AC失效，形成0/36 |
| E7 | reproduction | scripts/sync-workflow-status.py --event sprint.archive --sprint sprint-011 --dry-run | 同会话预演将REQ-0046投影pending；未执行实际Sprint同步 |
| E8 | code_path | scripts/workflow_sync/issue_subdocuments.py：acceptance_status_for；scripts/validate-sprint-archive-readiness.py | 同步调用深层归档判定，Sprint预检仅任务、trace/摘要与陈旧状态，导致前后口径不同 |

四条后继按顺序为fix-verified-result-execution-guard-convergence、fix-direct-command-completion-proof、fix-chat-turn-message-order、fix-cross-entry-continuation-guard。第一条无模块交集；后三条分别涉及governance-command-durable-recovery、web-catalog-chat-workbench、governance-command-durable-recovery，但均不改目标Requirement。原始完整清单和日志不改写。

## 已排除假设

- 目标交付或增量被改写：本轮哈希匹配，排除本现场该原因。
- 原AC附件损坏：36项附件全部匹配，不支持整体失效。
- 目标条文被后继覆盖：标题交集为空，原条文当前效果校验通过。
- 当前规格缺少完整后继链：连续四条链到当前哈希，最终效果校验通过。
- 纯前端缓存问题：本地共享判定函数已直接复现，不能靠刷新消除。

## 已确认根因

模块级范围比实际条文冲突更宽；同模块独立条文被判作保护范围重叠，合法链节点被排除。这是现有代码和测试的显式行为，不是删除某个日志即可恢复的偶发问题。随后异常归并丢失恢复原因，验收聚合将恢复失败当作全部AC失效；Sprint入口又没有同源深层预检，从而迟到暴露阻塞。

## 修复方向

使用模块与Requirement标题组合计算可证明的冲突范围；解析不确定、同条文操作或重命名仍拒绝。完整哈希链、身份唯一、交付与附件完整性、原条文和后继最终效果继续验证。独立返回AC证据结果与恢复准入结果，并将Sprint预检统一接入同一判定。同步规格、现有重叠拒绝测试及负向安全门禁，不直接编辑已生效规格或历史记录。

## 验证闭环

故障侧只读复现及排除检查已完成；修复已实现条文级判定、AC进度与深层预检，源码回归通过，部署观察已通过。建议验证矩阵见[验收标准](acceptance.md)，逐AC结果见当前Change验收证据，产品观察未通过前不宣称就绪。完整根因文档可进入评审不代表修复完成，不自动关闭sprint-011。
