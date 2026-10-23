---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断
status: done
created_at: '2026-10-21 15:43:58'
updated_at: 2026-10-21 17:25:20
severity: high
environment: local docker
related_requirement: null
related_bug: BUG-0060-direct-command-completion-proof-drift
owner: 产品团队
discovered_at: '2026-10-21 15:36:49'
related_change: null
root_cause_status: confirmed
historical_attribution_status: partial
---

# 产品执行受阻后 CLI 续接完成未收敛旧保护导致阶段回退与归档阻断

## 现象与影响

产品 Chat 的 BUG-0055 治理执行结束但交付受阻，CLI 续接后验收12/12、ready=true，产品仍显示待开发、结果待核对，完成 / 归档按钮禁用；刷新无效。开发5/5、测试7/7与旧阶段并存。此问题属于通用直接治理命令的跨入口后继证明与执行保护衔接，不只修当前卡片。

严重度 high：合法交付被阻断，可能诱导重复执行；未发现数据丢失证据。当前现场为本地 Docker，其他对象的影响需通用回归确认。

## 复现步骤

1. 在产品对已纳入迭代的对象执行 opsx-apply，保留原操作身份与完成证明。
2. 由于验证环境不足，完成部分任务并同步 opsx.progress，继续写回阻塞及收尾说明，轮次结束，业务尚未完成。
3. 在 CLI 续接同一交付，补齐验证和验收，执行正式完成同步，获得当前输入有效的 ready。
4. 刷新产品卡片并检查实际动作准入：旧 needs_review 仍阻断，卡片回退到旧 confirmed_stage。

## 期望与实际

期望：原执行保持真实未完成事实，CLI 后继交付有独立可核验证明；验证身份、依赖、版本、完成事件及当前证据后安全收敛保护，产品与 CLI 的当前归档准入一致。真实冲突、缺证、运行中操作与过期回调继续拒绝。

实际：旧证明与后继交付清单必然不同；外部事实收敛直接返回，已有证明的显式恢复又要求完全相等，无法承接合法后继完成。旧保护将当前卡片覆盖为 ready-dev。验收 ready 不能单独证明产品允许实际发送归档。

## 已确认机制与证据

| 编号 | 证据来源 | 事实与结论 |
|---|---|---|
| E1 | capture.md 引用截图及同会话浏览器只读观察 | 待开发、结果待核对、归档禁用，与开发/测试完成计数并存 |
| E2 | opsx_acceptance.py --change fix-chat-turn-message-order --archive-readiness | ready=true，done=12、total=12；只证明验收门禁，不代表产品保护已解除 |
| E3 | 部署数据库 execution_guards、completion_handoffs 只读查询 | action=opsx-apply，needs_review，confirmed_stage=ready-dev，terminal_status=completed，direct_dependency_conflict；收尾blocked，最近核验2026-10-21 14:36:07本地时间 |
| E4 | 原 direct-command journal | 140个工具边界，3份同步清单；最后正式同步为opsx.progress；终态classification=sync_incomplete，未签认最终完成证明 |
| E5 | 原轮次 chat_events seq669 | opsx.progress成功；任务9/12，验收pending，不能视为交付完成 |
| E6 | 原轮次 chat_events seq683/684 | 随后写入Change verification.md与trace.md，追加环境门禁阻塞及本轮收尾说明，工具退出0；证明存在同步后写回，但不据此推断所有历史差异 |
| E7 | direct_completion.manifest/differences 对旧最后同步清单与当前清单比较 | 19项差异，详见下表；规则、相关正式规格、对象注册信息与Sprint投影在当前动作清单内无差异 |
| E8 | execution_context.py：reconcile_external | 有operation_id且running/needs_review时直接返回；后继收敛特殊分支只覆盖评审动作 |
| E9 | direct_completion.py：verify/recover | 有清单的恢复仍走完全相等校验；合法后继变更没有独立承接路径 |
| E10 | reader.py：执行保护投影 | 未解除保护且历史未核验时覆盖为旧confirmed_stage，并禁用动作 |

root_cause_status=confirmed 指上述阻断机制和触发条件已由运行记录及代码确认；不表示历史每个文件的具体内容、写入者和时间均已确认。

## 19项文件差异清单

以下均为旧最后同步证明至探索时当前清单的累计差异，不是“14:36首次冲突的19个文件”。Issue目录为 issues/bugs/review/BUG-0055-chat-turn-message-order-inversion/；Change目录为 openspec/changes/fix-chat-turn-message-order/。验收批次为20261021150824291429-1d703a4d。

| 编号 | 相对对应目录路径 | 类型 | 判断边界 |
|---|---|---|---|
| 1 | Issue acceptance.md | modified | 验收状态及结果，需要后继证据 |
| 2 | Issue trace.md | modified | 生命周期和关联完成事实 |
| 3 | Change design.md | modified | 设计/验证边界，不能一概忽略 |
| 4 | Change tasks.md | modified | 任务完成变化，需逐项验证 |
| 5 | Change trace.md | modified | 执行及验收完成记录 |
| 6 | Change verification.md | modified | 验证及环境阻塞解决说明 |
| 7 | Change evidence/acceptance/20261021150824291429-1d703a4d/summary.md | added | 验收总摘要，需核验输入指纹及归属 |
| 8 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-001/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 9 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-002/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 10 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-003/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 11 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-004/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 12 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-005/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 13 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-006/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 14 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-007/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 15 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-008/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 16 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-009/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 17 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-010/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 18 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-011/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |
| 19 | Change evidence/acceptance/checkpoints/20261021150824291429-1d703a4d-checkpoint-AC-012/summary.md | added | AC检查点派生摘要，不能仅凭存在放行 |

本清单是治理快照纳入的文件投影，不代表代码、JSON证据、图片等整个仓库只有19处变化。相关正式规格无差异也不等于所有交付输入自动可信。

## dry-run误识别与完成事件混淆

原轮seq71包含 opsx.apply --dry-run; 后接其他命令；内部同步报告“Completion requires all tasks checked”，但外层shell退出0，journal仍记录sync_succeeded。is_formal_workflow_sync排除表达式未将分号识别为dry-run参数边界。

本轮只调用纯识别函数复核：带 --dry-run; true 返回True；普通结尾 --dry-run 返回False；opsx.progress返回True。没有执行这些同步命令或写业务数据。此证据确认误识别，不仅是推测。

最后清单来自后续真实opsx.progress，因此不能把当前阻断全归因于早期dry-run误识别。两者共同暴露证明语义缺口：开始、进度与完成事件需要区分，命令文本匹配及外层退出码不能替代结构化正式同步结果、实际写入与完成事件证明。

## 历史归因缺口

已检查私有operation/baseline记录、逐步哈希及原轮工具事件；同步时仅保留文件哈希，无该时点完整正文。启动baseline正文不等于最后同步时正文。可精确确定19项路径与增改类型，也可确认后续收尾写入目标，但不能完整重建全部历史行级变化、写入者与首次冲突归属。

因此历史归因标记partial。后续若找到可信快照可增补；否则保留缺口，用隔离样本记录同步、终态、CLI续接三个时点的清单和变化来源验证机制，不伪造历史差异。此缺口不否定已确认的阻断机制，也不授权忽略真实交付冲突。

## 通用修复方向与安全恢复

1. 保留旧操作、同步步骤与未完成事实；新增独立后继核验记录，关联原操作和CLI交付，不覆盖历史证明、不伪造原轮成功。
2. 校验同对象、同Change、项目绑定、操作者权限、实际完成事件、源码/交付输入、逐AC证据及当前准入；合法续接不是仅凭当前ready或文本声明。
3. 对派生验收输出验证归属与有效性；对设计、任务和交付输入变化进行受影响范围复验；无关对象变化单独判定；真实冲突、缺证、身份歧义继续阻断。
4. 核验过程保护快照稳定性和操作版本；采用原子版本比较，拒绝新执行竞争与旧回调，重复核验幂等。禁止直接清空guard、删除历史记录或重放原命令。
5. 正式同步证明包含事件类型、对象、写入/校验模式、执行结果和对应版本；正确处理分号、换行、复合shell、dry-run/check以及内部失败外层0。不把opsx.start/progress当作apply完成。
6. 卡片区分当前交付阶段、原执行结果和当前动作准入，显示具体差异分类、核验时间与恢复入口，不用旧阶段掩盖后继交付事实。
7. 产品与CLI共用当前动作判定；实际发送再次校验，归档沿标准包装链路完成，恢复不重复合并规格。

## 建议验收与回归范围

- 正向：产品执行受阻→CLI续接完成并验收→产品核验安全收敛→实际发送归档→归档终态；CLI归档使用等价隔离对象对照，记录同输入下准入结论。
- 反向：相关输入冲突、设计变化未复验、证据缺失/过期、身份或绑定变化、越权、运行中操作均拒绝；不可为成功样本降低门禁。
- 并发恢复：核验期间快照变化、新执行抢占、过期完成回调、重复核验、刷新及中断后重试，验证版本隔离和幂等。
- 证明采集：dry-run/check不同参数边界、引用文本、命令链与内部非零外层零不产生成功完成证明；正式失败、start、progress、apply完成分别断言。
- 文件分类：派生输出、合法后继交付、无关对象并发及真实冲突均有可解释判定；保留原始证据与恢复审计。
- BUG-0055恢复：操作前重新核实当前状态；验证实际发送与最终流转，不只验证静态ready/按钮可点；原轮历史不改写。
- 通用范围：覆盖REQ、BUG及支持的直接命令动作；评审、归档保留专用协议，不以通用恢复绕过专用门禁。合成回归、真实产品观察与CLI结果分别报告。

## 关联与边界

关联 BUG-0060-direct-command-completion-proof-drift、BUG-0052-verified-result-execution-guard-not-released；恢复现场 BUG-0055-chat-turn-message-order-inversion / fix-chat-turn-message-order / sprint-011。前两项已归档，本BUG独立处理跨入口后继证明；不将治理修复混入消息排序修复。缺陷包已补齐，评审前以trace当前状态为准；未纳入Sprint、未创建Change或实施恢复。

## 数据采集与同步影响

product_data_collection_observability: affected

affected_layers: governance workflow、API admission、UI projection、completion proof、recovery audit。

validation: 后续验证原操作/后继记录关联、判定原因、差异分类、核验版本和恢复终态的脱敏可追溯性；不采集完整提示、聊天正文、密钥或私有文件正文。API响应、UI提示及治理文档需随实现同步；数据库是否需迁移和客户端生成由设计确定，capture/generate阶段不改schema。对象存储和未启用客户端暂无已确认改动，须在设计时复核。部署后验证实际产品发送，不以本地CLI结果代替。

## 完善文档入口

根因和历史边界见[root-cause.md](root-cause.md)，临时处理见[workaround.md](workaround.md)，14项待执行标准见[acceptance.md](acceptance.md)，状态与关联见[trace.md](trace.md)。
