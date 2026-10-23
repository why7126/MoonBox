---
bug_id: BUG-0049-archive-wrapper-workflow-sync-unrecognized
title: 归档包装脚本同步成功未识别导致看板停留验收中
status: done
created_at: '2026-10-19 22:57:27'
updated_at: 2026-10-20 08:13:21
severity: high
lifecycle_stage: plan
related_requirement: REQ-0027-requirement-center-command-chain-realization
related_bug: BUG-0044-requirement-stage-premature-transition-session-split
environment: docker
owner: 产品团队
discovered_at: '2026-10-19'
related_change: null
---

# 归档包装脚本同步成功未识别导致看板停留验收中

## 缺陷现象

在本地 Docker 产品内对 BUG-0048 执行归档后，Chat 报告“已归档”，正式 Change 和 BUG 已进入归档目录，BUG 状态为 done；需求看板却仍显示“验收中”“结果待核对 · 已产生的文档会保留”。聊天权限已根据正式对象状态变为完全只读，进一步形成跨入口结论不一致。

## 环境与前置条件

- 环境：本地 Web、backend、chat-worker、治理控制器，SQLite 数据库；沿用 2026-10-19 同会话 explore 的真实运行观察。
- 对象：BUG-0048-chat-legacy-panel-cleanup-removes-conversation，关联 Change 为 fix-chat-legacy-panel-cleanup-boundary，来源 Sprint 为 sprint-010。本 BUG 尚未纳入 Sprint。
- 前置条件：目标 Change 已完成开发及验收，具备归档条件；通过产品 Chat 执行包装脚本 finalize 路径。
- 本次文档生成未重新归档，也未声称已在其他环境复现。

## 复现步骤

1. 在目标 BUG 的产品会话发送 `/opsx-archive BUG-0048-chat-legacy-panel-cleanup-removes-conversation`。
2. 执行器调用 `bash scripts/archive-change.sh fix-chat-legacy-panel-cleanup-boundary --finalize`。脚本内部完成归档、Workflow Sync 和关联 Issue 迁移。
3. 等待本轮 completed，核对工具事件中包装脚本退出码为 0。
4. 对比正式文件目录与状态、私有 operation 凭证、对象执行门禁和看板阶段。

本例前置验收曾因勾选格式失败，修正后重新执行成功；此先前失败与最终同步漏识别分开记录。后续回归应使用独立待归档样本，不对已归档对象重复执行破坏性流程。

## 期望与实际

| 维度 | 期望 | 实际 |
|---|---|---|
| 归档结果 | 文件、同步及迁移经可信核验后确认完成 | 文件归档且 BUG 为 done，结构校验通过 |
| 执行凭证 | 记录包装脚本内部同步成功及最终状态 | operation 为 terminal/partial_write，所有步骤的 workflow_sync 和 sync_succeeded 均为 false |
| 对象门禁 | 结果验证后收敛为完成，保留归档只读约束 | needs_review/result_unverified，confirmed_stage=acceptance |
| 页面结论 | Chat、需求看板和对象权限一致 | Chat 已归档、对象只读，看板仍验收中并提示待核对 |

## 影响范围与严重等级

严重度 high：已成功归档对象的完成状态无法收敛，治理入口持续待核对，用户可能误判失败并重复执行。已观察范围仅为上述归档包装脚本路径；未证明所有治理命令受影响，未发现数据丢失。归档后的业务只读约束本身应保留。

影响模块包括命令观测、同步成功凭证、执行结果对账、对象门禁及看板投影。原 BUG-0048 的 DOM 清理和 REQ-0046 的评审结果不属于本次修复范围。

## 已确认机制与证据

根因判断：confirmed（限本例）。证据承接同会话只读取证，详见 capture.md 的已有证据表；此判断不代表已生成正式根因文档或完成评审。

1. `scripts/archive-change.sh` 的 finalize 分支内部调用 `sync-workflow-status.py --event opsx.archive`，然后执行关联 Issue 迁移；本轮工具事件显示包装脚本退出码为 0。
2. `src/backend/app/governance/direct_command_journal.py:is_formal_workflow_sync` 仅识别顶层 command 字符串中显式出现同步脚本和 --event 的命令。实际顶层命令是归档包装脚本，不满足识别条件。
3. 取证时私有 operation 的 final_revision 与正式快照一致，归档 `validate_result` 返回 true，但同步标记全部为 false，最终分类为 partial_write。这解释了“文件有效但同步证明缺失”。该摘要匹配是当时事实，不保证后续其他治理写入后仍相同。
4. `execution_context.py:reconcile` 要求匹配当前摘要的同步成功证明或已核验应用证明；该直接命令本轮没有候选/应用记录可作为回退依据，因此门禁未 confirm。
5. `reader.py` 对未放行对象采用 guard.confirmed_stage 覆盖卡片阶段，故正式 done 被投影为归档前 acceptance。数据库只读观察与用户截图相符。

### 证据入口

- 用户提供的两张截图：同会话附件；不复制临时绝对路径和原始截图。
- 正式 BUG：`issues/bugs/archive/BUG-0048-chat-legacy-panel-cleanup-removes-conversation/bug.md`。
- 正式 Change：`openspec/archive/2026-10-19-fix-chat-legacy-panel-cleanup-boundary/`。
- 脱敏运行态摘要与相关代码路径：本 BUG `capture.md` 的证据表。
- 原始消息、身份、凭证与数据库内容不落盘。

## 修复方向与验收建议

采用可校验的完成凭证，将对象、原执行、同步结果、Issue 迁移结果及最终文件摘要绑定；具体设计留待 bug-complete 和评审。不能仅按包装脚本名称、模型文字或单一退出码放行。

建议覆盖：包装脚本成功、内部同步失败、后续迁移失败、文件摘要漂移、重复核验、重启恢复、直接同步命令回归。对既有轮次采用受控核验恢复，保留历史记录，不重复归档、不直接改数据库解锁。跨入口最终展示一致，已归档对象仍保持只读。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow 命令观测、私有 operation、对象门禁、看板状态投影。
- validation: 复用已有运行态、代码与文件证据；后续验收需要核对凭证关联、摘要、同步状态、拒绝原因及恢复幂等性。
- N/A：本轮仅生成缺陷文档及同步元数据，不修改 API、DB schema、UI、安全或部署，不需要生成客户端；实施影响在后续 Change 确定。
