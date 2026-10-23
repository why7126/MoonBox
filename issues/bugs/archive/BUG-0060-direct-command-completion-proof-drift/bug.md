---
bug_id: BUG-0060-direct-command-completion-proof-drift
title: Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段
status: done
created_at: '2026-10-21 11:21:34'
updated_at: 2026-10-21 14:09:29
severity: high
environment: local docker chat-platform
related_requirement: null
related_bug: BUG-0052-verified-result-execution-guard-not-released
owner: 产品团队
discovered_at: '2026-10-21 09:24:32'
related_change: null
root_cause_status: confirmed
---

# Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段

## 现象与影响

BUG-0055 的 bug-opsx 已创建 fix-chat-turn-message-order，Workflow Sync 成功且轮次 completed；产品卡片仍滞留迭代规划，提示结果待核对，开始修复禁用，刷新不恢复。文档投影应为 ready-dev，却被执行保护覆盖回 sprint-planning。

严重度 high：已生成成果不能进入下一动作，且对话成功提示与业务结果不一致，容易诱导重复执行。没有数据丢失证据。不把 BUG-0055 消息排序实现混入本缺陷；关联 BUG-0052-verified-result-execution-guard-not-released 的完成保护机制。

## 复现与期望

1. 在已纳入 Sprint 的 Issue 执行受支持的直接治理命令，完成成果生成和正式 Workflow Sync。
2. 同步后发生文档收尾或其他对象治理变化，再结束轮次；观察同步、终态和当前快照的指纹及执行保护。
3. 刷新卡片并核对业务阶段、核验原因和下一动作准入。

期望：动作相关交付有效时可安全签认和流转；相关冲突仍阻断并给出具体差异与恢复入口。运行结束与业务确认分开表达。实际本例整树摘要改变便使原同步证明失效，没有区分变化归属。

## 根因状态与确认范围

root_cause_status: confirmed，限于全局指纹耦合、证明留存不足以及保护不收敛的机制；本次新增结论承接 capture 中 probable 的历史文件归属判断，并未把逐文件归属升级为 confirmed。

- 同步成功证明绑定五个治理目录的完整内容摘要；任何被纳入文件的字节变化都可能失效，不限当前对象。
- 收尾及 reconcile 要求成功同步步骤摘要与终态/当前摘要匹配；本例不匹配，留下 sync_incomplete 与 needs_review。
- 卡片按旧 confirmed_stage 展示；reconcile_external 对仍有运行身份且 needs_review 的保护返回，不会仅凭当前文档结构正确自动清除。因此刷新重复相同判定。
- 工具边界只记录总摘要，没有同步成功时逐文件清单或结果快照，无法解释具体差异，也无法安全认定全部变化无关。
- 既有评审/归档专用证明不等于所有直接命令均有同等覆盖；修复须建立动作分类验证，不能统一无条件放行。

## 证据链

| ID | 类型 | 来源 | 脱敏事实与判断 |
|---|---|---|---|
| E1 | screenshot | 用户附件 2df3937f、fd432dc6 及上一轮浏览器只读观察 | Chat 已完成，BUG-0055 留在迭代规划，按钮禁用 |
| E2 | data_sample | 部署数据库只读查询摘要，capture.md | completed；guard needs_review；reason result_unverified；confirmed_stage sprint-planning |
| E3 | data_sample | direct-command journal 与工具事件关联 | 28 个边界，1 次正式同步成功；最终 sync_incomplete，无 candidate/application 替代证明 |
| E4 | code_path | src/backend/app/governance/snapshot.py：ROOTS、digest | 对 issues、iterations、openspec、docs、rules 中纳入的文件名及内容摘要计算整树指纹 |
| E5 | code_path | direct_command_journal.py：observe、terminal；execution_context.py：reconcile | 同步步骤和当前摘要相等才可继续确认；--check/--dry-run 不算正式同步成功 |
| E6 | code_path | reader.py：_call；execution_context.py：reconcile_external | 保护覆盖业务阶段，外部投影不能越过原执行保护 |
| E7 | data_sample | 原轮事件150、218—226 | 09:22:42 正式同步成功，后续摘要从 8316694e27a1 经 a03270b25664 变为 0726bc554bcd；无第二次正式同步证明 |
| E8 | data_sample | 事件225/226 的操作摘要 | 对 sprint-011/sprint.md 与 Change trace.md 执行 write_text，随后仅 --check；写回前后总摘要相同，不能将此操作认定为摘要变化原因 |
| E9 | data_sample | BUG-0057 trace 记录及子文档元数据 | 09:22:50 补齐文档，处于本轮同步后窗口；acceptance/root-cause/workaround 等文件创建时间与之相符，是无关对象并发线索 |
| E10 | data_sample | 原轮私有存储只读检查 | baseline 有4353项文件；result 不存在；同步步骤只有摘要，缺同步时逐文件结果 |
| E11 | reproduction | 同会话只读探索中的内存实验 | 原执行前基线中，仅给 BUG-0057 trace 增加换行，digest 就改变；未写文件或数据库，证明无关变化也影响全局摘要 |
| E12 | data_sample | 同会话当前快照只读校验 | validate_result 对 BUG-0055/bug-opsx 为 True；不叠加保护时 ready-dev。只证明当时结构有效，不替代完整安全恢复依据 |
| E13 | data_sample | 执行前基线与探索时当前快照比较 | 38个路径差异，包含后续 BUG-0060 创建、BUG-0046 评审及 BUG-0057 更新；不是同步到收尾的精确差异 |

E1 原始附件保留在对话，不复制聊天正文。E2—E13 为此前同会话已完成的只读/内存取证，本次复用；不声称本轮重跑产品或重新确认最新运行态。路径、角色、摘要和时间均为脱敏事实。

## 同步后变化的分类与剩余缺口

| 类别 | 具体路径/变化 | 证据强度与处理 |
|---|---|---|
| 当前命令文档收尾 | iterations/change/sprint-011/sprint.md；openspec/changes/fix-chat-turn-message-order/trace.md 的创建状态和验证说明写回 | 已确认操作；该边界摘要相同，可能为无效替换，不认定是失效来源 |
| 无关对象并发 | issues/bugs/plan/BUG-0057-requirement-card-chat-navigation-latency/ 下 acceptance.md、root-cause.md、workaround.md 创建及其他子文档更新 | 文档记录在时间窗口内；缺同步时快照，无法将具体文件逐一归因到某次摘要跳变 |
| 更晚变化 | BUG-0060 文档、BUG-0046 评审迁移等 | 已包含在执行前到当前差异中；不能解释原始收尾失效，不混入历史因果 |
| 真实交付冲突 | 本例未发现当前结构性冲突 | 当前结构有效不足以排除全部历史相关输入变化；禁止据此直接解除保护 |

总哈希不可逆，缺失的历史逐文件状态不能从当前文件还原。此前工具边界观察到摘要变化不证明该校验工具是写入者；并发任务同样可能造成变化。后续若有可用历史文件清单再补齐，不伪造完整差异。隔离回归可证明机制和修复行为，不能代替历史归因。

## 通用完成证明方案

1. 每类直接命令声明动作身份、对象、操作版本、输入依赖、预期输出与业务验证器。保存同步和最终签认的逐文件哈希清单及必要字段投影，供差异分类；最小化保存敏感内容。
2. 对共享注册表、Sprint 文档按当前对象条目/依赖验证，避免无关条目使证明失效；同时保留唯一性、引用完整性和容量等适用全局约束。不是简单忽略整个共享文件。
3. 分离交付输入、派生说明和无关内容。仅经过明确策略及业务校验的说明回填可重新签认；任务、规格、身份、状态、验收要求等实质变化仍按相关冲突处理。
4. 完成最后文档回填后统一执行最终核验与证明签认，持久交接到保护确认；签认与释放之间复读相关指纹并用版本围栏防竞态。崩溃后可从持久证明恢复，不重做业务写入。
5. --check 保持只读检查语义，退出0不等于已生成新的正式同步证明。模型声明、单个命令退出0、静态 ready 均不能单独放行。
6. 建立支持动作矩阵：req/bug generate、complete、review、opsx，sprint-propose，opsx apply/modify/archive；逐类保留自己的门禁和输出要求，复用已有可靠证明而非覆盖已有归档/评审保护。

## 错误提示与安全恢复方案

区分运行结束和业务确认。原因至少区分证明缺失/损坏、同步后相关变化、无关变化待重核、结构校验失败、权限或绑定变化、暂不可用和新执行占用；提供核验时间、脱敏差异类别和原执行入口，不继续只显示结果待核对。

恢复前验证原执行终态、操作与对象身份、权限/绑定、当前相关交付及同步一致性，确认没有更新运行占用；相关哈希复读稳定后按 operation/version 条件更新保护和投影。重复恢复幂等，延迟回调不能释放新保护。

历史证据不足时明确“需重建核验依据”，以受控流程重新验证当前成果并签发可追溯的新核验记录，保留旧记录，不伪造原同步结果。无法满足门禁则继续阻断并说明缺口。具体恢复实现须经后续 Change 与验收，不在本轮解除现场。

不重放 bug-opsx、不重复创建 Change、不手改数据库、不直接改卡片阶段、不绕过权限或冲突门禁。BUG-0055 现场是兼容恢复样本，不能成为硬编码特例。

## 回归与交付范围（待实施验证）

- 正常正式同步与最终签认；仅 --check/退出0 不误放行。
- 同步后说明回填、当前对象实质交付变化、无关对象并发、共享文件无关条目与影响全局约束的变化。
- 缺损证明、无历史逐文件证据、权限撤销、绑定变化、真实相关冲突：保留阻断且原因具体。
- 签认窗口并发写入、终态交接中断、进程重启、重复恢复、旧回调到达新执行：围栏及幂等有效。
- 支持动作分类参数化覆盖，产品实际发送→成果落地→同步→收尾→卡片流转→下一动作准入，与 CLI 一致。
- 历史 BUG-0055 只核验恢复，不重新执行原业务；合成回归、真实产品观察、历史恢复证据分别记录。外部模型调用按届时有效授权执行。

## 文档与治理边界

缺陷包已补齐，详见 [根因分析](root-cause.md)、[临时处理](workaround.md) 与 [验收标准](acceptance.md)。已批准修复，尚未进入 Sprint 或创建 Change，未修改代码或正式现场；修复验收尚未开始，条件见 [评审记录](review.md)。后续设计按实际影响同步 API/错误码、DB/证明版本兼容、UI 状态说明、部署恢复说明、客户端生成与测试。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Chat、治理快照、完成证明、执行保护、CLI、卡片投影及恢复；validation: E1—E13 的既有证据，回归尚未执行。仅保存仓库相对路径、必要摘要、分类、状态和操作关联，不落原始聊天、凭证或本机路径。N/A：本轮无业务实现、部署或权限变更。
