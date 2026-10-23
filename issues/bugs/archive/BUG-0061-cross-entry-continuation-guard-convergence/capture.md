---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断
status: done
created_at: '2026-10-21 15:36:49'
updated_at: 2026-10-21 17:25:21
severity: high
environment: local docker
related_requirement: null
related_bug: BUG-0060-direct-command-completion-proof-drift
---

# 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断

## 现象

BUG-0055 产品治理执行受阻后由 CLI 续接完成，当前验收 12/12、ready=true，但产品卡片仍在待开发，显示“结果待核对”，完成 / 归档不可用；刷新仍阻断。覆盖直接治理命令跨入口续接，不限当前卡片。

## 复现步骤

1. 产品 Chat 发起 opsx-apply，执行结束但收尾依赖核验冲突，保留 needs_review 保护。
2. CLI 续接修复、验证、验收与 Workflow Sync，当前交付达到 ready。
3. 返回产品刷新卡片，比较当前交付事实、旧执行保护、卡片阶段和实际发送准入。

## 期望与实际

期望：保留旧操作及不可变证据，独立核验合法后继完成事实；满足完整准入时安全收敛保护。真实交付冲突、缺证、运行中操作及过期回调仍拒绝，并提供可定位差异和恢复入口。
实际：旧 opsx-apply 的 needs_review 保护阻断外部事实收敛，卡片回退至 confirmed_stage=ready-dev；验收 ready 与产品可归档不一致。

## 已有证据与判断边界

| 证据 | 来源 | 已观察事实 |
|---|---|---|
| E1 | 用户截图 codex-clipboard-ab8be641-f740-4c5f-8085-5aa79a091e46.png；同会话产品只读观察 | 待开发，开发5/5、测试7/7，结果待核对，归档按钮禁用 |
| E2 | opsx_acceptance.py --change fix-chat-turn-message-order --archive-readiness | ready=true，done=12，total=12，source=evidence |
| E3 | 部署数据库只读查询 execution_guards / completion_handoffs | opsx-apply；needs_review；terminal_status=completed；confirmed_stage=ready-dev；direct_dependency_conflict；收尾记录 blocked，尝试1次；最近核验2026-10-21 14:36:07（本地时间） |
| E4 | src/backend/app/governance/execution_context.py：reconcile_external | 有 operation_id 且为 running/needs_review 时直接返回；后继事实特殊收敛仅覆盖评审动作 |
| E5 | src/backend/app/governance/reader.py：卡片执行保护投影 | 保护未解除且历史结果未核验时以旧 confirmed_stage 覆盖阶段，并禁用动作 |
| E6 | src/backend/app/governance/direct_completion.py：verify | 完成证明与当前动作清单不同即报 direct_dependency_conflict |

阻断机制已确认；原始14:36冲突的逐文件归因尚未完成，不能断言全部变化均为无害收尾，也不能仅依据当前 ready、模型文字或退出码解除保护。后续补查同步时、终态与 CLI 续接后的文件清单及变化来源；缺少历史清单时如实记录缺口，以隔离复现验证机制，不伪造历史差异。

## 关联与重复检查

- BUG-0060-direct-command-completion-proof-drift：已归档，处理直接命令同步后证明漂移及安全恢复；本次为产品旧操作与 CLI 合法续接的后继证明衔接。
- BUG-0052-verified-result-execution-guard-not-released：已归档，关联执行保护收敛与当前动作准入。
- BUG-0055-chat-turn-message-order-inversion：当前恢复现场，原缺陷是消息排序，不将治理修复混入其排序范围。
- 用户已授权创建关联缺陷；阶段回退和归档阻断是同一因果链，保持单条。

## 修复范围与建议验收

- 区分旧操作结果与当前后继交付；验证动作、对象、版本、依赖、完成事实和授权，保留原记录，禁止删保护或伪造旧证明。
- 分类文档收尾、无关对象并发、合法 CLI 续接与真实交付冲突；展示具体阻断原因、差异及可安全执行的核验入口。
- 覆盖产品受阻→CLI 续接完成→产品核验→实际发送→归档终态；对比 CLI 与产品准入，不仅验证 ready 或按钮可点。
- 覆盖重复核验、刷新、并发新执行、过期回调和中断恢复；真实冲突及缺证继续阻断，不重复执行原命令或重复合并规格。
- 恢复 BUG-0055 前核实当前身份、阶段、证据及运行状态；本次 capture 不解除保护、不触发归档。

## 影响与严重度

初判 high：阻断合法交付流转与归档，可能诱导重复执行；尚无数据丢失证据。跨入口通用机制适用于其他 Chat 治理对象，其他对象实际影响待验证。

## 数据采集与观测

product_data_collection_observability: affected。affected_layers: governance workflow、API admission、UI projection、completion proof。validation: 后续验证核验原因、差异分类、关联操作和恢复结果的脱敏观测；不记录密钥、会话正文或完整私有清单。DB schema 变更尚未决定，不在 capture 阶段声明需要迁移。

## 附件

截图保留在当前对话；仓库仅记录附件名及脱敏事实。当前未复制原始数据库或聊天日志。
