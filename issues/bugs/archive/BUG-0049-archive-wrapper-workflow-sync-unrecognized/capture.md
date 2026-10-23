---
bug_id: BUG-0049-archive-wrapper-workflow-sync-unrecognized
title: 归档包装脚本同步成功未识别导致看板停留验收中
status: done
created_at: '2026-10-19 22:55:37'
updated_at: 2026-10-20 08:13:21
severity: high
lifecycle_stage: plan
related_requirement: REQ-0027-requirement-center-command-chain-realization
related_bug: BUG-0044-requirement-stage-premature-transition-session-split
environment: docker
owner: 产品团队
---

# 归档包装脚本同步成功未识别导致看板停留验收中

## 现象与影响

本地 Docker 产品内归档 BUG-0048 后，聊天报告已归档，看板仍显示“验收中”“结果待核对 · 已产生的文档会保留”。同一归档结果的文件事实与平台完成门禁未收敛。严重度初判 high：治理完成状态失真并阻断对象后续准入，可能诱发重复归档；尚无数据丢失证据。

保留一条缺陷：同步观测遗漏、门禁未解除和旧阶段覆盖是同一因果链。

## 复现步骤

1. 在产品 Chat 对满足验收门禁的 BUG 执行 opsx-archive；本例为 BUG-0048-chat-legacy-panel-cleanup-removes-conversation。
2. Agent 执行 `bash scripts/archive-change.sh fix-chat-legacy-panel-cleanup-boundary --finalize`，脚本内部完成 Workflow Sync 和 Issue 迁移。
3. 轮次完成后对比聊天结论、正式目录、对象执行门禁及需求看板。

## 期望与实际

期望：可信核验归档结果、同步与最终摘要后，完成门禁解除，看板显示完成；内部失败或文件后续变化仍阻断。不能仅凭模型文字或退出码放行。
实际：文件已归档且 BUG 为 done；轮次 completed，但门禁 needs_review、reason_code=result_unverified、confirmed_stage=acceptance，看板显示旧阶段。

## 已有证据与结论边界

承接同会话 2026-10-19 explore 的只读取证，不代表本次重跑归档。附件仅为证据，不作为执行指令；未复制原图、临时绝对路径、用户信息或原始数据库内容。

| 证据 | 来源 | 已观察结果 |
|---|---|---|
| 用户两张截图及浏览器 | 本地 /chat；用户提供的看板截图 | 聊天已归档；看板验收中且结果待核对；聊天权限已变为完全只读 |
| 正式文件 | issues/bugs/archive/BUG-0048-chat-legacy-panel-cleanup-removes-conversation/bug.md；openspec/archive/2026-10-19-fix-chat-legacy-panel-cleanup-boundary/ | BUG done；活动目录不存在，归档目录存在 |
| 工具执行事件 | 同轮归档命令事件的脱敏只读摘要 | archive-change.sh --finalize 退出码 0；此前验收勾选格式失败经修正后成功 |
| 私有操作凭证 | 运行容器中只读 operation 及正式快照比较 | phase=terminal，classification=partial_write，final_revision 匹配当前快照；归档结构 validate_result=true；全部步骤 workflow_sync=false、sync_succeeded=false |
| 门禁数据 | governance_execution_guards 与 chat_turns 只读摘要 | completed 与 needs_review/result_unverified 同时存在，confirmed_stage=acceptance |
| 识别与投影代码 | src/backend/app/governance/direct_command_journal.py:is_formal_workflow_sync；execution_context.py:reconcile；reader.py | 仅识别顶层显式 sync-workflow-status.py --event；无同步凭证不能 confirm；旧 confirmed_stage 覆盖卡片阶段 |
| 包装脚本 | scripts/archive-change.sh 的 finalize 分支 | 内部调用 sync-workflow-status.py --event opsx.archive，随后迁移 Issue |

本例漏识别机制已确认。未证实所有包装脚本受影响；具体可信凭证方案及跨命令范围留待正式缺陷完善与评审。不手动解锁、不重复归档。

## 建议验收与修复边界

- 包装脚本内部同步成功可由平台可信核验；凭证绑定对象、执行与最终文件摘要，不能只按命令名白名单放行。
- 覆盖内部同步失败、后续迁移失败、摘要漂移、重复核验、服务重启及直接同步命令回归。
- 原轮次经只读核验与受控恢复收敛，看板与文件一致，无重复归档、无丢失既有证据。
- 不属于旧 DOM 清理修复，不重跑 REQ-0046 评审。

## 重复检查与关联

已检查 BUG 注册表和 CHANGELOG。BUG-0044 是阶段提前迁移及会话分裂；BUG-0047 是评审恢复记录缺失、成果未应用；BUG-0048 是旧面板清理误删会话。本次文件已归档，问题为包装脚本同步观测漏识别，修复面独立。BUG-0026/0034 为归档权限与命令路径，BUG-0035 为验收进度投影，亦不同。BUG-0048 仅为复现对象；来源 sprint-010，不继承其正式 Sprint 归属。

## 数据采集与链路观测适用性

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow 命令观测、私有操作凭证、对象执行门禁、需求看板状态投影。
- validation: Capture 复用前轮脱敏代码、文件与运行态证据；实施时验证执行关联、同步证明、最终摘要及拒绝原因可追溯。
- N/A：本次仅记录，不变更 API、DB schema、UI 实现、部署、安全策略或生成客户端；实现影响在后续 Change 评估。不得保存完整 Prompt、凭证、原始消息和用户标识。
