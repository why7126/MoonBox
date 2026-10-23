---
bug_id: BUG-0047-review-recovery-operation-record-missing
title: 评审恢复记录缺失导致成果未应用与卡片未流转
status: done
created_at: '2026-10-19 14:16:01'
updated_at: 2026-10-19 15:36:46
severity: high
owner: 产品团队
source: 本会话 explore 整合及用户授权 capture
lifecycle_stage: plan
captured_via: capture
classification_rationale: 已有评审能力执行失败，属于既有能力偏差，独立于通用恢复能力增量。
environment: 本地产品；沿用本会话 2026-10-19 取证，部署版本待核对
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0044-requirement-stage-premature-transition-session-split
related_requirements:
- REQ-0047-governance-command-durable-recovery
- REQ-0027-requirement-center-command-chain-realization
---

# 评审恢复记录缺失导致成果未应用与卡片未流转

## 现象与影响

对 REQ-0046-chat-execution-output-status-feedback 执行 /req-review 后，Agent 报告工作区评审通过，但轮次失败、成果未应用，刷新需求中心仍为待评审。high 为初判：评审流程被阻断，用户可能重复执行；未证实数据丢失，也未证明所有评审均受影响。

## 复现与期望

1. 在本地产品 /chat 打开目标需求评审会话，查看 2026-10-19 13:57:27 开始的 req-review 轮次。
2. 查看轮次轨迹及结果，核对后端轮次错误和治理应用记录。
3. 刷新 /requirements，核对目标 trace.md 的状态与目录。

期望：准备完整后执行，评审经后端应用与回读确认后进入 approved / review；失败保留成果并给出具体阻断原因。
实际：助手工作区校验通过不等于后端应用完成；事实源仍为 pending_review / plan，评审时间为空。

## 已有证据与结论边界

承接同会话 explore 的只读取证，不代表本次重新执行评审；未保存原始截图、会话标识、用户信息或数据库原文。

| 证据 | 来源 | 摘要 |
|---|---|---|
| E1 | 用户截图及 Chrome /chat | 展示本轮失败、治理校验未通过，同时保留助手“评审通过”原文。 |
| E2 | Chrome /requirements 刷新 | REQ-0046 仍处于待评审且保留发起评审动作。 |
| E3 | 本地 canonical SQLite 聚焦只读查询 | chat_turns 为 failed，error_code 为 direct_command_recovery_blocked；候选 rejected，错误归类 executor_unavailable；无成功应用记录。 |
| E4 | 当前需求 trace.md | pending_review / plan，reviewed、approved 为空。 |
| E5 | 对应私有恢复记录目录检查 | 仅有 baseline.json，缺少 operation.json。 |
| E6 | src/backend/app/governance/direct_command_journal.py，completion_block_reason；app/chat/execution.py | 恢复目录存在但 operation 读取失败会返回阻断原因，收尾将 completed 改为 failed。 |

已确认阻断点：缺少 operation.json 触发完成确认失败。尚未确认其缺失的产生原因、部署版本差异和全部失败收尾分支；根因整体保持待完善，不能据此标记完整 root-cause confirmed。正式复现需使用隔离夹具，不破坏真实评审记录。

## 修复方向与建议验收

- 查明恢复记录未生成或未保留的原因，核对准备、执行、收尾之间的契约及版本兼容。
- 对本次缺失记录分支提前检测，避免耗费完整评审后才发现不可恢复；不以补空文件或跳过校验掩盖故障。
- 保留原始阻断原因与候选/轮次关联，避免统一归类 executor_unavailable 丢失诊断信息。
- 复验正常评审的事实源、目录、应用记录与看板一致；缺失记录时不虚假成功，不覆盖并发成果，已有成果可核查。
- 通用持久化阶段、幂等续接和跨命令恢复归属 REQ-0047-governance-command-durable-recovery；用户反馈与可信结果展示归属 REQ-0046-chat-execution-output-status-feedback。

## 重复检查

已检查两类 CHANGELOG 与注册表。BUG-0044-requirement-stage-premature-transition-session-split 已归档，主要处理提前迁移与会话分裂，本次是评审收尾被缺失记录阻断，关联而不重开历史交付。BUG-0025 为命令写入未接入、BUG-0020 为 req.complete 投影残留，触发与修复面不同；BUG-0045 为验收环境能力，BUG-0046 为问题回答续接，均非本次恢复记录缺失。按用户要求独立记录本故障。

## 待补齐

- 缺失记录的产生原因、部署代码版本与稳定隔离复现。
- 失败成果实际保留位置、恢复条件与最终应用路径的验证证据。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、请求日志、Task Trace、阶段记录和 Web 结果关联。

validation: 后续验证预检失败、服务重启、重复恢复、并发冲突和结果同步的脱敏链路；本次仅记录，不改变 schema、API、部署、保留周期、对象存储或客户端生成物，以上实现变更本轮 N/A。
