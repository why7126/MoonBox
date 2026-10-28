---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断
status: done
created_at: '2026-10-21 15:36:49'
updated_at: 2026-10-27 16:02:30
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

## 2026-10-27 复发现象补充（未重新开启）

用户确认将本次现场补充至原 BUG，不新建编号；保留原 done / archive、sprint-012 和已归档 Change 事实。本节是新增复发证据，不代表历史验收失效或本次问题已修复。

### 现场与证据

- 现场对象：BUG-0056-requirement-center-context-load-latency；Change：fix-requirement-center-context-load-latency；现场 Sprint：sprint-014（不改变本 BUG 的历史 Sprint 归属）。
- 用户截图 codex-clipboard-c03d9ee4-af24-4c87-b0fc-f8e9b13691e3.png：卡片在验收中，研发 6/6、测试 7/7、验收 8/8，同时显示“结果待核对”，动作仅“查看执行”。截图留在本次对话，不复制会话与数据库原始数据。
- 同会话浏览器于 2026-10-27 13:01 左右只读观察 /requirements：状态详情显示“缺少正式同步成功证明”，最近核验 2026-10-27 06:57:57；进入原执行后，06:50:07 开始的轮次显示“已停止 / 执行已中断”。上述时间均为 Asia/Shanghai。
- 后续 Codex 接续完成：Change trace 的 execution.completed_at 为 2026-10-27 12:38:48；evidence/acceptance/20261027124209183130-5049da30/summary.md 为 complete / passed，8 项均通过。报告属于上述 BUG-0056 Change；不能单凭 8/8 认定原 Chat 轮次完成或当前产品动作已经放行。
- 源码线索：src/backend/app/governance/execution_context.py 的 _reconcile_external_plan 对带 operation_id 的 running / needs_review 记录保留原保护；direct_completion.status 对 needs_review 且缺少 sync_succeeded 的记录返回 direct_sync_missing；reader.py 在不可发送时投影“结果待核对”。

### 判断边界与影响

已确认本次页面的最新验收计数与旧停止轮次待核对提示并存；属于原 BUG 的跨入口续接场景复发证据。原案例是完成轮次的证明冲突，本次是停止轮次缺少正式同步证明。尚未核实部署版本与历史修复的覆盖关系，不能断定是代码回归、部署遗漏还是遗漏分支；本次未读取运行数据库、未尝试发送归档，也未解除执行保护。记录严重度沿用 high：正常后续动作入口受限，可能诱导重复开发；无数据丢失证据。

### 用户确认的处理方向与建议验收

1. 保留旧执行“已停止”、事件、原证明及核验原因，不篡改历史为成功，不删除保护记录来绕过校验。
2. 独立核验后续完成证据的对象、动作、版本、依赖、授权和有效验收结果；满足条件后解除当前对象限制，明确展示“已由后续执行完成”及证据入口。
3. 覆盖 Chat 中断且缺少旧同步证明 → 外部接续实现与验收 → 产品核验 → 卡片恢复合法后续动作的完整场景；同时检查真实动作准入，不能仅检查 8/8、ready 或按钮外观。
4. 缺证、证据过期、对象或版本不匹配、真实冲突、仍在运行的新执行均继续阻断并给出具体原因；覆盖重复核验、刷新、并发执行和过期回调，不重跑原开发或伪造旧证明。

### 观测与后续范围

product_data_collection_observability: affected；affected_layers: governance workflow、completion proof、API admission、UI projection。validation: 后续记录脱敏的旧执行与后继证据关联、核验原因和保护解除结果；本次只补充文档，未新增埋点、修改 API / DB / UI / 部署或生成客户端。DB 迁移需求待修复设计确认。
